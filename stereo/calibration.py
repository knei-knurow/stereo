from .camera import DEF_SIZE
import cv2 as cv
import numpy as np
import os

DEF_CALIB_IMG_PATH = os.path.normpath("calibraion")
DEF_CALIB_LEFT_IMG_PATH = os.path.join(DEF_CALIB_IMG_PATH, "left")
DEF_CALIB_RIGHT_IMG_PATH = os.path.join(DEF_CALIB_IMG_PATH, "right")

DEF_CALIB_IMG_PAIR_PATH = os.path.join(DEF_CALIB_IMG_PATH, "pair")
DEF_CALIB_LEFT_IMG_PAIR_PATH = os.path.join(DEF_CALIB_IMG_PAIR_PATH, "left")
DEF_CALIB_RIGHT_IMG_PAIR_PATH = os.path.join(DEF_CALIB_IMG_PAIR_PATH, "right")

DEF_CB_PATTERN_SIZE = (7, 7)
DEF_CB_SQUARE_SIZE = 1.0

def load_calib_imgs(paths):
    """Load set of images from the given paths."""
    if not isinstance(paths, (tuple, list)):
        paths = (paths,)

    groups = []
    for path in paths:
        images = []
        for f in os.listdir(path):
            image = cv.imread(os.path.join(path, f))
            image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
            images.append(image)
        groups.append(images)
    
    return groups

def load_2cams_calib_imgs():
    return load_calib_imgs((DEF_CALIB_LEFT_IMG_PATH, DEF_CALIB_RIGHT_IMG_PATH,
        DEF_CALIB_LEFT_IMG_PAIR_PATH, DEF_CALIB_RIGHT_IMG_PAIR_PATH)
    )

def find_chessboards(imgs, pattern_size=DEF_CB_PATTERN_SIZE,
    square_size=DEF_CB_SQUARE_SIZE, return_nones=False):
    obj_pts = []
    img_pts = []
    for img in imgs:
        # Find chessboard corners
        ret, corners = cv.findChessboardCorners(img, pattern_size,
            cv.CALIB_CB_ADAPTIVE_THRESH
            | cv.CALIB_CB_NORMALIZE_IMAGE 
            | cv.CALIB_CB_FAST_CHECK
        )
        
        # If no corners found, continue
        if not ret:
            if return_nones:
                obj_pts.append(None)
                img_pts.append(None)
            continue
        
        # Increase the accuracy of corner points
        corners = cv.cornerSubPix(img, corners, (11, 11), (-1, -1), 
            (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )

        # Add chessboard points as object points
        obj = np.zeros((7 * 7, 3), np.float32)
        obj[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2) * square_size
        obj_pts.append(obj)

        # Add chessboard points as image points
        img_pts.append(corners)
    return obj_pts, img_pts

def find_pair_chessboards(imgs0, imgs1, pattern_size=DEF_CB_PATTERN_SIZE):
    obj_pts, img0_pts = find_chessboards(imgs0, pattern_size, True)
    _, img1_pts = find_chessboards(imgs1, pattern_size, True)

    for i in range(len(obj_pts)):
        if img0_pts[i] == None or img1_pts[i] == None:
            del img0_pts[i], img1_pts[i]
            del obj_pts[i]
    
    return obj_pts, img0_pts, img1_pts

def find_2cams_chessboards(left_imgs, right_imgs, left_pair_imgs,
    right_pair_imgs, pattern_size=DEF_CB_PATTERN_SIZE):

    obj_pts, left_img_pair_pts, right_img_pair_pts = find_pair_chessboards(
        left_pair_imgs, right_pair_imgs, pattern_size)

    obj_pair_pts, left_img_pts = find_chessboards(left_imgs, pattern_size)
    _, right_img_pts = find_chessboards(right_imgs, pattern_size)

    return (obj_pts, left_img_pts, right_img_pts, 
        obj_pair_pts, left_img_pair_pts, right_img_pair_pts)

def calibrate_cam(obj_pts, img_pts, size=DEF_SIZE):
    _, matrix, distortion_coeff, rot_vec, trans_vec = cv.calibrateCamera(
        obj_pts, img_pts, size, None, None
    )
    
    return matrix, distortion_coeff, rot_vec, trans_vec

def calibrate_2cams(obj_pts, left_img_pts, right_img_pts, size):
    left_matrix, left_dist_coeff, left_rot_vec, left_trans_vec = \
        calibrate_cam(obj_pts, left_img_pts, size)

    right_matrix, right_dist_coeff, right_rot_vec, right_trans_vec = \
        calibrate_cam(obj_pts, right_img_pts, size)

    _, _, _, _, _, rot_vec, trans_vec, _, _ = cv.stereoCalibrate(
        obj_pts,
        left_img_pts, right_img_pts,
        left_matrix, left_dist_coeff,
        right_matrix, right_dist_coeff,
        size, None, None, None, None,
        cv.CALIB_FIX_INTRINSIC,
        (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    )

    return left_matrix, left_dist_coeff, left_rot_vec, left_trans_vec, \
        right_matrix, right_dist_coeff, right_rot_vec, right_trans_vec, \
        rot_vec, trans_vec
