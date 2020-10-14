from .exceptions import CameraCaptureError
import cv2 as cv
import numpy as np
import platform
import sys
import io
import IPython
import PIL.Image

DEF_IDS = [0]
DEF_WIDTH = 1280
DEF_HEIGHT = 720
DEF_SIZE = (DEF_WIDTH, DEF_HEIGHT)
DEF_FPS = 30
DEF_MODE = 3

_platform = platform.system()
if  _platform == "Windows":
    # DEF_API = cv.CAP_DSHOW # Weird errors with messed up image array
    DEF_API = cv.CAP_MSMF
elif _platform == "Linux":
    DEF_API = cv.CAP_V4L2
else:
    _backends = []
    for value in cv.videoio_registry.getCameraBackends():
        _backends.append(value)
    DEF_API = _backends[0]

class Cameras:
    def __init__(self, devices=DEF_IDS, size=DEF_SIZE, fps=DEF_FPS, 
        mode=DEF_MODE, transformations=None, api=DEF_API):
        if not isinstance(devices, list):
            self.devices = [devices,]
        else:
            self.devices = devices
        self.width = size[0]
        self.height = size[1]
        self.fps = fps
        self.mode = mode
        self.api = api
        if transformations is None:
            self.transformations = []
        else:
            self.transformations = transformations

        self.frames = []
        for _ in range(len(self.devices)):
            self.frames.append(np.zeros((self.height, self.width, 3), dtype=np.uint8))
            
        self.transform()

    @staticmethod
    def list_backends():
        """List available OpenCV backends."""
        backends = []
        for value in cv.videoio_registry.getCameraBackends():
            backends.append((value, cv.videoio_registry.getBackendName(value)))
        return backends

    @staticmethod
    def list_cams():
        """Brute-force camera device indices and return a list of available ones."""
        cams = []
        for i in range(32):
            cam = cv.VideoCapture(i)
            ret, _ = cam.read()
            if not ret:
                continue
            cams.append(i)
        return cams

    def to_csi_device(self):
        """Convert the camera name to CSI device value."""
        for idx, device in enumerate(self.devices):
            self.devices[idx] = (
                "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
                "video/x-raw(memory:NVMM), "
                "width=(int)%d, height=(int)%d, "
                "format=(string)NV12, framerate=(fraction)%d/1 ! "
                "nvvidconv flip-method=%d ! "
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink"
                % (
                    device, # camera id
                    self.mode, # mode
                    self.width, # width
                    self.height, # height
                    self.fps, # frame rate
                    0, # flip method
                    self.width, # display width
                    self.height, # display height
                )
            )

    def transform(self):
        """For each frame apply given transformations which should be a list 
        like that: [function, arg1, arg2, ...]. Each transformation function has
        to return a new image. Transformations are executed one by one.
        """
        for i in range(len(self.frames)):
            for transformation in self.transformations:
                function = transformation[0]
                if len(transformation) > 1:
                    args = transformation[1:]
                else:
                    args = []
                # function(self.frames[i], *args, dst=self.frames[i])
                self.frames[i] = function(self.frames[i], *args)

    def capture_black_screen(self):
        """Make all frames black."""
        for frame in self.frames:
            frame.fill(0)

    def capture(self):
        """Call cv.VideoCapture() for each device, transform recieved images and
        return as a list of numpy arrays.
        """
        cameras = []
        for device in self.devices:
            camera = cv.VideoCapture(device)
            camera.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
            camera.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
            cameras.append(camera)

        for camera in cameras:
            ret = camera.grab()
            if not ret:
                for c in cameras:
                    c.release()
                raise CameraCaptureError("Unable to grab image from cam", camera)

        for idx, camera in enumerate(cameras):
            ret, self.frames[idx] = camera.retrieve()
            if not ret:
                for c in cameras:
                    c.release()
                raise CameraCaptureError("Unable to retrieve image from cam", camera)
        
        for camera in cameras:
            camera.release()

        self.transform()

        return self.frames

    def capture_rgb(self):
        """Do the same what capture() but after all transformations convert colors
        to RGB.
        """
        self.capture()
        for i in range(len(self.frames)):
            self.frames[i] = cv.cvtColor(self.frames[i], cv.COLOR_BGR2RGB)
        return self.frames

    def capture_gray(self):
        """Do the same what capture() but after all transformations convert colors
        to grayscale.
        """
        self.capture()
        for i in range(len(self.frames)):
            self.frames[i] = cv.cvtColor(self.frames[i], cv.COLOR_BGR2GRAY)
        return self.frames

    def show(self):
        """Show all frames using OpenCV imshow function."""
        for idx, frame in enumerate(self.frames):
            cv.imshow("Frame " + str(idx), frame)
        
        cv.waitKey(0)
        cv.destroyAllWindows()

    def nshow(self):
        """Show all frames using Jupyter Notebook cell output. Apply the
           conversion from BGR to RGB before.
        """
        frames = self.frames.copy()
        for frame in frames:
            frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
            IPython.display.display(PIL.Image.fromarray(frame))

    def _stream_update(self):
        for idx, frame in enumerate(self.frames):
            cv.imshow("Stream " + str(idx), frame)

        if cv.waitKey(1) == ord("q"):
            return False
        return True

    def _stream_cleanup(self):
        cv.destroyAllWindows()
 
    def stream(self, update_fn=_stream_update, cleanup_fn=_stream_cleanup):
        cameras = []
        for device in self.devices:
            camera = cv.VideoCapture(device)
            camera.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
            camera.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
            cameras.append(camera)
        
        running = True
        try:
            while running:
                for camera in cameras:
                    ret = camera.grab()
                    if not ret:
                        for c in cameras:
                            c.release()
                        raise CameraCaptureError(
                            "Unable to grab image from cam", camera
                        )

                for idx, camera in enumerate(cameras):
                    ret, frame = camera.retrieve()
                    if not ret:
                        for c in cameras:
                            c.release()
                        raise CameraCaptureError(
                            "Unable to retrieve image from cam", camera
                        )
                    self.frames[idx] = frame

                self.transform()

                if update_fn(self) == False:
                    running = False

        except KeyboardInterrupt:
            pass
        
        for camera in cameras:
            camera.release()

        cleanup_fn(self)
