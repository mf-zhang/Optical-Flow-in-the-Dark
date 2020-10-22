# This program fill the 'VBOF_data' folder (which is empty at first) with the files in the 'src' folder.

from tqdm import tqdm
import glob, os

print('\n8 bars in total. To stop, press ctrl+c for 10 secends :)')

def create_a_pair(im1addr,im2addr,n1,n2,br,floaddr,data_addr,camera_str):
    os.system('cp %s %s'%(im1addr,data_addr))
    os.system('cp %s %s'%(im2addr,data_addr))
    os.system('cp %s %s'%(floaddr,data_addr))

    # target name
    a=b=c=d=e=0
    if camera_str in ['sony','sony2','sony3']: a = 1
    if camera_str in ['canon']:                a = 2 
    if camera_str in ['fuji','fuji2']:         a = 3
    if camera_str in ['nikon','nikon2']:       a = 4
    if camera_str in ['sony','canon','fuji','nikon']: b = 1
    if camera_str in ['sony2','fuji2','nikon2']:      b = 2
    if camera_str in ['sony3']:                       b = 3
    if True: c = n1
    if True: d = n2
    if True: e = br
    target_name = '%d%d%02d%02d%02d'%(a,b,c,d,e)
    
    # rename
    os.system('mv %s/%s %s/%s_img1.jpg'%(data_addr,os.path.basename(im1addr), data_addr, target_name))
    os.system('mv %s/%s %s/%s_img2.jpg'%(data_addr,os.path.basename(im2addr), data_addr, target_name))
    os.system('mv %s/%s %s/%s_flow.flo'%(data_addr,os.path.basename(floaddr), data_addr, target_name))

def get_gt_list(addr):
    gts = glob.glob(addr)
    list1 = []
    list2 = []
    for gt in gts:
        gt = os.path.basename(gt)
        gt = gt[:-4]
        gt_split = gt.split('-')
        list1.append(int(gt_split[0]))
        list2.append(int(gt_split[1]))
    return list1, list2

canon_im1, canon_im2 = get_gt_list('./src/canon/GT/*.flo') # 25*2
sony_im1, sony_im2 = get_gt_list('./src/sony/GT/*.flo') # 8*2
sony2_im1, sony2_im2 = get_gt_list('./src/sony2/GT/*.flo') # 14*2
sony3_im1, sony3_im2 = get_gt_list('./src/sony3/GT/*.flo') # 30*2
fuji_im1, fuji_im2 = get_gt_list('./src/fuji/GT/*.flo') # 17*2
fuji2_im1, fuji2_im2 = get_gt_list('./src/fuji2/GT/*.flo') # 69*2
nikon_im1, nikon_im2 = get_gt_list('./src/nikon/GT/*.flo') # 25*2
nikon2_im1, nikon2_im2 = get_gt_list('./src/nikon2/GT/*.flo') # 25*2

cameras = ['canon','sony','sony2','sony3','fuji','fuji2','nikon','nikon2']
data_addr = './VBOF_data/'

for camera_str in cameras:
    camera_im1 = eval('%s_im1'%camera_str)
    camera_im2 = eval('%s_im2'%camera_str)

    for i in tqdm(range(len(camera_im1))):
        n1 = camera_im1[i]
        n2 = camera_im2[i]
        images_this_scene = glob.glob('./src/%s/%d_*.jpg'%(camera_str,n1))
        image_num_this_scene = len(images_this_scene)

        for j in range(1,image_num_this_scene+1):
            ima = './src/%s/%d_%d.jpg'%(camera_str,n1,j)
            imb = './src/%s/%d_%d.jpg'%(camera_str,n2,j)
            flo = './src/%s/GT/%d-%d.flo'%(camera_str,n1,n2)
            create_a_pair(im1addr=ima,im2addr=imb,n1=n1,n2=n2,br=j,floaddr=flo,data_addr=data_addr,camera_str=camera_str)
