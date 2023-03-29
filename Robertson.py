import cv2 as cv
import glob
import os
import numpy as np
from tqdm import tqdm 
import matplotlib.pyplot as plt

def weight(z):
    if z <= (0+255)/2:
        w = z - 0 
    else:
        w = 255 - 0
    return w

def solve_response_curve(img_list, t, k=5):
    Z = []
    for img in img_list:
        Z.append(img.flatten()) 
    Z = np.array(Z)     #(frame,pixel)
    g = [i/256 for i in range(256)]   #initial g
    E = np.zeros((Z.shape[1]), dtype=np.float32)
    while k>0:
        for i in tqdm(range(Z.shape[1])):
            a = 0
            b = 0
            for j in range(Z.shape[0]):
                z = Z[j][i]
                a += weight(z)*g[z]*t[j]
                b += weight(z)*t[j]*t[j]
            E[i] = a/b
        for m in range(256):
            c = 0
            frame, pixel = np.where(Z == m)
            # print('frame',frame)
            # print('pixel',pixel)
            for i in range(len(frame)):
                c += E[pixel[i]]*t[frame[i]]
            g[m] = c/len(frame)
        k -= 1 
    return g, E


def compute_radiance(img_list,g,t):
    Z = []
    for img in img_list:
        Z.append(img.flatten()) 
    Z = np.array(Z)   
    lnE = np.zeros((Z.shape[1]), dtype=np.float32)
    for i in tqdm(range(Z.shape[1])):
        a = 0 
        b = 0
        for j in range(Z.shape[0]):
             z = Z[j][i]
             a += weight(z)*(g[z]-np.log(t[j]))
             b += weight(z)
        lnE[i] = a/b
    
    E = np.exp(lnE)
    hdr = np.reshape(E,(img_list[0].shape[0],img_list[0].shape[1]))
    return hdr

def run_Robertson(img_list, ln_exposure_times, data_name, hdr_method):
    prefix = f'./result_{hdr_method}_{data_name}/'
    os.makedirs(prefix,exist_ok=True)

    t = np.exp(ln_exposure_times)
    b_list = [img[:,:,0] for img in img_list]
    g_list = [img[:,:,1] for img in img_list]
    r_list = [img[:,:,2] for img in img_list]

    g_b, E_b = solve_response_curve(b_list,t)
    g_g, E_g = solve_response_curve(g_list,t)
    g_r, E_r = solve_response_curve(r_list,t)

    hdr_b = compute_radiance(b_list,g_b,t)
    hdr_g = compute_radiance(g_list,g_g,t)
    hdr_r = compute_radiance(r_list,g_r,t)

    hdr = np.stack((hdr_b,hdr_g,hdr_r),axis=2)

    cv.imwrite(f'{prefix}/{data_name}.hdr', hdr)

    #show cmap
    plt.imshow(np.log(cv.cvtColor(np.float32(hdr), cv.COLOR_BGR2GRAY)), cmap='jet')
    plt.colorbar()
    plt.savefig(f'{prefix}/{data_name}_cmap''.jpg')
    
    #show curve
    plt.clf()
    plt.plot(np.log(g_b), range(256), 'b')
    plt.plot(np.log(g_g), range(256), 'g')
    plt.plot(np.log(g_r), range(256), 'r')
    plt.xlabel('log exposure X')
    plt.ylabel('pixel value Z')
    plt.savefig(f'{prefix}/{data_name}_resonse_curve.jpg')
    
    return hdr

if __name__ == '__main__':
    pass