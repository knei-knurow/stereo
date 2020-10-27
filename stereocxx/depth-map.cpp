#include <vector>
#include <opencv2/core.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/cudaimgproc.hpp>
#include "calibration.h"
#include "depth-map.h"

StereoVision2Cams::StereoVision2Cams(const CalibParams2Cams& calib) 
	: _calib(calib) {
	_stereo = cv::StereoBM::create(16, 9);

	cv::initUndistortRectifyMap(
		_calib.left_matrix,
		_calib.left_dist_coeff,
		_calib.left_rectif,
		_calib.left_proj,
		cv::Size(_calib.width, _calib.height),
		CV_32FC1,
		_left_map_x, _left_map_y);

	cv::initUndistortRectifyMap(
		_calib.right_matrix,
		_calib.right_dist_coeff,
		_calib.right_rectif,
		_calib.right_proj,
		cv::Size(_calib.width, _calib.height),
		CV_32FC1,
		_right_map_x, _right_map_y);

	_stereo->setBlockSize(21);
	_stereo->setMinDisparity(4);
	_stereo->setNumDisparities(128);
	_stereo->setSpeckleRange(16);
	_stereo->setSpeckleWindowSize(45);
	_stereo->setTextureThreshold(10);
	_stereo->setPreFilterCap(31);
	_stereo->setPreFilterSize(9);
	_stereo->setPreFilterType(0);
	_stereo->setSmallerBlockSize(0);
	_stereo->setUniquenessRatio(15);
}

void StereoVision2Cams::calculate_depth(cv::Mat& left, cv::Mat& right, cv::Mat& depth) {
	cv::remap(left, left, _left_map_x, _left_map_y, cv::INTER_LINEAR);
	cv::remap(right, right, _right_map_x, _right_map_y, cv::INTER_LINEAR);
	_stereo->compute(left, right, depth);
	depth.convertTo(depth, CV_8UC1, 255.0 / 2048.0, 0);
}