import stereo as st
import numpy as np
import cv2 as cv

c = st.Calibration2Cams()
c.calibration_path = "calibration-images/2cam-csi-12cm"
c.pattern_size = (9, 6)
c.load_images()

c.calibrate(True)