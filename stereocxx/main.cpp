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

#include <opencv2/photo.hpp>

#include <json.hpp>

#include "calibration.h"
#include "misc.h"
#include "cameras.h"
#include "depth-map.h"

using nlohmann::json;

void load(cv::Mat& left, cv::Mat& right) {
    // left = cv::imread("../test-images/left/ksiazki.jpg", cv::IMREAD_GRAYSCALE);
    // right = cv::imread("../test-images/right/ksiazki.jpg", cv::IMREAD_GRAYSCALE);
    left = cv::imread("../test-images/left/ksiazki.jpg");
    right = cv::imread("../test-images/right/ksiazki.jpg");
}

void on_t0(int v, void*) {
    std::cout << v << std::endl;
}

void on_t1(int v, void*) {
    std::cout << v << std::endl;
}

void on_t2(int v, void*) {
    std::cout << v << std::endl;
}

void on_t3(int v, void*) {
    std::cout << v << std::endl;
}

int main() {
    info("Program is starting.");
    info("Debug printing: " + std::to_string(DEBUG));
    info("Number of concurrent threads supported by the implementation: " + std::to_string(std::thread::hardware_concurrency()));
    CalibParams2Cams calib("../calibrated/2cam-usb-12cm-v1.json");

    // auto cams = Cameras({ 0, 1 });
    cv::Mat depth, left, right, left_s, right_s, depth_s;
    StereoVision2Cams stereo(calib);

    int t0 = 3, t1 = 7, t2 = 21, t3 = 0;

    while (1) {
        load(left, right);

        cv::fastNlMeansDenoisingColored(left, left, double(t0), double(t1), double(t2));
        cv::fastNlMeansDenoisingColored(right, right, double(t0), double(t1), double(t2));
        cv::cvtColor(left, left, cv::COLOR_BGR2GRAY);
        cv::cvtColor(right, right, cv::COLOR_BGR2GRAY);
        // cv::fastNlMeansDenoising(left, left, double(t0), double(t1), double(t2));
        // cv::fastNlMeansDenoising(right, right, double(t0), double(t1), double(t2));

        stereo.calculate_depth(left, right, depth);
        cv::applyColorMap(depth, depth, cv::COLORMAP_JET);

        cv::resize(left, left_s, cv::Size(640, 480));
        cv::resize(right, right_s, cv::Size(640, 480));
        cv::resize(depth, depth_s, cv::Size(640, 480));
        std::cout << "---" << t0 << std::endl;
        cv::imshow("0", left);
        cv::imshow("depth", depth_s);
        cv::createTrackbar("0", "depth", &t0, 100, on_t0);
        cv::createTrackbar("1", "depth", &t1, 100, on_t1);
        cv::createTrackbar("2", "depth", &t2, 100, on_t2);
        cv::createTrackbar("3", "depth", &t3, 100, on_t3);
        if (cv::waitKey(0) == 'q') break;
    }
    cv::imwrite("fastNlMeansDenoising-0.png", depth);
    cv::imwrite("fastNlMeansDenoising-0-left.png", left);
    cv::imwrite("fastNlMeansDenoising-0-right.png", right);
    cv::destroyAllWindows();

    return 0;
}
