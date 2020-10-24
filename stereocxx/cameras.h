#pragma once
#include <string>
#include <vector>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>

class Cameras {
public:
	Cameras(std::vector<int> sources = {},
		unsigned width = 1280,
		unsigned height = 1024,
		unsigned fps = 30,
		int mode = 0);

	bool capture();
	bool capture_black();

	cv::VideoCapture& cam(size_t no);

private:
	unsigned _width;
	unsigned _height;
	unsigned _fps;
	int _mode;

	std::vector<cv::VideoCapture> _cams;
	std::vector<cv::Mat> _frames;
	std::vector<bool> _status;
};