from abc import ABC, abstractmethod
import cv2 as cv
import io
import IPython
import PIL.Image
import ipywidgets
import threading
import logging
import time
import yaml


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
                logging.info("fps: {:.2f}\tavg: {:.2f}"
                             .format(self.fps, self.fps_avg))
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
        try:
            self.cameras.stream(
                update_fn=lambda cameras: self._update(cameras),
                cleanup_fn=lambda cameras: self._cleanup(cameras),
            )
        except Exception:
            logging.error("Fatal exception in the main stream loop:",
                          exc_info=True)
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
        self._sep_thread = sep_thread

    def _setup(self, cameras):
        logging.info("Starting jupyter notebook stream.")
        for _ in range(len(self.cameras.devices)):
            self.widgets.append(ipywidgets.Image(width=480))
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
        self.widgets = []


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
    def __init__(self, cameras, stereo, sep_thread=True, render_depth=True,
                 render_preview=False):
        super().__init__(cameras)
        self.stereo = stereo

        self.widgets = []
        self.widgets.append(ipywidgets.Image(width=720))
        self.widgets.append(ipywidgets.Image(width=720))
        self.widget_fps = ipywidgets.Label()

        self.render_depth = render_depth
        self.render_preview = render_preview

        self._sep_thread = sep_thread

    def _setup(self, cameras):
        logging.info("Starting depth-map jupyter notebook stream.")
        self.cameras.capture_black_screen()
        IPython.display.display(*self.widgets)
        IPython.display.display(self.widget_fps)
        self._update(cameras)

    def _update(self, cameras):
        self.update_fps(False)
        self.widget_fps.value = "FPS:\t{:.2f}\tAVG:\t{:.2f}" \
            .format(self.fps, self.fps_avg)

        self.stereo.left = cameras.frames[0]
        self.stereo.right = cameras.frames[1]
        depth = self.stereo.calculate_depth()
        depth = cv.applyColorMap(depth, cv.COLORMAP_JET)
        depth = cv.cvtColor(depth, cv.COLOR_BGR2RGB)

        if self.render_depth:
            bytes_stream = io.BytesIO()
            PIL.Image.fromarray(depth).save(bytes_stream, format="jpeg")
            self.widgets[0].value = bytes_stream.getvalue()

        if self.render_preview:
            bytes_stream = io.BytesIO()
            PIL.Image.fromarray(self.cameras.frames[0]).save(bytes_stream,
                                                             format="jpeg")
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


class NDepthStreamExt(NDepthStream):
    def __init__(self, cameras, stereo, sep_thread=True, render_depth=True,
                 render_preview=False):
        super().__init__(cameras, stereo, sep_thread, render_depth,
                         render_preview)
        self.ext_params = {}
        self.widgets_ext = {
            "setBlockSize": (
                ipywidgets.IntSlider(min=5, max=99, step=2),
                lambda: self.stereo.stereo.getBlockSize(),
                lambda v: self.stereo.stereo.setBlockSize(v["new"])
            ),
            "setMinDisparity": (
                ipywidgets.IntSlider(min=-8, max=256, step=1),
                lambda: self.stereo.stereo.getMinDisparity(),
                lambda v: self.stereo.stereo.setMinDisparity(v["new"])
            ),
            "setNumDisparities": (
                ipywidgets.IntSlider(min=16, max=256, step=16),
                lambda: self.stereo.stereo.getNumDisparities(),
                lambda v: self.stereo.stereo.setNumDisparities(v["new"])
            ),
            # "setDisp12MaxDiff":(
            #     ipywidgets.IntSlider(min=-8, max=256, step=1),
            #     lambda: self.stereo.stereo.getDisp12MaxDiff(),
            #     lambda v: self.stereo.stereo.setDisp12MaxDiff(v["new"])
            # ),
            "setSpeckleRange": (
                ipywidgets.IntSlider(min=-8, max=256, step=1),
                lambda: self.stereo.stereo.getSpeckleRange(),
                lambda v: self.stereo.stereo.setSpeckleRange(v["new"])
            ),
            "setSpeckleWindowSize": (
                ipywidgets.IntSlider(min=-8, max=512, step=1),
                lambda: self.stereo.stereo.getSpeckleWindowSize(),
                lambda v: self.stereo.stereo.setSpeckleWindowSize(v["new"])
            ),
            "setTextureThreshold": (
                ipywidgets.IntSlider(min=0, max=512, step=1),
                lambda: self.stereo.stereo.getTextureThreshold(),
                lambda v: self.stereo.stereo.setTextureThreshold(v["new"])
            ),
            "setPreFilterCap": (
                ipywidgets.IntSlider(min=1, max=63, step=1),
                lambda: self.stereo.stereo.getPreFilterCap(),
                lambda v: self.stereo.stereo.setPreFilterCap(v["new"])
            ),
            "setPreFilterSize": (
                ipywidgets.IntSlider(min=5, max=255, step=2),
                lambda: self.stereo.stereo.getPreFilterSize(),
                lambda v: self.stereo.stereo.setPreFilterSize(v["new"])
            ),
            "setPreFilterType": (
                ipywidgets.Dropdown(
                    options=(("PREFILTER_NORMALIZED_RESPONSE", 0), ("PREFILTER_XSOBEL", 1))),
                lambda: self.stereo.stereo.getPreFilterType(),
                lambda v: self.stereo.stereo.setPreFilterType(v["new"])
            ),
            "setSmallerBlockSize": (
                ipywidgets.IntSlider(min=-1005, max=255, step=2),
                lambda: self.stereo.stereo.getSmallerBlockSize(),
                lambda v: self.stereo.stereo.setSmallerBlockSize(v["new"])
            ),
            # "setSpekleRemovalTechnique":(
            #     ipywidgets.IntSlider(min=-1005, max=255, step=2),
            #     lambda: self.stereo.stereo.getSpekleRemovalTechnique(),
            #     lambda v: self.stereo.stereo.setSpekleRemovalTechnique(v["new"])
            # ),
            "setUniquenessRatio": (
                ipywidgets.IntSlider(min=0, max=128, step=2),
                lambda: self.stereo.stereo.getUniquenessRatio(),
                lambda v: self.stereo.stereo.setUniquenessRatio(v["new"])
            ),
            # "setUsePrefilter":(
            #     ipywidgets.Dropdown(options=(("TRUE", 1),("FALSE", 0))),
            #     lambda: self.stereo.stereo.getUsePrefilter(),
            #     lambda v: self.stereo.stereo.setUsePrefilter(v["new"])
            # ),
        }

    def get_ext_params(self):
        params = {}
        for name, (_, value_fn, _) in self.widgets_ext.items():
            params[name] = value_fn()
        return params

    def save_ext_params(self, filename):
        logging.info("Saving depth map parameters to {}.".format(filename))
        params = self.get_ext_params()
        with open(filename, "w") as file:
            _ = yaml.dump(params, file)
        return params

    def start(self):
        for name, (widget, value_fn, fn) in self.widgets_ext.items():
            widget.disabled = False
            widget.description = name + str(":\t")
            if self.ext_params.get(name) is None:
                widget.value = value_fn()
            else:
                widget.value = self.ext_params[name]
            widget.observe(fn, "value")
            widget.layout = ipywidgets.Layout(width="500px")
            widget.style = {"description_width": "initial"}
            IPython.display.display(widget)
        super().start()

    def _cleanup(self, cameras):
        super()._cleanup(cameras)
        for _, (widget, _, _) in self.widgets_ext.items():
            widget.disabled = True

    def stop(self):
        super().stop()
        return self.get_ext_params()
