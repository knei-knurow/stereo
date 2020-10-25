#include <opencv2/core.hpp>
#include <fstream>
#include <json.hpp>
#include <iostream>
#include "calibration.h"
#include "misc.h"

using nlohmann::json;

CalibParams2Cams::CalibParams2Cams(std::string filename) {
	info("Loading calibration parameters from '" + filename + "'.");
	std::ifstream file(filename);
	if (!file) {
		error("Unable to open '" + filename + "'. Calibration has not been loaded.");
		return;
	}
	json js;
	try {
		file >> js;
	}
	catch (json::exception& e) {
		error("Unable to parse '" + filename + "':" + e.what() + ". Calibration has not been loaded.");
		return;
	}
	info("Calibration has been loaded.");
	try {
		width = js["width"].get<unsigned>();
		height = js["height"].get<unsigned>();

		json_to_cv_mat(js["left_dist_coeff"], left_dist_coeff);
		json_to_cv_mat(js["left_matrix"], left_matrix);
		json_to_cv_mat(js["left_proj"], left_proj);
		json_to_cv_mat(js["left_rectif"], left_rectif);
		json_to_cv_rect(js["left_roi"], left_roi);
		left_reprojection_error = js["left_reprojection_error"].get<double>();

		json_to_cv_mat(js["right_dist_coeff"], right_dist_coeff);
		json_to_cv_mat(js["right_matrix"], right_matrix);
		json_to_cv_mat(js["right_proj"], right_proj);
		json_to_cv_mat(js["right_rectif"], right_rectif);
		json_to_cv_rect(js["right_roi"], right_roi);
		right_reprojection_error = js["right_reprojection_error"].get<double>();

		json_to_cv_mat(js["both_rot_matrix"], both_rot_matrix);
		json_to_cv_mat(js["both_trans_vec"], both_trans_vec);

	}
	catch (json::type_error& e) {
		std::cout << e.what() << std::endl;
		return;
	}

	// If everything is ok
	calibrated = true;
}

void CalibParams::json_to_cv_mat(const json& js, cv::Mat& mat) {
	auto v = js.get<std::vector<std::vector<double>>>();
	mat = cv::Mat(v.size(), v.at(0).size(), CV_64FC1);
	for (int i = 0; i < mat.rows; ++i)
		for (int j = 0; j < mat.cols; ++j)
			mat.at<double>(i, j) = v.at(i).at(j);
}

void CalibParams::json_to_cv_rect(const json& js, cv::Rect& rect) {
	auto v = js.get<std::vector<int>>();
	rect = cv::Rect(v[0], v[1], v[2], v[3]);
}