import argparse
import cv2
import os
import glob
import numpy as np
import math
from tqdm import trange 
from matplotlib.pylab import cm
import matplotlib.pylab as plt
import random
from MTB import mtb
import Debevec
import Robertson
from tonemap import tonemap

def load_data(data_name):
    root = os.getcwd()
    img_path = os.path.join(root, 'data', data_name,"*.JPG")
    filenames = sorted(glob.glob(img_path))
    images = [cv2.imread(fn) for fn in filenames]
    
    if data_name=="exposures_1":
        exposure_times = np.array([13.0, 10.0, 4.0, 3.2, 1.0, 0.8, 0.3, 1/4.0, 1/60.0, 1/80.0], dtype=np.float32)
    else:
        exposure_times = 1/np.array([4.0, 8.0, 15.0, 30.0, 60.0, 125.0, 250.0, 500.0, 1000.0, 2000.0], dtype=np.float32)

    ln_exposure_times = np.log(exposure_times)
    return images, ln_exposure_times

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'High Dynamic Range Imaging')
    parser.add_argument('-data','--data_name', default = 'grass', choices=['corridor','grass'])
    parser.add_argument('-hdr','--hdr_method', default = 'Debevec', choices=['Debevec','Robertson'])
    parser.add_argument('-g','--tonemap_global', default = True)
    parser.add_argument('-m','--tonemap_Mantiuk', default = True)
    parser.add_argument('-r','--tonemap_Reinhard', default = True)
    parser.add_argument('-d','--tonemap_Drago', default = True)
    ## Tonemap global
    parser.add_argument('-a', default = 0.9, type=float)
    parser.add_argument('-l_white', default = 1.7, type=float)

    args = parser.parse_args()

    images, ln_exposure_times = load_data(args.data_name)
    assert(len(images)==len(ln_exposure_times))

    images = mtb(images)

    if args.hdr_method == 'Debevec':
        print("Run Debevec")
        hdr = Debevec.run_Debevec(images, ln_exposure_times, args.data_name, args.hdr_method)

    if args.hdr_method == 'Robertson':
        print("Run Robertson")
        hdr = Robertson.run_Robertson(images, ln_exposure_times, args.data_name, args.hdr_method)
    
    tonemap(args, hdr)



   
