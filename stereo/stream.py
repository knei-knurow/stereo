from abc import ABC, abstractmethod
import cv2 as cv
import io
import IPython
import PIL.Image
import ipywidgets
import threading
import logging
import time

class Stream(ABC):
    @abstractmethod
    def __init__(self, cameras):
        self.cameras = cameras
        self.running = False
        self.frames_count = 0
        self.start_time = time.time()
        self.last_time = time.time()
        self.fps = -1
        self.fps_avg = -1

    def update_fps(self, log=True):
        deltatime = (time.time() - self.start_time)
        self.frames_count += 1
        if not (self.frames_count % 10):
            self.fps = 1 / (time.time() - self.last_time)
            self.fps_avg = self.frames_count / deltatime
            if log:
                print("fps: {:.2f}\tavg: {:.2f}".format(self.fps, self.fps_avg), flush=True)
        self.last_time = time.time()

    @abstractmethod
    def _setup(self, cameras):
        pass

    @abstractmethod
    def _update(self, cameras):
        pass

    @abstractmethod
    def _cleanup(self, cameras):
        pass

    def _start(self):
        self._setup(self.cameras)

        self.running = True
        self.cameras.stream(
            update_fn=lambda cameras: self._update(cameras),
            cleanup_fn=lambda cameras: self._cleanup(cameras),
        )
        self.running = False

    @abstractmethod
    def start(self):
        pass

    def stop(self):
        self.running = False

class NStream(Stream):
    def __init__(self, cameras, sep_thread=False):
        super().__init__(cameras)
        self.widgets = []
        for _ in range(len(self.cameras.devices)):
            self.widgets.append(ipywidgets.Image(width=self.cameras.width))
        self._sep_thread = sep_thread

    def _setup(self, cameras):
        logging.info("Starting jupyter notebook stream.")
        self.cameras.capture_black_screen()
        IPython.display.display(*self.widgets)
        self._update(cameras)

    def _update(self, cameras):
        for frame, widget in zip(cameras.frames, self.widgets):
            bytes_stream = io.BytesIO()
            PIL.Image.fromarray(frame).save(bytes_stream, format="jpeg")
            widget.value = bytes_stream.getvalue()
        return self.running

    def _cleanup(self, cameras):
        logging.info("Closing jupyter notebook stream.")
        for widget in self.widgets:
            widget.close()

    def start(self):
        if self._sep_thread:
            thread = threading.Thread(target=self._start)
            thread.start()
        else:
            self._start()

    def stop(self):
        self.running = False
        
class DepthStream(Stream):
    def __init__(self, cameras, stereo, sep_thread=True, render_depth=True,
        render_preview=False):
        super().__init__(cameras)
        self._sep_thread = sep_thread
        self.stereo = stereo
        self.render_depth = render_depth
        self.render_preview = render_preview

    def _setup(self, cameras):
        logging.info("Starting depth map stream.")
        self._update(cameras)

    def _update(self, cameras):
        self.update_fps()
        self.stereo.left, self.stereo.right = cameras.frames[0], cameras.frames[1]
        depth = self.stereo.calculate_depth()
        
        if self.render_preview:
            cv.imshow("Left", self.stereo.left)

        if self.render_depth:
            depth = cv.applyColorMap(depth, cv.COLORMAP_JET)
            cv.imshow("Depth", depth)
            if cv.waitKey(1) == ord("q"):
                return False
        return self.running

    def _cleanup(self, cameras):
        pass

    def start(self):
        if self._sep_thread:
            thread = threading.Thread(target=self._start)
            thread.start()
        else:
            self._start()

    def stop(self):
        self.running = False


class NDepthStream(Stream):
    def __init__(self, cameras, stereo, sep_thread=True):
        super().__init__(cameras)
        self.stereo = stereo
        self.widgets = []
        self.widgets.append(ipywidgets.Image(width=720))
        self.widgets.append(ipywidgets.Image(width=720))
        self.widget_fps = ipywidgets.Label("ASDF")
        self._sep_thread = sep_thread

    def _setup(self, cameras):
        logging.info("Starting depth-map jupyter notebook stream.")
        self.cameras.capture_black_screen()
        IPython.display.display(*self.widgets)
        IPython.display.display(self.widget_fps)
        self._update(cameras)

    def _update(self, cameras):
        self.update_fps(False)
        self.widget_fps.value = "FPS:\t{:.2f}\tAVG:\t{:.2f}".format(self.fps, self.fps_avg)

        self.stereo.left, self.stereo.right = cameras.frames[0], cameras.frames[1]
        depth = self.stereo.calculate_depth()
        depth = cv.applyColorMap(depth, cv.COLORMAP_JET)
        depth = cv.cvtColor(depth, cv.COLOR_BGR2RGB)
        
        bytes_stream = io.BytesIO()
        PIL.Image.fromarray(depth).save(bytes_stream, format="jpeg")
        self.widgets[0].value = bytes_stream.getvalue()

        bytes_stream = io.BytesIO()
        PIL.Image.fromarray(self.cameras.frames[0]).save(bytes_stream, format="jpeg")
        self.widgets[1].value = bytes_stream.getvalue()
        return self.running

    def _cleanup(self, cameras):
        logging.info("Closing jupyter notebook stream.")
        for widget in self.widgets:
            widget.close()

    def start(self):
        if self._sep_thread:
            thread = threading.Thread(target=self._start)
            thread.start()
        else:
            self._start()

    def stop(self):
        self.running = False