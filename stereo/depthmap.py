import cv2 as cv
from abc import ABC, abstractmethod
import numpy as np

class StereoVision():
    def __init__(self, calibration):
        self.calibration = calibration
        self.stereo = cv.StereoBM_create()
    
    @abstractmethod
    def get_depth(self):
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

        self.stereo.setMinDisparity(4)
        self.stereo.setNumDisparities(128)
        self.stereo.setBlockSize(21)
        self.stereo.setSpeckleRange(16)
        self.stereo.setSpeckleWindowSize(45)

        self.depth = None

    def calculate_depth(self, left, right):
        left = cv.remap(left, self.left_max_x, self.left_map_y, 
            cv.INTER_LINEAR
        )
        right = cv.remap(right, self.right_max_x, self.right_map_y,
            cv.INTER_LINEAR
        )

        self.depth = self.stereo.compute(left, right) / 2048
        return self.depth
