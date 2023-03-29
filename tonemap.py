import cv2
import numpy as np
import os

def globalTonemap(img, l):
    return cv2.pow(img/255., 1.0/l)

def tonemap(args,hdr_img):
    print("Run Tonemapping")
    prefix = f'./result_{args.hdr_method}_{args.data_name}/'
    os.makedirs(prefix,exist_ok=True)

    # Gamma tone mapping
    if args.tonemap_global:
        Gamma = np.uint8(globalTonemap(hdr_img, args.gamma) * 255.)
        cv2.imwrite(f'{prefix}/{args.data_name}_gamma_tomemapping.jpg', Gamma)

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
