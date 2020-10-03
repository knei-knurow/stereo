from .camera import (capture_rgb, capture_gray, DEF_WIDTH, DEF_HEIGHT, DEF_API,
    stream)
import cv2 as cv
import ipywidgets
from IPython.display import clear_output, display
from PIL import Image
import io

def img_nb(array):
    """Display numpy array image as Jupyter notebook cell output."""
    display(Image.fromarray(array))

def capture_nb(devices=0):
    """Capture image and display it as Jupyter notebook cell output."""
    frames = capture_rgb(devices)
    if isinstance(frames, (tuple, list)):
        for frame in frames:
            img_nb(frame)
    else:
        img_nb(frames)

def capture_gray_nb(devices=0):
    """Capture grayscaled image and display it as Jupyter notebook cell output.
    """
    frames = capture_gray(devices)
    if isinstance(frames, (tuple, list)):
        for frame in frames:
            img_nb(frame)
    else:
        img_nb(frames)

def _stream_nb_update(frames, widgets):
    for frame, widget in zip(frames, widgets):
        bytes_stream = io.BytesIO()
        Image.fromarray(frame).save(bytes_stream, format="jpeg")
        widget.value = bytes_stream.getvalue()

    return 0

def _stream_nb_cleanup(widgets):
    pass

def stream_nb(devices=0, width=DEF_WIDTH, height=DEF_HEIGHT, 
    transformations=None, api=DEF_API, update_fns=None, cleanup_fns=None):
    if not isinstance(devices, (list, tuple)):
        devices = (devices,)
    
    widgets = []
    for _ in range(len(devices)):
        widgets.append(ipywidgets.Image(width=640))
    display(*widgets)

    if update_fns is None:
        update_fns = []
    if cleanup_fns is None:
        cleanup_fns = []
    update_fns = (lambda frames: _stream_nb_update(frames, widgets), *update_fns)
    cleanup_fns = (lambda: _stream_nb_cleanup(widgets), *cleanup_fns)

    if transformations is None:
        transformations = []
    transformations.insert(0, (cv.cvtColor, cv.COLOR_BGR2RGB))

    stream(devices=devices, width=width, height=height,
        transformations=transformations, api=api, update_fns=update_fns,
        cleanup_fns=cleanup_fns)