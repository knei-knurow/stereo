from .cameras import DEF_SIZE
from .exceptions import *
import cv2 as cv
import numpy as np
import os
import yaml
import logging
from abc import ABC, abstractmethod

DEF_CALIB_IMG_PATH = os.path.normpath("calibrated")

class Calibration(ABC):
    @abstractmethod
    def __init__(self):
        self.calibrated = False

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
                    raise CalibrationDimentionsNotMatch()
                    
                images.append(image)
            groups.append(images)
        
        return groups

    @abstractmethod
    def load_images(self):
        pass

    def _find_chessboards(self, imgs, keep_preview_imgs=False, 
        return_nones=False):
        """Find chessboards in the given images."""
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

    def _calculate_reprojection_error(self, obj_pts, img_pts, rot_vec,
        trans_vec, matrix, dist_coeff):
        """Calculate re-projection error (requires calibration)."""
        error = 0
        for i in range(len(obj_pts)):
            projected_img_pts, _ = cv.projectPoints(obj_pts[i], rot_vec[i], 
                trans_vec[i], matrix, dist_coeff)
            error += cv.norm(img_pts[i], projected_img_pts, cv.NORM_L2) \
                / len(projected_img_pts)
        return error / len(obj_pts)

    @abstractmethod
    def calculate_reprojection_error(self):
        pass

    def _undistort(self, img, matrix, dist_coeff, crop=True):
        """Undistord given image (requires calibration)."""
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
        self.both_rot_matrix = None
        self.both_trans_vec = None

        self.left_rectif = None
        self.right_rectif = None
        self.left_proj = None
        self.right_proj = None
        self.left_roi = None
        self.right_roi = None

        self.left_reprojection_error = None
        self.right_reprojection_error = None

    def load_images(self):
        """Load set of corresponding left and right images from 
           calibration_path/left and calibration_path/right.
        """
        logging.info("Loading sets of corresponding left and right images "
            "from {}.".format(self.calibration_path))
        self.left_imgs, self.right_imgs = self._load_images([
            os.path.join(self.calibration_path, "left"),
            os.path.join(self.calibration_path, "right")]
        )
        logging.info("Loaded {} pairs.".format(len(self.left_imgs)))
        return len(self.left_imgs)

    def find_chessboards(self, keep_chessboard_preview_imgs=False):
        # Get chessboard points as image points
        logging.info("Finding chessboard patterns in the images.")
        left_img_pts, left_chessboard_preview_imgs = self._find_chessboards(
            self.left_imgs, keep_chessboard_preview_imgs, True
        )
        right_img_pts, right_chessboard_preview_imgs = self._find_chessboards(
            self.right_imgs, keep_chessboard_preview_imgs, True
        )
        # Set only pairs with both valid images
        valid_pairs_cnt = 0
        for i in range(len(left_img_pts)):
            if (not left_img_pts[i] is None) and (not right_img_pts[i] is None):
                valid_pairs_cnt += 1
                self.left_img_pts.append(left_img_pts[i])
                self.right_img_pts.append(right_img_pts[i])
                # Set chessboard preview images if necessary
                if keep_chessboard_preview_imgs:
                    self.left_chessboard_preview_imgs.append(
                        left_chessboard_preview_imgs[i])
                    self.right_chessboard_preview_imgs.append(
                        right_chessboard_preview_imgs[i])
        logging.info("Found chessboard patterns in {} pairs.".format(
            valid_pairs_cnt)
        )

        # Set chessboard points as object points
        obj = np.zeros((7 * 7, 3), np.float32)
        obj[:, :2] = np.mgrid[0:7, 0:7].T.reshape(-1, 2) \
            * self.pattern_square_size
        self.obj_pts = [obj] * valid_pairs_cnt

        return valid_pairs_cnt
    
    def calibrate(self, load_images=False, keep_chessboard_preview_imgs=False):
        """Perform a complete calibration process."""
        if load_images:
            self.load_images()

        if len(self.left_imgs) == 0:
            logging.warning("No calibration images loaded.")
            self.load_images()

        if len(self.left_imgs) != len(self.right_imgs):
            raise CalibrationImagesNotMatch()

        self.find_chessboards(keep_chessboard_preview_imgs)

        logging.info("Calibrating left camera.")
        _, left_matrix, left_dist_coeff, left_rot_vec, left_trans_vec = \
            cv.calibrateCamera(self.obj_pts, self.left_img_pts,
            (self.width, self.height), None, None
        )
        self.left_matrix = left_matrix
        self.left_dist_coeff = left_dist_coeff
        self.left_rot_vec = left_rot_vec
        self.left_trans_vec = left_trans_vec

        logging.info("Calibrating right camera.")
        _, right_matrix, right_dist_coeff, right_rot_vec, right_trans_vec = \
            cv.calibrateCamera(self.obj_pts, self.right_img_pts,
            (self.width, self.height), None, None
        )
        self.right_matrix = right_matrix
        self.right_dist_coeff = right_dist_coeff
        self.right_rot_vec = right_rot_vec
        self.right_trans_vec = right_trans_vec

        logging.info("Calibrating both cameras.")
        _, _, _, _, _, rot_matrix, trans_vec, _, _ = cv.stereoCalibrate(
            self.obj_pts,
            self.left_img_pts, self.right_img_pts,
            self.left_matrix, self.left_dist_coeff,
            self.right_matrix, self.right_dist_coeff,
            (self.width, self.height), None, None, None, None,
            cv.CALIB_FIX_INTRINSIC,
            (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )
        self.both_rot_matrix = rot_matrix
        self.both_trans_vec = trans_vec

        logging.info("Rectifying cameras.")
        self.left_rectif, self.right_rectif, self.left_proj, self.right_proj, \
            _, self.left_roi, self.right_roi = cv.stereoRectify(
                self.left_matrix, self.left_dist_coeff,
                self.right_matrix, self.right_dist_coeff,
                (self.width, self.height), 
                self.both_rot_matrix, self.both_trans_vec,
                None, None, None, None, None,
                cv.CALIB_ZERO_DISPARITY, 0.25
        )

        self.calibrated = True

        # Set re-projection error
        self.left_reprojection_error, self.right_reprojection_error = \
            self.calculate_reprojection_error()
        logging.info("Calibration finished. Re-projection errors: {}, {}."
            .format(self.left_reprojection_error, 
            self.right_reprojection_error)
        )

    def get_dict(self, numpy2list=False):
        """Return a dict with important calibration parameters."""
        params = {
            "calibrated":self.calibrated,
            "left_matrix":self.left_matrix,
            "left_dist_coeff":self.left_dist_coeff,
            "left_rectif":self.left_rectif,
            "left_proj":self.left_proj,
            "left_roi":self.left_roi,
            "left_reprojection_error":self.left_reprojection_error,
            "right_matrix":self.right_matrix,
            "right_dist_coeff":self.right_dist_coeff,
            "right_rectif":self.right_rectif,
            "right_proj":self.right_proj,
            "right_roi":self.right_roi,
            "right_reprojection_error":self.right_reprojection_error,
            "both_rot_matrix":self.both_rot_matrix,
            "both_trans_vec":self.both_trans_vec,
        }
        if numpy2list:
            for key, value in params.items():
                if isinstance(value, np.ndarray):
                    params[key] = value.tolist()
        return params

    def save(self, filename):
        """Save important calibration parameters to the specified file."""
        logging.info("Saving important calibration parameters to {}."
            .format(filename)
        )
        params = self.get_dict(True)
        with open(filename, "w") as file:
            _ = yaml.dump(params, file)
        return params

    def load(self, filename):
        """Load important calibration parameters from the specified file."""
        logging.info("Loading important calibration parameters {}"
            .format(filename)
        )
        
        with open(filename, "r") as file:
            params = yaml.load(file)

        for value in params.values():
            if value is None:
                raise NotCalibrated()

        for key, value in params.items():
            if isinstance(value, list):
                params[key] = np.array(value)

        self.calibrated = params["calibrated"]
        self.left_matrix = params["left_matrix"]
        self.left_dist_coeff = params["left_dist_coeff"]
        self.left_rectif = params["left_rectif"]
        self.left_proj = params["left_proj"]
        self.left_roi = params["left_roi"]
        self.left_reprojection_error = params["left_reprojection_error"]
        self.right_matrix = params["right_matrix"]
        self.right_dist_coeff = params["right_dist_coeff"]
        self.right_rectif = params["right_rectif"]
        self.right_proj = params["right_proj"]
        self.right_roi = params["right_roi"]
        self.right_reprojection_error = params["right_reprojection_error"]
        self.both_rot_matrix = params["both_rot_matrix"]
        self.both_trans_vec = params["both_trans_vec"]

        return params

    def calculate_reprojection_error(self):
        """Calculate re-projection errors for left and right camera or return
           already calculated ones (requires calibration).
        """
        if not self.calibrated:
            raise NotCalibrated()

        # If errors are already calculated, return them
        if self.left_rot_vec is None or self.left_trans_vec is None \
            or self.right_rot_vec is None or self.right_trans_vec is None:
            return self.left_reprojection_error, self.right_reprojection_error

        # Left camera re-projection
        left_reprojection_error = self._calculate_reprojection_error(
            self.obj_pts, self.left_img_pts, self.left_rot_vec, 
            self.left_trans_vec, self.left_matrix, self.left_dist_coeff
        )
        # Right camera re-projection
        right_reprojection_error = self._calculate_reprojection_error(
            self.obj_pts, self.right_img_pts, self.right_rot_vec, 
            self.right_trans_vec, self.right_matrix, self.right_dist_coeff
        )

        return left_reprojection_error, right_reprojection_error

    def undistort_left(self, img, crop=True):
        """Undistort image captured by left camera (requires calibration)."""
        if not self.calibrated:
            raise NotCalibrated()

        return self._undistort(img, self.left_matrix, self.left_dist_coeff, 
            crop)

    def undistort_right(self, img, crop=True):
        """Undistort image captured by right camera (requires calibration)."""
        if not self.calibrated:
            raise NotCalibrated()

        return self._undistort(img, self.right_matrix, self.right_dist_coeff, 
            crop)