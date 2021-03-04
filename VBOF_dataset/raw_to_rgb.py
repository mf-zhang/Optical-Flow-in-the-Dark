from __future__ import absolute_import, division, print_function
import argparse,glob,rawpy,tqdm,os,cv2
import numpy as np
import matplotlib.pyplot as plt


parser = argparse.ArgumentParser(description='Process RAW files in VBOF to RGB')

parser.add_argument('--input_raw_path', default='./VBOF_rawdata/', help='The path of RAW files folder')
parser.add_argument('--output_rgb_path', default='./raw2jpg_output/', help='The path of output RGB image folder')

args = parser.parse_args()

input_dir = args.input_raw_path
output_dir = args.output_rgb_path
if not os.path.exists(input_dir):
    print('Please download VBOF_raw dataset first.')
    exit()
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def raw_info(addr):
    """
    input a string of raw address\n
    print raw_pattern, black_level, shot_wb, shape, min, mean, max
    """
    print(addr)
    raw = rawpy.imread(addr)
    im = raw.raw_image_visible.astype(np.float32)
    print('raw pattern:')
    print(raw.color_desc)
    print(raw.raw_pattern)
    print('black level: ', raw.black_level_per_channel)
    print('shot white balance: ', raw.camera_whitebalance)
    print('shape: ', im.shape)
    print('min: %f, mean: %f, max: %f' % (np.min(im),np.mean(im),np.max(im)))

def raw_read(addr, rmin=2047, rmax=16383, orig=False):
    """
    input a string of raw address\n
    consult `raw_info()` before you decide the min and max\n
    min should be slightly bigger than np.min(all_im). In most cases the black level works\n
    max should be slightly bigger than np.max(all_im). In mosr cases 16383 works\n
    try differnet values until the contrast seems fine\n
    if orig then return the original im array [0,2^n]\n
    else return (im2d-min)/max [0,1]
    """
    raw = rawpy.imread(addr)
    im = raw.raw_image_visible.astype(np.float32)
    if orig: return im

    im = im - rmin
    im = im / (rmax-rmin)

    im = np.maximum(im,0.)
    im = np.minimum(im,1.)
    return im

def pack_bayer(bayer_2d):
    """
    input an 2d image (H,W) from a bayer raw\n
    return a 4d image (H/2,W/2,4)\n
    a b\n
    c d\n
    im[x,x,0]-a, im[x,x,1]-b, im[x,x,2]-d, im[x,x,3]-c\n
    
    normally,\n
    im[x,x,0]-R, im[x,x,1]-G, im[x,x,2]-B, im[x,x,3]-G
    """
    import numpy as np
    im = bayer_2d
    im = np.expand_dims(im, axis=2)
    
    out = np.concatenate((im[0::2, 0::2, :], # a
                          im[0::2, 1::2, :], # b
                          im[1::2, 1::2, :], # d
                          im[1::2, 0::2, :]  # c
                          ), axis=2)
    return out

