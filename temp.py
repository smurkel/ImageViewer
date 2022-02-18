import numpy as np
import matplotlib.pyplot as plt
from Util import *
from pystackreg import StackReg
from skimage import transform as tf
import cv2

a = Load("C:/Users/mgflast/Desktop/stitch test/xidx_1_yidx_0.tif")
b = Load("C:/Users/mgflast/Desktop/stitch test/xidx_2_yidx_0.tif")




def register_pair(ref, img, overlap, direction="east"):
    width, height = np.shape(ref)
    overlap_width = min([int(width * overlap), width])
    overlap_height = min([int(height * overlap), height])
    roi_ref = None
    roi_img = None
    translation = np.asarray([0.0, 0.0])
    if direction == "north":
        roi_ref = ref[:overlap_height, :]
        roi_img = img[-overlap_height:, :]
        translation += np.asarray([0.0, (1.0 - overlap) * height])
    elif direction == "east":
        roi_ref = ref[:, -overlap_width:]
        roi_img = img[:, :overlap_width]
        translation += np.asarray([-(1.0 - overlap) * width, 0.0])
    elif direction == "south":
        roi_ref = ref[-overlap_height:, :]
        roi_img = img[:overlap_height, :]
        translation += np.asarray([0.0, -(1.0 - overlap) * height])
    elif direction == "west":
        roi_ref = ref[:, :overlap_width]
        roi_img = img[:, -overlap_width:]
        translation += np.asarray([(1.0 - overlap) * width, 0.0])
    def register_rois(refroi, imgroi):
        orb = cv2.ORB_create(nfeatures=100)
        kp_ref = orb.detect(refroi, None)
        kp_img = orb.detect(imgroi, None)
        kp_ref, des_ref = orb.compute(refroi, kp_ref)
        kp_img, des_img = orb.compute(imgroi, kp_img)
        print(len(kp_ref))
        bfm = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck = True)
        matches = bfm.match(des_ref, des_img)
        matches = sorted(matches, key=lambda x: x.distance)
        NUM_MATCHES_TO_USE = min([100, len(matches)])
        print(len(matches))
        keypoints_ref = np.float32([kp_ref[m.queryIdx].pt for m in matches[:NUM_MATCHES_TO_USE]]).reshape(-1, 1, 2)
        keypoints_img = np.float32([kp_img[m.trainIdx].pt for m in matches[:NUM_MATCHES_TO_USE]]).reshape(-1, 1, 2)
        atm,_ = cv2.estimateAffinePartial2D(keypoints_ref, keypoints_img)
        print(atm)
        return atm

    roi_ref = roi_ref.astype(np.uint8)
    roi_img = roi_img.astype(np.uint8)
    transform = register_rois(roi_ref, roi_img)
    translation += np.asarray([transform[0][2], transform[1][2]])
    # plt.subplot(3,2,1)
    # plt.imshow(ref)
    plt.subplot(1,4,1)
    plt.imshow(roi_ref)
    # plt.subplot(3,2,3)
    # plt.imshow(img)
    plt.subplot(1,4,2)
    plt.imshow(roi_img)
    plt.subplot(1,4,3)
    comp_roi = np.zeros((np.shape(roi_ref)[0], np.shape(roi_ref)[1], 3))
    roi_reg = apply_translation(roi_img, [transform[0][2], transform[1][2]])
    comp_roi[:, :, 0] = roi_ref / np.amax(roi_ref)
    comp_roi[:, :, 1] = roi_reg / np.amax(roi_reg)

    plt.imshow(comp_roi)
    plt.subplot(1,4,4)
    comp = np.zeros((width, height, 3))
    comp[:, :, 0] = ref
    comp[:, :, 1] = apply_translation(img, translation)
    comp[:, :, 0] = comp[:, :, 0] / np.max(comp[:, :, 0])
    comp[:, :, 1] = comp[:, :, 1] / np.max(comp[:, :, 1])
    plt.imshow(comp)
    plt.show()
    cv2.estimateAffinePartial2D()

def apply_translation(img, translation):
    tmat = np.array([[1.0, 0.0, translation[0]],[0.0, 1.0, translation[1]],[0.0, 0.0, 1.0]])
    atm = tf.AffineTransform(tmat)
    reg = tf.warp(img, atm, preserve_range=True)
    return reg


register_pair(a, b, overlap = 0.5, direction = "east")