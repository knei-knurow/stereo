from stereo import camera
import stereo
import cv2 as cv

# print(stereo.camera.list_cams())
stereo.camera.stream((0,1))
# stereo.notebook.stream(0)

print("Hello world")
cv.destroyAllWindows()


