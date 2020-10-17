import stereo as st
import numpy as np
import cv2 as cv

cameras = st.Cameras([0,1], transformations=[
    (cv.cvtColor, cv.COLOR_BGR2GRAY)
])
cameras.to_csi_device()

calibration = st.Calibration2Cams()
calibration.load("calibrated/2cam-csi-12cm-v1.yaml")
stereo = st.StereoVision2Cams(calibration)

# cameras.stream()

stream = st.DepthStream(cameras, stereo, True)
stream.start()