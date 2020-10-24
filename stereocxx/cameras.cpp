#include <opencv2/videoio.hpp>
#include "cameras.h"

Cameras::Cameras(std::vector<int> sources,
	unsigned width,
	unsigned height,
	unsigned fps,
	int mode)
{
	_width = width;
	_height = height;
	_fps = fps;
	_mode = mode;
	_cams.resize(sources.size());
	_status.resize(sources.size(), true);
	_frames.resize(sources.size(), cv::Mat(_height, _width, CV_8UC3));
	for (int i = 0; i < sources.size(); i++) {
		_status[i] = _cams[i].open(sources[i]);
		if (_status[i]) _status[i] = _cams.back().set(cv::CAP_PROP_FRAME_WIDTH, _width);
		if (_status[i]) _status[i] = _cams.back().set(cv::CAP_PROP_FRAME_HEIGHT, _height);
		if (_status[i]) _status[i] = _cams.back().set(cv::CAP_PROP_FPS, _fps);
	}
}

bool Cameras::capture() {
	bool ret = true;

	for (int i = 0; i < _cams.size(); i++) {
		_status[i] = _cams[i].grab();
		ret &= _status[i];
	}
	
	for (int i = 0; i < _cams.size(); i++) {
		if (_status[i]) {
			_status[i] = _cams[i].retrieve(_frames[i]);
			ret &= _status[i];
		}
	}
	return ret;
}

bool Cameras::capture_black() {
	for (auto& frame : _frames) {
		frame = cv::Scalar(0, 0, 0);
	}
	return true;
}

cv::VideoCapture& Cameras::cam(size_t no) {
	return _cams[no];
}

