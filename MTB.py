import cv2 as cv
import glob
import os
import numpy as np


def bitmap(img):
    img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    med = np.median(img)
    eb = np.array(img)
    eb[np.where((img <= med + 4) & (img >= med - 4))] = 0
    eb[np.where((img <= med - 4) | (img >= med + 4))] = 1
    mtb = np.array(img)
    mtb[np.where(img<med)] = 0
    mtb[np.where(img>=med)] = 1
    return mtb, eb

def shrink(img):
    img = np.delete(img, np.s_[::2], 0)
    img = np.delete(img, np.s_[::2], 1)
    return img

def align(img1,img2,scale,shift_x,shift_y):
    if scale > 0:
        img1 = shrink(img1)
        img2 = shrink(img2)
        shift_x,shift_y = align(img1,img2,scale-1,shift_x,shift_y)
        shift_x *= 2
        shift_y *= 2
    else:
        shift_x = 0
        shift_y = 0
    mtb1, eb1 = bitmap(img1)
    mtb2, eb2 = bitmap(img2)
    min_error = img1.shape[0]*img1.shape[1]
    for i in range(-1,2):
        for j in range(-1,2):
            x = shift_x + i
            y = shift_y + j 
            t = np.float32([[1, 0, x],[0, 1, y]])
            shift_mtb2 = cv.warpAffine(mtb2, t, (mtb2.shape[1],mtb2.shape[0]))
            shift_eb2 = cv.warpAffine(eb2, t, (eb2.shape[1],eb2.shape[0]))
            diff = np.bitwise_xor(mtb1,shift_mtb2)
            diff = np.bitwise_and(diff,eb1)
            diff = np.bitwise_and(diff,shift_eb2)
            error = np.count_nonzero(diff)
            if error < min_error:
                shift_fx = x
                shift_fy = y
                min_error = error
    return shift_fx, shift_fy

def mtb(img_list):
    x = 0
    y = 0
    new_img_list = []
    old_img_list = []
    mv_x = []
    mv_y = []
    for i in range(len(img_list)-1):
        # img1 = cv.imread(img_list[i])
        # img2 = cv.imread(img_list[i+1])
        img1 = img_list[i]
        img2 = img_list[i+1]
        shift_fx, shift_fy = align(img1,img2,scale=5,shift_x=0,shift_y=0)
        x += shift_fx
        y += shift_fy
        # print(x)
        # print(y)
        mv_x.append(x)
        mv_y.append(y)
        t = np.float32([[1, 0, x],[0, 1, y]])
        shift_img2 = cv.warpAffine(img2, t, (img2.shape[1],img2.shape[0]))
        if i == 0:
            new_img_list.append(img1)
            old_img_list.append(img1)
        new_img_list.append(shift_img2)
        old_img_list.append(img2)
    
    max_x = [abs(x) for x in mv_x]
    max_y = [abs(y) for y in mv_y]
    # if max(max_x) < max(max_y):
    #     crop_x = max(max_x)
    #     crop_y = int(max(max_x) * img1.shape[0]/img1.shape[1])
    # else:
    #     crop_x = int(max(max_y) * img1.shape[1]/img1.shape[0])
    #     crop_y = max(max_y)
    crop_x = max(max_x)
    crop_y = max(max_y)
    # print(crop_x)
    # print(crop_y)

    new_img_list = [img[crop_x:-crop_x,crop_y:-crop_y] for img in new_img_list]
        

    # for i in range(len(new_img_list)):
    #     cv.imwrite(f'new/{i}.JPG', new_img_list[i])
    #     cv.imwrite(f'old/{i}.JPG', old_img_list[i])

    return new_img_list


if __name__ == '__main__':
    img_list = sorted(list(glob.glob(os.path.join('data/image','*.JPG'))))
    img_list = [cv.imread(img) for img in img_list]
    print(len(img_list))
    new_img_list = mtb(img_list)