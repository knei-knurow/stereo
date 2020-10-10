import stereo as st
import numpy as np
import cv2 as cv

calibration = st.Calibration2Cams()
calibration.load("calibrated/2cam-usb-12cm-v1.yaml")

cameras = st.Cameras([0, 1], transformations=[
    (cv.cvtColor, cv.COLOR_BGR2GRAY)
])
stereo = st.StereoVision2Cams(calibration)

cameras.capture()
depth = stereo.calculate_depth(cameras.frames[0], cameras.frames[1])

cv.imshow("left", cameras.frames[0])
cv.imshow("right", cameras.frames[1])
cv.imshow("depth", depth)