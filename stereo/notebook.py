from .cameras import Cameras
import cv2 as cv
import ipywidgets
from IPython.display import clear_output, display
from PIL import Image
import io

def nbimg(arrays):
    """Display numpy array image as Jupyter notebook cell output."""
    if isinstance(arrays, (tuple, list)):
        for array in arrays:
            nbimg(array)
    else:
        display(Image.fromarray(arrays))

def nbcapture(cameras):
    """Capture image and display it as Jupyter notebook cell output."""
    frames = cameras.capture_rgb()
    for frame in frames:
        nbimg(frame)

def nbcapture_gray(cameras):
    """Capture grayscaled image and display it as Jupyter notebook cell output.
    """
    frames = cameras.capture_gray()
    for frame in frames:
        nbimg(frame)

def _nbstream_update(frames, widgets):
    for frame, widget in zip(frames, widgets):
        bytes_stream = io.BytesIO()
        Image.fromarray(frame).save(bytes_stream, format="jpeg")
        widget.value = bytes_stream.getvalue()

    return 0

def _nbstream_cleanup(widgets):
    pass

def nbstream(cameras, update_fns=None, cleanup_fns=None):
    widgets = []
    for _ in range(len(cameras.devices)):
        widgets.append(ipywidgets.Image(width=640))
    display(*widgets)

    if update_fns is None:
        update_fns = lambda self: _nbstream_update(self, widgets)
    if cleanup_fns is None:
        cleanup_fns = lambda self: _nbstream_cleanup(widgets)

    cameras.stream()