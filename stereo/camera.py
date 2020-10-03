import cv2 as cv
from collections.abc import Iterable

DEF_ID = 0
DEF_WIDTH = 640
DEF_HEIGHT = 480
DEF_FPS = 30
DEF_MODE = 3

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

def name_to_index(name):
    if name in ("left", "l"):
        return 0
    elif name in ("right", "r"):
        return 1
    elif name in ("center", "c"):
        return 2
    else:
        return name

def get_usb_device(name):
    """Convert the camera name to USB device value."""
    return name_to_index(name)

def get_csi_device(name, width=DEF_WIDTH, height=DEF_HEIGHT, fps=DEF_FPS, 
    mode=DEF_MODE):
    """Convert the camera name to CSI device value."""
    name = name_to_index(name)
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
    if not isinstance(frames, (tuple, list)):
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
            frames[i] = function(frames[i], *args)
    
    if len(frames) == 1:
        return frames[0]
    else:
        return frames

def capture(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, transformations=[]):
    """Call cv.VideoCapture() for each device, transform recieved images and
       return as a list of numpy arrays.
    """
    if not isinstance(devices, (tuple, list)):
        devices = (devices,)

    cameras = []
    for device in devices:
        camera = cv.VideoCapture(device)
        camera.set(cv.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv.CAP_PROP_FRAME_HEIGHT, height)
        cameras.append(camera)
    
    frames = []
    for camera in cameras:
        ret = camera.grab()
        if not ret:
            raise Exception("Unable to grab image from cam", camera)

    for camera in cameras:
        ret, frame = camera.retrieve()
        if not ret:
            raise Exception("Unable to retrieve image from cam", camera)
        frames.append(frame)
    
    frames = transform(frames, transformations)

    return frames

def capture_rgb(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, 
    transformations=[]):
    """Do the same what capture() but before all transformation convert colors
       to RGB.
    """
    transformations.insert(0, [cv.cvtColor, cv.COLOR_BGR2RGB])
    return capture(devices=devices, width=width, height=height, 
        transformations=transformations)

def capture_gray(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, 
    transformations=[]):
    """Do the same what capture() but before all transformation convert colors
       to grayscale.
    """
    transformations.insert(0, [cv.cvtColor, cv.COLOR_BGR2GRAY])
    return capture(devices=devices, width=width, height=height, 
        transformations=transformations)
