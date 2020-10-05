from .camera import DEF_SIZE
import cv2 as cv
import numpy as np
import os
from abc import ABC, abstractmethod

DEF_CALIB_IMG_PATH = os.path.normpath("calibration")

class CalibrationError(Exception):
    """Calibration error class."""
    pass

class DimentionsNotMatch(CalibrationError):
    """The dimensions of images used for calibration do not match."""
    pass
    
class NoCalibrationImages(CalibrationError):
    """No valid calibration images found in the specified path."""
    pass

class NotCalibrated(CalibrationError):
    """Action cannot be completed without performed calibration."""

class Calibration(ABC):
    @abstractmethod
    def __init__(self):
        self.calibration_path = DEF_CALIB_IMG_PATH
        self.pattern_size = (7, 7)
        self.pattern_square_size = 1.0
        
        self.width = None
        self.height = None
    
    def _load_images(self, paths):
        """Load set of images from the given paths."""
        if not isinstance(paths, (tuple, list)):
            paths = (paths,)

        groups = []
        for path in paths:
            images = []
            for f in sorted(os.listdir(path)):
                image = cv.imread(os.path.join(path, f))
                image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
                # Set dimenstions of images if not set already
                if self.width == None or self.height == None:
                    self.width, self.height = image.shape[1], image.shape[0]
                elif self.width != image.shape[1] or \
                    self.height != image.shape[0]:
                    raise DimentionsNotMatch()
                    
                images.append(image)
            groups.append(images)
        
        return groups

    @abstractmethod
    def load_images(self):
        pass

    def _find_chessboards(self, imgs, keep_preview_imgs=False, 
        return_nones=False):
        img_pts = []
        preview_imgs = []
        for img in imgs:
            # Find chessboard corners
            ret, corners = cv.findChessboardCorners(img, self.pattern_size,
                cv.CALIB_CB_ADAPTIVE_THRESH
                | cv.CALIB_CB_NORMALIZE_IMAGE 
                | cv.CALIB_CB_FAST_CHECK
            )
            
            # If no corners found, continue
            if not ret:
                if return_nones:
                    img_pts.append(None)
                    if keep_preview_imgs:
                        preview_imgs.append(None)
                continue
            
            # Increase the accuracy of corner points
            corners = cv.cornerSubPix(img, corners, (11, 11), (-1, -1), 
                (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
            )

            # Create preview images if necessary
            if keep_preview_imgs:
                img_rgb = np.repeat(img[:, :, np.newaxis], 3, axis=2)
                preview_imgs.append(cv.drawChessboardCorners(img_rgb,
                    self.pattern_size, corners, True))

            # Add chessboard points as image points
            img_pts.append(corners)

        if len(img_pts) == 0:
            raise NoCalibrationImages()

        return img_pts, preview_imgs

    @abstractmethod
    def calibrate(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def load(self):
        pass

    def _reprojection_error(self, obj_pts, img_pts, rot_vec, trans_vec, matrix,
        dist_coeff):
        """Calclate re-projection error."""
        error = 0
        for i in range(len(obj_pts)):
            projected_img_pts, _ = cv.projectPoints(obj_pts[i], rot_vec[i], 
                trans_vec[i], matrix, dist_coeff)
            error += cv.norm(img_pts[i], projected_img_pts, cv.NORM_L2) \
                / len(projected_img_pts)
        return error

    @abstractmethod
    def reprojection_error(self):
        pass

    def _undistort(self, img, matrix, dist_coeff, crop=True):
        if matrix is None or dist_coeff is None or crop is None:
            raise NotCalibrated()

        new_matrix, roi = cv.getOptimalNewCameraMatrix(matrix, dist_coeff,
            (self.width, self.height), 0)

        undistorted_img = cv.undistorted(img, matrix, dist_coeff, new_matrix)
        if crop:
            x, y, w, h = roi
            undistorted_img = undistorted_img[y:y + h, x:x + w]

        return undistorted_img
    

        

class Calibration2Cams(Calibration):
    def __init__(self):
        super().__init__()
        self.left_imgs = []
        self.right_imgs = []

        self.left_chessboard_preview_imgs = []
        self.right_chessboard_preview_imgs = []

        self.obj_pts = []
        self.left_img_pts = []
        self.right_img_pts = []

        self.left_matrix = None
        self.left_dist_coeff = None
        self.left_rot_vec = None
        self.left_trans_vec = None
        self.right_matrix = None
        self.right_dist_coeff = None
        self.right_rot_vec = None
        self.right_trans_vec = None

        self.left_reprojection_error = None
        self.right_reprojection_error = None

    def load_images(self):
        """Load set of corresponding left and right images from 
           calibration_path/left and calibration_path/right.
        """
        self.left_imgs, self.right_imgs = self._load_images([
            os.path.join(self.calibration_path, "left"),
            os.path.join(self.calibration_path, "right")]
        )
        return len(self.left_imgs)

    def find_chessboards(self, keep_chessboard_preview_imgs=False):
        # Get chessboard points as image points
        left_img_pts, left_chessboard_preview_imgs = self._find_chessboards(
            self.left_imgs, keep_chessboard_preview_imgs, True
        )
        right_img_pts, right_chessboard_preview_imgs = self._find_chessboards(
            self.right_imgs, keep_chessboard_preview_imgs, True
        )
        # Add only pairs with both valid images
        valid_pairs_cnt = 0
        for i in range(len(left_img_pts)):
            if (not left_img_pts[i] is None) and (not right_img_pts[i] is None):
                valid_pairs_cnt += 1
                self.left_img_pts.append(left_img_pts[i])
                self.right_img_pts.append(right_img_pts[i])
                # Add chessboard preview images if necessary
                if keep_chessboard_preview_imgs:
                    self.left_chessboard_preview_imgs.append(
                        left_chessboard_preview_imgs[i])
                    self.right_chessboard_preview_imgs.append(
                        right_chessboard_preview_imgs[i])

        # Add chessboard points as object points
        obj = np.zeros((7 * 7, 3), np.float32)
        obj[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2) \
            * self.pattern_square_size
        self.obj_pts = [obj] * valid_pairs_cnt

        return valid_pairs_cnt
    
    def calibrate(self):
        # Calibrate left camera
        _, left_matrix, left_dist_coeff, left_rot_vec, left_trans_vec = \
            cv.calibrateCamera(self.obj_pts, self.left_img_pts,
            (self.width, self.height), None, None
        )
        # Calibrate right camera
        _, right_matrix, right_dist_coeff, right_rot_vec, right_trans_vec = \
            cv.calibrateCamera(self.obj_pts, self.right_img_pts,
            (self.width, self.height), None, None
        )

        # Add left camera coefficients
        self.left_matrix = left_matrix
        self.left_dist_coeff = left_dist_coeff
        self.left_rot_vec = left_rot_vec
        self.left_trans_vec = left_trans_vec

        # Add right camera coefficients
        self.right_matrix = right_matrix
        self.right_dist_coeff = right_dist_coeff
        self.right_rot_vec = right_rot_vec
        self.right_trans_vec = right_trans_vec

        # Calibrate both cameras together
        _, _, _, _, _, rot_matrix, trans_vec, _, _ = cv.stereoCalibrate(
            self.obj_pts,
            self.left_img_pts, self.right_img_pts,
            self.left_matrix, self.left_dist_coeff,
            self.right_matrix, self.right_dist_coeff,
            (self.width, self.height), None, None, None, None,
            cv.CALIB_FIX_INTRINSIC,
            (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )

        # Add both cameras coefficients
        self.both_rot_matrix = rot_matrix
        self.both_trans_ves = trans_vec

    def save(self):
        pass

    def load(self):
        pass

    def reprojection_error(self):
        # Left camera re-projection
        if not (self.obj_pts == None or self.left_img_pts == None
            or self.left_rot_vec == None or self.left_trans_vec == None
            or self.left_matrix == None or self.left_dist_coeff == None):

            self.left_reprojection_error = self._reprojection_error(
                self.obj_pts, self.left_img_pts, self.left_rot_vec, 
                self.left_trans_vec, self.left_matrix, self.left_dist_coeff
            )
        
        # Right camera re-projection
        if not (self.obj_pts == None or self.right_img_pts == None
            or self.right_rot_vec == None or self.right_trans_vec == None
            or self.right_matrix == None or self.right_dist_coeff == None):

            self.right_reprojection_error = self._reprojection_error(
                self.obj_pts, self.right_img_pts, self.right_rot_vec, 
                self.right_trans_vec, self.right_matrix, self.right_dist_coeff
            )

    def undistort_left(self, img, crop=True):
        """Undistort image captured by left camera (requires calibration)."""
        return self._undistort(img, self.left_matrix, self.left_dist_coeff, 
            crop)

    def undistort_right(self, img, crop=True):
        """Undistort image captured by right camera (requires calibration)."""
        return self._undistort(img, self.right_matrix, self.right_dist_coeff, 
            crop)
    
DEF_CALIB_IMG_PATH = os.path.normpath("calibration")
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

def _find_pair_chessboards(imgs0, imgs1, pattern_size=DEF_CB_PATTERN_SIZE):
    obj_pts, img0_pts = find_chessboards(imgs0, pattern_size, True)
    _, img1_pts = find_chessboards(imgs1, pattern_size, True)

    for i in range(len(obj_pts)):
        if img0_pts[i] == None or img1_pts[i] == None:
            del img0_pts[i], img1_pts[i]
            del obj_pts[i]
    
    return obj_pts, img0_pts, img1_pts

def find_2cams_chessboards(left_imgs, right_imgs, left_pair_imgs,
    right_pair_imgs, pattern_size=DEF_CB_PATTERN_SIZE):

    obj_pts, left_img_pair_pts, right_img_pair_pts = _find_pair_chessboards(
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

def calculate_reprojection_err(obj_pts, rot_vec, trans_vec, matrix, dist_coeff):
    pass

def save_2cams_calibration():
    pass

def load_2cams_calibration():
    pass
