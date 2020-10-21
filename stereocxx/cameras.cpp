#include <opencv2/videoio.hpp>
#include "cameras.h"

Cameras::Cameras(std::initializer_list<std::string> sources,
	unsigned width,
	unsigned height,
	unsigned fps,
	int mode) 
{
	for (auto source : sources) {
		_cams.push_back(cv::VideoCapture(source));
		init(_cams.back());
	}
	_width = width;
	_height = height;
	_fps = fps;
	_mode = mode;
}

Cameras::Cameras(std::initializer_list<int> sources,
	unsigned width,
	unsigned height,
	unsigned fps,
	int mode)
{
	for (auto source : sources) {
		_cams.push_back(cv::VideoCapture(source));
		init(_cams.back());
	}
	_width = width;
	_height = height;
	_fps = fps;
	_mode = mode;
}

bool Cameras::init(cv::VideoCapture & cam) {
	cam.set(cv::CAP_PROP_FRAME_WIDTH, _width);
	cam.set(cv::CAP_PROP_FRAME_HEIGHT, _height);
	cam.set(cv::CAP_PROP_FPS, _fps);
}
