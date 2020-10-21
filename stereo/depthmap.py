import cv2 as cv
from abc import ABC, abstractmethod
import numpy as np

class StereoVision():
    def __init__(self, calibration):
        self.calibration = calibration
        self.stereo = cv.StereoBM_create()
        self.stereo.setMinDisparity(4)
        self.stereo.setNumDisparities(128)
        self.stereo.setBlockSize(21)
        self.stereo.setSpeckleRange(16)
        self.stereo.setSpeckleWindowSize(45)

    @abstractmethod
    def calculate_depth(self):
        pass

class StereoVision2Cams(StereoVision):
    def __init__(self, calibration):
        super().__init__(calibration)

        self.left_max_x, self.left_map_y = cv.initUndistortRectifyMap(
            self.calibration.left_matrix, self.calibration.left_dist_coeff, 
            self.calibration.left_rectif,
            self.calibration.left_proj, 
            (self.calibration.width, self.calibration.height), cv.CV_32FC1
        )

        self.right_max_x, self.right_map_y = cv.initUndistortRectifyMap(
            self.calibration.right_matrix, self.calibration.right_dist_coeff, 
            self.calibration.right_rectif,
            self.calibration.right_proj, 
            (self.calibration.width, self.calibration.height), cv.CV_32FC1
        )

        self.depth = np.zeros((self.calibration.height, self.calibration.width),
            dtype=np.float32)
        self.left  = np.zeros((self.calibration.height, self.calibration.width),
            dtype=np.uint8)
        self.right  = np.zeros((self.calibration.height, self.calibration.width),
            dtype=np.uint8)

        self.stereo.setROI1(self.calibration.left_roi)
        self.stereo.setROI2(self.calibration.right_roi)

    def preprocess_frames(self):
        self.left = cv.remap(self.left, self.left_max_x, self.left_map_y, 
            cv.INTER_LINEAR
        )
        self.right = cv.remap(self.right, self.right_max_x, self.right_map_y,
            cv.INTER_LINEAR
        )

    def calculate_depth(self):
        self.preprocess_frames()
        self.depth = (self.stereo.compute(self.left, self.right)/ 2048 *255).astype(np.uint8)
        return self.depth