def pack_XTrans(bayer_2d):
    """
    input a 2d xtrans raw image, pattern like this:\n
    [0, 2, 1, 2, 0, 1],\n
    [1, 1, 0, 1, 1, 2],\n
    [1, 1, 2, 1, 1, 0],\n
    [2, 0, 1, 0, 2, 1],\n
    [1, 1, 2, 1, 1, 0],\n
    [1, 1, 0, 1, 1, 2]\n
    return a 9d image\n
    R-0,4d G-1,5,6,7,8d B-1,5d\n
    This is slightly different from the camerea used in Learning to See in the Dark\n
    """
    import numpy as np
    im = bayer_2d

    img_shape = im.shape
    H = (img_shape[0] // 6) * 6
    W = (img_shape[1] // 6) * 6

    out = np.zeros((H // 3, W // 3, 9))

    # 0 R
    out[0::2, 0::2, 0] = im[5:H:6, 0:W:6]
    out[0::2, 1::2, 0] = im[5:H:6, 4:W:6]
    out[1::2, 0::2, 0] = im[2:H:6, 1:W:6]
    out[1::2, 1::2, 0] = im[2:H:6, 3:W:6]

    # 1 G
    out[0::2, 0::2, 1] = im[5:H:6, 2:W:6]
    out[0::2, 1::2, 1] = im[5:H:6, 5:W:6]
    out[1::2, 0::2, 1] = im[2:H:6, 2:W:6]
    out[1::2, 1::2, 1] = im[2:H:6, 5:W:6]

    # 1 B
    out[0::2, 0::2, 2] = im[5:H:6, 1:W:6]
    out[0::2, 1::2, 2] = im[5:H:6, 3:W:6]
    out[1::2, 0::2, 2] = im[2:H:6, 0:W:6]
    out[1::2, 1::2, 2] = im[2:H:6, 4:W:6]

    # 4 R
    out[0::2, 0::2, 3] = im[0:H:6, 2:W:6]
    out[0::2, 1::2, 3] = im[1:H:6, 5:W:6]
    out[1::2, 0::2, 3] = im[4:H:6, 2:W:6]
    out[1::2, 1::2, 3] = im[3:H:6, 5:W:6]

    # 5 B
    out[0::2, 0::2, 4] = im[1:H:6, 2:W:6]
    out[0::2, 1::2, 4] = im[0:H:6, 5:W:6]
    out[1::2, 0::2, 4] = im[3:H:6, 2:W:6]
    out[1::2, 1::2, 4] = im[4:H:6, 5:W:6]

    out[:, :, 5] = im[0:H:3, 0:W:3]
    out[:, :, 6] = im[0:H:3, 1:W:3]
    out[:, :, 7] = im[1:H:3, 0:W:3]
    out[:, :, 8] = im[1:H:3, 1:W:3]
    return out

def imcrop(im,to_h,to_w,skip_n=1):
    assert(im.shape[0]>=to_h)
    assert(im.shape[1]>=to_w)
    
    marg_h = im.shape[0] - to_h
    marg_w = im.shape[1] - to_w
    h1=h2=w1=w2=0
    h1 = marg_h/2 if marg_h%2==0 else marg_h/2-0.5
    h2 = marg_h/2 if marg_h%2==0 else marg_h/2+0.5
    w1 = marg_w/2 if marg_w%2==0 else marg_w/2-0.5
    w2 = marg_w/2 if marg_w%2==0 else marg_w/2+0.5
    h1,h2,w1,w2 = int(h1),int(h2),int(w1),int(w2)
    newim = im[h1:-h2:skip_n,w1:-w2:skip_n,:]
    
    return newim

def nd_to_3d(ndarray, Rlist, Glist, Blist, G_plus=0):
    """
    input an nd image, Rchannels, Gchannels, Bchannels\n
    G_plus up, green color down
    return a 3d image
    """
    import numpy as np
    out = np.zeros([ndarray.shape[0],ndarray.shape[1],3])

    for r in Rlist: out[:,:,0] += ndarray[:,:,r]
    out[:,:,0] /= len(Rlist)
    for g in Glist: out[:,:,1] += ndarray[:,:,g]
    out[:,:,1] /= (len(Glist)+G_plus)
    for b in Blist: out[:,:,2] += ndarray[:,:,b]
    out[:,:,2] /= len(Blist)

    return out

def adjust_br(im, to_mean):
    assert(np.max(im)<=1)
    ratio = to_mean/np.mean(im)
    im = im*ratio
    im = np.maximum(im,0.)
    im = np.minimum(im,1.)
    return im


# SONY
raws_path = glob.glob('%s/1*.ARW'%input_dir)
for raw_addr in tqdm.tqdm(raws_path):
    # raw_info(raw_addr)
    # break
    im2d = raw_read(raw_addr,512,16383)
    im4d = pack_bayer(im2d)
    im4d = imcrop(im4d,4000/2,6000/2) # crop the size of camera-produce raw to camera-produce jpg
    im = nd_to_3d(im4d,[0],[1,3],[2],2)
    im = adjust_br(im,0.4)
    im = cv2.resize(im,(736,480))
    plt.imsave('%s/%s.png'%(output_dir,os.path.basename(raw_addr)[:-4]),im)

# CANON
raws_path = glob.glob('%s/2*.CR2'%input_dir)
for raw_addr in tqdm.tqdm(raws_path):
    # raw_info(raw_addr)
    # break
    im2d = raw_read(raw_addr,2047,16383)
    im4d = pack_bayer(im2d)
    im4d = imcrop(im4d,4000/2,6000/2) # crop the size of camera-produce raw to camera-produce jpg
    im = nd_to_3d(im4d,[0],[1,3],[2],0.2)
    im = adjust_br(im,0.4)
    im = cv2.resize(im,(736,480))
    plt.imsave('%s/%s.png'%(output_dir,os.path.basename(raw_addr)[:-4]),im)

# FUJIFILM
raws_path = glob.glob('%s/3*.RAF'%input_dir)
for raw_addr in tqdm.tqdm(raws_path):
    # raw_info(raw_addr)
    # break
    im2d = raw_read(raw_addr,1022,16383)
    im9d = pack_XTrans(im2d)
    im9d = imcrop(im9d,1333,6000/3) # crop the size of camera-produce raw to camera-produce jpg
    im = nd_to_3d(im9d,[0,3],[1,5,6,7,8],[2,4],2)
    im = adjust_br(im,0.4)
    im = cv2.resize(im,(736,480))
    plt.imsave('%s/%s.png'%(output_dir,os.path.basename(raw_addr)[:-4]),im)

# NIKON
raws_path = glob.glob('%s/4*.NEF'%input_dir)
for raw_addr in tqdm.tqdm(raws_path):
    # raw_info(raw_addr)
    # break
    im2d = raw_read(raw_addr,100,16383)
    im4d = pack_bayer(im2d)
    im4d = imcrop(im4d,5504/2,8256/2) # crop the size of camera-produce raw to camera-produce jpg
    im = nd_to_3d(im4d,[0],[1,3],[2],1)
    im = adjust_br(im,0.4)
    im = cv2.resize(im,(736,480))
    plt.imsave('%s/%s.png'%(output_dir,os.path.basename(raw_addr)[:-4]),im)
