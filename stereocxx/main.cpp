#include <iostream>
#include <fstream>
#include <ctime>
#include <cmath>
#include <thread>

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
    info("Program is starting.");
    info("Debug printing: " + std::to_string(DEBUG));
    info("Number of concurrent threads supported by the implementation: " + std::to_string(std::thread::hardware_concurrency()));
    CalibParams2Cams calib("../calibrated/2cam-usb-12cm-v1.json");

    auto cams = Cameras({ 0, 1, 2, 3, 4, 5, 6 });
    while (1);

    //while (1) {
    //    cams.capture();
    //    cv::imshow("0", cams.frame(0));
    //    // cv::imshow("1", cams.frame(1));
    //    if (cv::waitKey(1) == 'q') break;
    //}
    //cv::destroyWindow("0");
    // cv::destroyWindow("1");

    return 0;
}
