#pragma once
#include <initializer_list>
#include <string>
#include <vector>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>

class Cameras {
public:
	enum Interface {
		USB,
		CSI,
	};

	Cameras(std::initializer_list<std::string> sources,
		unsigned width = 1280,
		unsigned height = 1024,
		unsigned fps = 30,
		int mode = 0);
	Cameras(std::initializer_list<int> sources,
		unsigned width = 1280,
		unsigned height = 1024,
		unsigned fps = 30,
		int mode = 0);

	bool capture();
	bool capture_black();

private:
	bool init(cv::VideoCapture& cam);

	unsigned _width;
	unsigned _height;
	unsigned _fps;
	int _mode;

	std::vector<cv::VideoCapture> _cams;
	std::vector<cv::Mat> _frames;
};