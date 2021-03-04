from __future__ import absolute_import, division, print_function
import argparse
import numpy as np
import cv2,os,glob
from tqdm import tqdm

parser = argparse.ArgumentParser(description='Synthesize Low-light Raw effect on FlyingChairs Dataset to create FCDN dataset.')

parser.add_argument('--input_FC_path', default='./FlyingChairs/FlyingChairs_release/data/', help='The path of FlyingChairs dataset')
parser.add_argument('--output_FCDN_path', default='./FCDN/FlyingChairs_release/data/', help='The path of output FCDN dataset')
parser.add_argument('--parameter_g', default=38.25, type=int, help='Gauss parameter, change it to fit your data')
parser.add_argument('--parameter_p', default=19.50, type=int, help='Poisson parameter, change it to fit your data')
parser.add_argument('--parameter_c', default=0.05, type=float, help='Color random adjustment parameter')

args = parser.parse_args()

def add_noise(img1, img2):
    g = args.parameter_g
    p = args.parameter_p/255.
    a,b = abs(np.random.normal(0,p)), abs(np.random.normal(0,g))
    sd1, sd2 = abs(a*img1+b), abs(a*img2+b)
    noisy_img1 = img1 + np.random.normal(0,sd1)
    noisy_img2 = img2 + np.random.normal(0,sd2)
    return np.clip(noisy_img1.astype(int),0,255), np.clip(noisy_img2.astype(int),0,255)

def wb_effect(img1, img2):
    red_gain = np.random.normal(1.0,args.parameter_c)
    green_gain = np.random.normal(1.0,args.parameter_c)
    blue_gain = np.random.normal(1.0,args.parameter_c)
    gains = np.array([[[1.0/(blue_gain), 1.0/(green_gain), 1.0/(red_gain)]]])
    out1 = np.multiply(img1,gains)
    out2 = np.multiply(img2,gains)
    return np.clip(out1.astype(int),0,255), np.clip(out2.astype(int),0,255)

input_dir = args.input_FC_path
output_dir = args.output_FCDN_path
if not os.path.exists(input_dir):
    print('Please download FlyingChairs dataset first.')
    exit()
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

img1_all_addrs = glob.glob('%s/*img1*'%input_dir)
img1_all_addrs.sort()
img2_all_addrs = glob.glob('%s/*img2*'%input_dir)
img2_all_addrs.sort()
assert(len(img1_all_addrs) == len(img2_all_addrs))

for i in tqdm(range(len(img1_all_addrs))):
    img1 = cv2.imread(img1_all_addrs[i])
    img2 = cv2.imread(img2_all_addrs[i])
    noisy_img1, noisy_img2 = add_noise(img1,img2)
    out_img1, out_img2 = wb_effect(noisy_img1,noisy_img2)
    cv2.imwrite('%s/%s'%(output_dir,os.path.basename(img1_all_addrs[i])),out_img1)
    cv2.imwrite('%s/%s'%(output_dir,os.path.basename(img2_all_addrs[i])),out_img2)

print('Finish synthesizing.')
print('Copying optical flow... might take a while.')
os.system('cp %s/*.flo %s/'%(input_dir,output_dir))
print('All finished.')
