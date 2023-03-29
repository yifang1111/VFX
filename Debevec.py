import cv2
import os
import glob
import numpy as np
import math
from tqdm import trange 
from matplotlib.pylab import cm
import matplotlib.pylab as plt
import random

def init_weight_function():
    Zmin = 0 
    Zmax = 255 
    Zmid = (Zmax+Zmin+1)//2
    w = np.zeros((Zmax-Zmin+1))

    for z in range(Zmin,Zmax+1): 
        if z <= Zmid:
            w[z] = z - Zmin
        else: 
            w[z] = Zmax - z
    return w

#random sample from 
def sampling(images, n_channels=3):
    Z_min, Z_max = 0, 256

    num_images = len(images)

    num_sample = Z_max - Z_min
    sample = np.zeros((num_sample, num_images, n_channels), dtype=float)
   
    sample_img = images[2]
    idx_list = []
    # sample for all Z_min
    for c in range(n_channels):
        for i in range(Z_min, Z_max):
            # print(sample_img[:,:,c])
            (rows, cols)  = np.where(sample_img[:,:,c] == i)
            if len(rows) == 0 and len(cols) == 0:
                continue
            idx = random.randrange(len(rows))
            # sample among all images
            for j in range(num_images):
                sample[i, j, c] = images[j][rows[idx], cols[idx]][c]
    # print(sample.shape)
    return sample


# solve_response_curve
def solve_response_curve(sample_c, ln_exposure_times, l=100):
    # (num_sample, num_images)
    Zmin = 0 
    Zmax = 255 
    Z_range = Zmax-Zmin+1 # 256
    # A: (NP+255) by (256+N)
    A = np.zeros((sample_c.shape[0]*sample_c.shape[1]+Z_range, Z_range+1+sample_c.shape[0]), dtype=np.float64)
    # b: (NP+255) by (1)
    b = np.zeros((A.shape[0], 1), dtype=np.float64)
    # weight function w(z)
    w = init_weight_function()
    
    k = 0
    # NP equations
    for i in range(sample_c.shape[0]):
        for j in range(sample_c.shape[1]):
            I_ij = int( sample_c[i,j] )
            w_ij = w[int(I_ij)]
            A[k, I_ij] = w_ij
            A[k, Z_range + i] = -w_ij
            b[k, 0] = w_ij * ln_exposure_times[j]
            k += 1
    # Color normalize equation: g(127)=1
    A[k, int((Zmax - Zmin) // 2)] = 1
    k += 1 
    # 254 equations
    for I_k in range(Zmin+1, Zmax):
        w_k = w[I_k]
        A[k, I_k-1] = w_k * l
        A[k, I_k] = -2 * w_k * l
        A[k, I_k+1] = w_k * l
        k += 1    

    # Solve
    inv_A = np.linalg.pinv(A)
    x = np.dot(inv_A, b)

    # Finally, g is obtained.
    g = x[0:Z_range]
    lE = x[Z_range:]

    return g[:,0]

# compute_radiance
def compute_radiance(images, ln_exposure_times, g):
    n_channels = g.shape[-1]
    num_images = len(images)
    width, height = images[0].shape[0], images[0].shape[1]
    img_rad = np.zeros((width, height, n_channels), dtype=np.float64)
    
    # weight function w(z)
    w = init_weight_function()  
    for c in range(n_channels):
        g_channel = g[:, c]

        for i in trange(width):
            for j in range(height):

                g_value = np.array([g_channel[ int(images[k][i, j, c]) ] for k in range(num_images) ])
                w_value = np.array([w[ int(images[k][i, j, c]) ] for k in range(num_images) ])
                
                sumW = np.sum(w_value)
                if sumW > 0:
                    img_rad[i,j,c] = np.sum(w_value * (g_value - ln_exposure_times) / sumW)
                else:
                    img_rad[i,j,c] = g_value[num_images // 2] - ln_exposure_times[num_images //2]

    return img_rad

def run_Debevec(images, ln_exposure_times, data_name, hdr_method):
    prefix = f'./result_{hdr_method}_{data_name}/'
    os.makedirs(prefix,exist_ok=True)

    n_channels = images[0].shape[-1]
    hdr_img = np.zeros(images[0].shape, dtype=np.float64)
    
    # Sample some indices from image.
    sample = sampling(images, n_channels)
    
    # For each individual channel:
    Zmin = 0 
    Zmax = 255 
    Z_range = Zmax-Zmin+1 # 256
    g = np.zeros((Z_range, n_channels), dtype=np.float64)

    for c in range(n_channels):
        # Solve ODE.
        g[:, c]= solve_response_curve(sample[:,:,c], ln_exposure_times, l=100)

    img_rad = compute_radiance(images, ln_exposure_times, g)
    hdr_img = cv2.normalize(img_rad, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    cv2.imwrite(f'{prefix}/{data_name}.hdr', hdr_img)

    # Save cmap
    colorize = cm.jet
    cmap = np.float32(cv2.cvtColor(np.uint8(hdr_img), cv2.COLOR_BGR2GRAY)/255.)
    cmap = colorize(cmap)
    plt.figure()
    plt.imshow(np.uint8(cmap*255.), cmap='jet')
    plt.colorbar()
    plt.savefig(f'{prefix}/{data_name}_cmap''.jpg')

    # Show curve
    plt.figure()
    x = np.arange(0, Z_range, 1)
    color = ['r', 'g', 'b']
    for c in range(n_channels):
        plt.plot(g[:, c], x, color=color[c])
    plt.xlabel('log exposure X')
    plt.ylabel('pixel value Z')
    plt.savefig(f'{prefix}/{data_name}_resonse_curve.jpg') 

    return hdr_img
        
if __name__ == "__main__":
    pass
