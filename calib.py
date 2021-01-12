import cv2 as cv
import numpy as np
import os   
import numpy as np
import time

from PIL import Image as im

DEF_CAL_IMG_PATH = os.path.normpath("calibration-images/2cam-csi-12cm")

class Camera:
	def __init__(self, camID, name, interface, mode, width, height, framerate, flipMethod, displayFormat ):
		self.camID = camID
		self.name = name
		self.interface = interface
		self.mode = mode
		self.width = width
		self.height = height
		self.framerate = framerate
		
		self.flipMethod = flipMethod
		self.displayWidth = width
		self.displayHeight = height
		self.displayFormat = displayFormat

	def getSource(self):
		return(
		"nvarguscamerasrc sensor-id=%d sensor-mode=%d !"
		"video/x-raw(memory:NVMM), "
		"width=(int)%d, "
		"height=(int)%d, "
		"format=(string)NV12, "
		"framerate=(fraction)%d/1 ! "
		"nvvidconv flip-method=%d ! "
		"video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
		"videoconvert ! "
		"video/x-raw, format=(string)%s ! appsink"
			% (
				self.camID,		# cam ID
				self.mode,		# cam mode (0,1,2,3)
				self.width,		# input width
				self.height,		# input height		
				self.framerate,		# fps
				self.flipMethod, 	# flip

				self.displayWidth,
				self.displayHeight,
				self.displayFormat
			
			)
		)
	
	def createVideoCapture(self):
		self.video = cv.VideoCapture(self.getSource())
		self.video.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
		self.video.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)

	def shot(self):
		self.video.grab()
		_, self.frame = self.video.retrieve()
	
	def show(self):
		self.frame = cv.cvtColor(self.frame, cv.COLOR_BGRA2RGB)
		cv.imshow(self.name, self.frame)

	def conv_n_save(self, i):		
		self.img = self.frame
		self.folder = os.path.join(DEF_CAL_IMG_PATH, self.name)
		self.path = self.folder + "/%d.png" %i	
		cv.imwrite(self.path, self.img)
		print("Saved image, path=", self.path)


def main():

	count = 0
		
	camL = Camera(0, "left", "csi", 3, 1280, 720, 30, 0, "BGR")
	camR = Camera(1, "right","csi", 3, 1280, 720, 30, 0, "BGR")

	time.sleep(5)
	camL.createVideoCapture();
	camR.createVideoCapture();

	while True:
			
		camL.shot()
		camR.shot()

		camL.show()
	    camR.show()			

	    if(cv.waitKey(1) == ord('q')):
			camL.conv_n_save(count)
			camR.conv_n_save(count)
			count+=1

main()
cv.destroyAllWindows()


