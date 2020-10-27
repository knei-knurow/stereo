#pragma once
#include <vector>
#include <opencv2/core.hpp>
#include <opencv2/cudastereo.hpp>
#include <opencv2/stereo.hpp>
#include "calibration.h"

class StereoVision {
public:
	virtual void calculate_depth(cv::Mat& left, cv::Mat& right, cv::Mat& depth) = 0;
};

class StereoVision2Cams
	: public StereoVision {
public:
	StereoVision2Cams(const CalibParams2Cams& calib);

	virtual void calculate_depth(cv::Mat& left, cv::Mat& right, cv::Mat& depth);

private:
	CalibParams2Cams _calib;
	cv::Mat _left_map_x;
	cv::Mat _left_map_y;
	cv::Mat _right_map_x;
	cv::Mat _right_map_y;
	cv::Ptr<cv::StereoBM> _stereo;
};

