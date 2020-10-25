#include <fstream>
#include <json.hpp>
#include "calibration.h"

using nlohmann::json;

CalibParams2Cams::CalibParams2Cams(std::string filename) {
	std::ifstream file(filename);
	json js;
	file >> js;
	
	if (!file) {

		return;
	}

}
