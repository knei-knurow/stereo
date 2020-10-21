#include <iostream>
#include <ctime>
#include <cmath>

#include <opencv2/core.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/imgcodecs.hpp>

#include <opencv2/core/cuda.hpp>
#include <opencv2/cudaarithm.hpp>
#include <opencv2/cudaimgproc.hpp>

#include "calibration.h"
#include "cameras.h"

#define TestCUDA true

int main() {

    try {
        cv::Mat mat0;
        cv::VideoCapture camera0(0);
        camera0.set(cv::CAP_PROP_FRAME_WIDTH, 1280);
        camera0.set(cv::CAP_PROP_FRAME_HEIGHT, 1024);
        camera0.set(cv::CAP_PROP_FPS, 30);


        cv::Mat mat1;
        cv::VideoCapture camera1(1);
        camera1.set(cv::CAP_PROP_FRAME_WIDTH, 1280);
        camera1.set(cv::CAP_PROP_FRAME_HEIGHT, 1024);
        camera1.set(cv::CAP_PROP_FPS, 30);
        double fps = 0;
        while (true) {
            
            camera0.read(mat0);
            camera1.read(mat1);

            // cv::imshow("0", mat0);
            // cv::imshow("1", mat1);
            if (cv::waitKey(1) == 'q') break;
        } 
    }
    catch (const cv::Exception& ex) {
        std::cout << "Error: " << ex.what() << std::endl;
    }

    return 0;
}
