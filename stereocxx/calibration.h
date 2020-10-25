#pragma once
#include <opencv2/core.hpp>
#include <vector>
#include <array>
#include <json.hpp>

using nlohmann::json;

struct CalibParams {
	bool calibrated = false;
	unsigned width = 0;
	unsigned height = 0;

protected:
	void json_to_cv_mat(const json& js, cv::Mat& mat);
	void json_to_cv_rect(const json& js, cv::Rect& rect);
};

struct CalibParams2Cams 
	: public CalibParams {
	cv::Mat left_dist_coeff = cv::Mat();
	cv::Mat left_matrix = cv::Mat();
	cv::Mat left_proj = cv::Mat();
	cv::Mat left_rectif = cv::Mat();
	cv::Rect left_roi = cv::Rect();
	double left_reprojection_error = 0;

	cv::Mat right_dist_coeff = cv::Mat();
	cv::Mat right_matrix = cv::Mat();
	cv::Mat right_proj = cv::Mat();
	cv::Mat right_rectif = cv::Mat();
	cv::Rect right_roi = cv::Rect();
	double right_reprojection_error = 0;

	cv::Mat both_rot_matrix = cv::Mat();
	cv::Mat both_trans_vec = cv::Mat();

	CalibParams2Cams(std::string filename);
};