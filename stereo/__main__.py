from stereo import camera
import stereo
import cv2 as cv


stereo.camera.stream_cv((0, 1, 2), transformations=[
    [cv.cvtColor, cv.COLOR_BGR2GRAY]
])
print("Hello world")
cv.destroyAllWindows()


