import cv2
import numpy as np
import os


def compute_lm(lw,a, sigma):
    lw_bar = np.exp(np.average(np.log(sigma+lw)))
    lm = a*(lw)/lw_bar
    return lm

def globalTonemap(hdr_image, a=0.7, l_white=1.7):
    ## l_white: 設定超過即過曝的數值
    sigma=0.0000001
    lw = hdr_image
    lm = compute_lm(lw, a, sigma)

    numerator = lm * (1 + lm/(l_white)**2) 
    denominator = 1 + lm
    ld = numerator / denominator

    # ld = gamma_correction(ld, gamma=1.2)
    ldr = (ld * 255).astype(int)
        
    return ldr

def gamma_correction(id, gamma):
    return cv2.pow(id, 1.0/gamma)



def tonemap(args,hdr_img):
    print("Run Tonemapping")
    prefix = f'./result_{args.hdr_method}_{args.data_name}/'
    os.makedirs(prefix,exist_ok=True)

    # Gamma tone mapping
    if args.tonemap_global:
        # Gamma = np.uint8(globalTonemap(hdr_img, args.gamma))
        Global = np.uint8(globalTonemap(hdr_img, args.a, args.l_white))
        cv2.imwrite(f'{prefix}/{args.data_name}_global_tomemapping.jpg', Global)

    # Mantiuk tone mapping
    if args.tonemap_Mantiuk:
        tonemapMantiuk = cv2.createTonemapMantiuk(2.2, 0.85, 1.2)
        ldrMantiuk = tonemapMantiuk.process(np.float32(hdr_img))
        # ldrMantiuk = 0.5 * ldrMantiuk
        cv2.imwrite(f'{prefix}/{args.data_name}_Mantiuk_tomemapping.jpg', ldrMantiuk * 255)

    # Reinhard tone mapping
    if args.tonemap_Reinhard:
        tonemapReinhard = cv2.createTonemapReinhard(1.5, 0, 0, 0)
        ldrReinhard = tonemapReinhard.process(np.float32(hdr_img))
        # ldrReinhard = 0.5 * ldrReinhard
        cv2.imwrite(f'{prefix}/{args.data_name}_Reinhard_tomemapping.jpg', ldrReinhard * 255)
    
    # Drago tone mapping
    if args.tonemap_Drago:
        tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
        ldrDrago = tonemapDrago.process(np.float32(hdr_img))
        # ldrDrago = 0.7 * ldrDrago
        cv2.imwrite(f'{prefix}/{args.data_name}_Drago_tomemapping.jpg', ldrDrago * 255)
