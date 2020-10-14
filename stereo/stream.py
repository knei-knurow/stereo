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
        self.frames_count = 0
        self.start_time = time.time()
        self.last_time = time.time()
        self.render_depth = render_depth
        self.render_preview = render_preview

    def _setup(self, cameras):
        logging.info("Starting depth map stream.")
        self._update(cameras)

    def _update(self, cameras):
        deltatime = (time.time() - self.start_time)
        self.frames_count += 1
        if not (self.frames_count % 10):
            fps = 1 / (time.time() - self.last_time)
            avg = self.frames_count / deltatime
            print("fps: {:.2f}\tavg: {:.2f}".format(fps, avg), flush=True)
        self.last_time = time.time()

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