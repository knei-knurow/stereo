from .camera import capture_rgb, capture_gray
import ipywidgets
from IPython.display import clear_output, display
from PIL import Image

def img_display(array):
    """Display numpy array image as Jupyter notebook cell output."""
    display(Image.fromarray(array))

def capture_display(devices=0):
    """Capture image and display it as Jupyter notebook cell output."""
    frames = capture_rgb(devices)
    if isinstance(frames, (tuple, list)):
        for frame in frames:
            img_display(frame)
    else:
        img_display(frames)

def capture_gray_display(devices=0):
    """Capture grayscaled image and display it as Jupyter notebook cell output.
    """
    frames = capture_gray(devices)
    if isinstance(frames, (tuple, list)):
        for frame in frames:
            img_display(frame)
    else:
        img_display(frames)