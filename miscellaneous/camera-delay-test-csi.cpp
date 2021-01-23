#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <iostream>
#include <chrono>

int main() {
	std::chrono::steady_clock::time_point t0, t1, t2;
	cv::VideoCapture cam0("nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)120/1 ! nvvidconv ! video/x-raw, width=(int)1280, height=(int)720, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"),
		         cam1("nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=(int)1280, height=(int)720, format=(string)NV12, framerate=(fraction)120/1 ! nvvidconv ! video/x-raw, width=(int)1280, height=(int)720, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink");
	cv::Mat img0, img1;
	bool ok0 = 1, ok1 = 1;

	//cv::namedWindow("0");
	//cv::namedWindow("1");
	int I = 0;
	std::cout << "Camera test start\n";
	while (true) {
		t0 = std::chrono::steady_clock::now();
		ok0 = cam1.grab();
		t1 = std::chrono::steady_clock::now();
		ok1 = cam0.grab();
		t2 = std::chrono::steady_clock::now();

		std::cout << "0 CAMERA TIME: "
			<< std::chrono::duration_cast<std::chrono::microseconds>(t1 - t0).count() << "us\n"
			<< "1 CAMERA TIME: "
			<< std::chrono::duration_cast<std::chrono::microseconds>(t2 - t1).count() << "us\n";

		CV_Assert(ok0 == true);
		CV_Assert(ok1 == true);

		ok0 = cam0.retrieve(img0);
		ok1 = cam1.retrieve(img1);

		CV_Assert(ok0 == true);
		CV_Assert(ok1 == true);
		
		if (I <= 1) {
			std::cin >> I;
		} else {
			I--;
		}
		//cv::imshow("0", img0);
		//cv::imshow("1", img1);
		//if ('q' == cv::waitKey(0)) break;
	}

	return 0;
}

