from stereo import camera
import cv2 as cv



print("Hello world")
transformations = [
    [cv.flip, 0],
    [cv.resize, (600, 200)],
    [cv.GaussianBlur, (11, 11), 100]
]

x = camera.capture_rgb(0, transformations=transformations)

cv.imshow("window", x)
cv.waitKey(0)
cv.destroyAllWindows()


