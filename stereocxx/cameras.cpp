#include <opencv2/videoio.hpp>
#include <thread>
#include "misc.h"
#include "cameras.h"

//CameraThread::CameraThread(int source, unsigned width, unsigned height, unsigned fps, int mode) {
//	info("Initializing camera from source: " + std::to_string(source));
//	_mat = cv::Mat(height, width, CV_8UC3);
//	_status = true;
//	_status = _cam.open(source);
//	if (!_status) {
//		error("Unable to create camera from source: " + std::to_string(source) + ".");
//		return;
//	}
//	_threads[i] = std::thread(&loop, i);
//	set_prop(cv::CAP_PROP_FRAME_WIDTH, width);
//	set_prop(cv::CAP_PROP_FRAME_HEIGHT, height);
//	set_prop(cv::CAP_PROP_FPS, fps);
//}
//
//CameraThread::CameraThread(std::string source, unsigned width, unsigned height, unsigned fps, int mode) {
//
//}
//
//std::atomic<cv::Mat>& CameraThread::get_mat() {
//	
//}
//
//std::chrono::time_point<std::chrono::high_resolution_clock>& CameraThread::get_next_cap() {
//
//}

void Cameras::loop(size_t no) {
	using namespace std::chrono_literals;

	while (1) {
		std::unique_lock<std::mutex> lock(_cond_mutex);
		info(std::to_string(no));
		_cond.wait(lock, [this, no] { return false; });
	}
	//while (1) {
		//std::unique_lock<std::mutex> lock(_mutexes[no]);
		//_cond.wait(lock);

		//auto t0 = _clock.now();
		////std::this_thread::sleep_for(1s); // This is not a precise solution
		//auto t1 = _clock.now();
		//bool ret;
		//for (int i = 0; i < 10; i++)
		//	ret = _cams[no].read(_frames[no]);
		//_status[no] = ret;
		//auto t2 = _clock.now();
		//
		//std::chrono::duration<double, std::milli> wait_time = t1 - t0;
		//std::chrono::duration<double, std::milli> read_time = t2 - t1;
		//if (ret) debuginfo("Frame successfully read from camera no " + std::to_string(no) + ", wait time: "
		//	+ std::to_string(wait_time.count()) + "ms, read time: " + std::to_string(read_time.count()) + "ms.");
		//else debuginfo("Unable to read from camera no " + std::to_string(no) + ".");


		//lock.unlock();
		//_cond.notify_one();
	//}
}

Cameras::Cameras(std::vector<int> sources, unsigned width, unsigned height, unsigned fps,
	int mode) {
	info("Initializing cameras.");
	_size = sources.size();
	_cams.resize(_size);
	_status.resize(_size, true);
	_frames.resize(_size);
	_threads.resize(_size);
	for (int i = 0; i < _size; i++) {
		_frames[i] = cv::Mat(height, width, CV_8UC3);
		_status[i] = _cams[i].open(sources[i]);
		if (!_status[i]) {
			error("Unable to create camera " + std::to_string(sources[i]) + ".");
			continue;
		}
	}
	set_prop(cv::CAP_PROP_FRAME_WIDTH, width);
	set_prop(cv::CAP_PROP_FRAME_HEIGHT, height);
	set_prop(cv::CAP_PROP_FPS, fps);

	_clock.now();
	for (int i = 0; i < _size; i++) {
		_threads[i] = std::thread(&Cameras::loop, this, i);
	}
}

Cameras::~Cameras() {
	for (int i = 0; i < _size; i++) {
	}
}

bool Cameras::capture() {
	bool ret = true;

	//for (int i = 0; i < _size; i++) {
	//	_status[i] = _cams[i].grab();
	//	ret &= _status[i];
	//	if (!_status[i]) {
	//		error("Unable to grab image from camera no " + std::to_string(i) + ".");
	//	}
	//}
	//
	//for (int i = 0; i < _size; i++) {
	//	if (_status[i]) {
	//		_status[i] = _cams[i].retrieve(_frames[i]);
	//		ret &= _status[i];
	//		if (!_status[i]) {
	//			error("Unable to retrieve image from camera no " + std::to_string(i) + ".");
	//		}
	//	}
	//}
	return ret;
}

bool Cameras::capture_black() {
	for (auto& frame : _frames) {
		frame = cv::Scalar(0, 0, 0);
	}
	return true;
}

cv::VideoCapture& Cameras::cam(size_t no) {
	return _cams[no];
}

cv::Mat& Cameras::frame(size_t no) {
	return _frames[no];
}

size_t Cameras::size() const {
	return _size;
}

void Cameras::set_prop(int prop_id, double value) {
	for (int i = 0; i < _size; i++) {
		if (!_status[i])
			continue;

		info("Setting camera no " + std::to_string(i) + " property "
			+ std::to_string(prop_id) + " to " + std::to_string(value) + ".");
		_status[i] = _cams[i].set(prop_id, value);
		if (!_status[i]) {
			error("Unable to set camera no " + std::to_string(i) + " property "
				+ std::to_string(prop_id) + " to " + std::to_string(value) + ".");
			continue;
		}
	}
}

