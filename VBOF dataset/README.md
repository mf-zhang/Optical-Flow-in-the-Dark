# Various Brightness Optical Flow (VBOF) Dataset

## Prepare the VBOF dataset

1. Download our VBOF dataset (1.23G) [here](https://drive.google.com/drive/folders/1LZR-kKs7kbLdh0QQYp4JmzEviZKhSWkb?usp=sharing).

2. Move `fill_VBOF_data.py` in this repository into the downloaded folder `VBOF_publish`.

3. Run `$ python fill_VBOF_data.py` to fill the `VBOF_publish/VBOF_data` folder with the files in the `VBOF_publish/src` folder.

4. Delete the `VBOF_publish/src` folder and `fill_VBOF_data.py`.

## Explain the VBOF dataset

### Steps to create the VBOF dataset

1. **Collect images**: 
Collect object movement in multiple exposures. (See Figure 2 in our [paper]( https://openaccess.thecvf.com/content_CVPR_2020/papers/Zheng_Optical_Flow_in_the_Dark_CVPR_2020_paper.pdf) for details)

2. **Scale the brightness**: 
Normalize the multiple-exposure 14-bit raw images to `[0,1]`, and scale the brightness intensity of each image to a mean value of `0.4`.

3. **Save image**: 
Demosiac the raw image, decreases the resolution, and save the images in 8-bit RGB format. (We publish this well-processed low-resolution version of our dataset in `VBOF_publish/src`.)

4. **Create image pairs**: 
Pair the images into couples and match optical flow references to each image pairs. (This is what `fill_VBOF_data.py` do.  The final dataset will be saved in ` VBOF_publish/VBOF_data`.)

### File name explaination in `VBOF_data`

xxxx