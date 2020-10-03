import cv2 as cv
import numpy as np
from collections.abc import Iterable
import platform
import sys

DEF_ID = 0
DEF_WIDTH = 640
DEF_HEIGHT = 480
DEF_FPS = 30
DEF_MODE = 3

def list_backends():
    """List available OpenCV backends."""
    backends = []
    for value in cv.videoio_registry.getCameraBackends():
        backends.append((value, cv.videoio_registry.getBackendName(value)))
    return backends

platform = platform.system()
if  platform == "Windows":
    DEF_API = cv.CAP_DSHOW
elif platform == "Linux":
    DEF_API = cv.CAP_V4L2
else:
    DEF_API = list_backends()[0][0]

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

def get_usb_device(name):
    """Convert the camera name to USB device value."""
    return name

def get_csi_device(name, width=DEF_WIDTH, height=DEF_HEIGHT, fps=DEF_FPS, 
    mode=DEF_MODE):
    """Convert the camera name to CSI device value."""
    return (
        "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            name, # camera id
            mode, # mode
            width, # width
            height, # height
            fps, # frame rate
            0, # flip method
            width, # display width
            height, # display height
        )
    )

def transform(frames, transformations):
    """For each frame apply given transformations which should be a list 
       like that: [function, arg1, arg2, ...]. Each transformation function has
       to return a new image. Transformations are executed one by one.
    """
    if not isinstance(frames, list):
        frames = [frames,]

    if not isinstance(transformations, (tuple, list)):
        transformations = (transformations,)
    
    for i in range(len(frames)):
        for transformation in transformations:
            function = transformation[0]
            if len(transformation) > 1:
                args = transformation[1:]
            else:
                args = []
            frame = function(frames[i], *args)
            frames[i] = frame
    
    if len(frames) == 1:
        return frames[0]
    else:
        return frames

def capture(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, transformations=None,
    api=DEF_API):
    """Call cv.VideoCapture() for each device, transform recieved images and
       return as a list of numpy arrays.
    """
    if not isinstance(devices, (tuple, list)):
        devices = (devices,)
    
    if transformations is None:
        transformations = []

    cameras = []
    for device in devices:
        camera = cv.VideoCapture(device, api)
        camera.set(cv.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        cameras.append(camera)
    
    frames = []
    for camera in cameras:
        ret = camera.grab()
        if not ret:
            for camera in cameras:
                camera.release()
            raise Exception("Unable to grab image from cam", camera)

    for camera in cameras:
        ret, frame = camera.retrieve()
        camera.release()
        if not ret:
            for camera in cameras:
                camera.release()
            raise Exception("Unable to retrieve image from cam", camera)
        frames.append(frame)
    
    frames = transform(frames, transformations)

    return frames

def capture_rgb(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, 
    transformations=None):
    """Do the same what capture() but before all transformations convert colors
       to RGB.
    """
    if transformations is None:
        transformations = []
    transformations.insert(0, [cv.cvtColor, cv.COLOR_BGR2RGB])
    return capture(devices=devices, width=width, height=height, 
        transformations=transformations)

def capture_gray(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, 
    transformations=None):
    """Do the same what capture() but before all transformations convert colors
       to grayscale.
    """
    if transformations is None:
        transformations = []
    transformations.insert(0, [cv.cvtColor, cv.COLOR_BGR2GRAY])
    return capture(devices=devices, width=width, height=height, 
        transformations=transformations)

def stream(update_fn, devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, transformations=None,
    api=DEF_API, cleanup_fn=None):
    if not isinstance(devices, (tuple, list)):
        devices = (devices,)
    
    if transformations is None:
        transformations = []

    cameras = []
    for device in devices:
        camera = cv.VideoCapture(device, api)
        camera.set(cv.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        cameras.append(camera)
    
    running = True
    frames = [np.zeros((height, width, 3))] * len(cameras)
    try:
        while running:
            for camera in cameras:
                ret = camera.grab()
                if not ret:
                    print("Unable to grab image from cam", camera, file=sys.stderr)

            for idx, camera in enumerate(cameras):
                ret, frame = camera.retrieve()
                if not ret:
                    for camera in cameras:
                        print("Unable to retrieve image from cam", camera, 
                            file=sys.stderr)
                    continue
                frames[idx] = frame

            transformed = transform(frames, transformations)

            ret = update_fn(transformed)
            if ret == -1:
                running = False
    except KeyboardInterrupt:
        pass
    
    for camera in cameras:
        camera.release()
    if cleanup_fn is not None:
        cleanup_fn()

def _stream_cv_update(frames):
    if isinstance(frames, list):
        for idx, frame in enumerate(frames):
            cv.imshow("Stream " + str(idx), frame)
    else:
        cv.imshow("Stream", frames)
    if cv.waitKey(1) == ord("q"):
        return -1
    return 0

def _stream_cv_cleanup():
    cv.destroyAllWindows()

def stream_cv(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT,
    transformations=None, api=DEF_API):
    stream(update_fn=_stream_cv_update, devices=devices, width=width,
        height=height, transformations=transformations, api=api, 
        cleanup_fn=_stream_cv_cleanup)