#include <iostream>
#include <fstream>
#include <ctime>
#include <cmath>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>

#include <opencv2/core/cuda.hpp>
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudaimgproc.hpp>

#include <json.hpp>

#include "calibration.h"
#include "misc.h"
#include "cameras.h"

using nlohmann::json;

int main() {
    info("Program is starting.", "main");

    auto cams = Cameras({ 0 });
    cams.capture();

    return 0;
}