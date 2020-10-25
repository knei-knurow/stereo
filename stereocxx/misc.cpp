#include <sstream>
#include <iostream>
#include <fstream>
#include <iomanip>
#include <chrono>
#include "misc.h"

const std::string& log(const std::string& msg,
	const std::string& source, LogLevel level) {
	
	// Displaying time
	tm localTime;
	std::chrono::system_clock::time_point t = std::chrono::system_clock::now();
	time_t now = std::chrono::system_clock::to_time_t(t);
	localtime_s(&localTime, &now);
	const std::chrono::duration<double> tse = t.time_since_epoch();
	std::chrono::seconds::rep milliseconds = std::chrono::duration_cast<std::chrono::milliseconds>(tse).count() % 1000;
	std::stringstream stream;

	stream << std::setfill('0') << std::setw(2) << localTime.tm_mday << '/'
		<< std::setfill('0') << std::setw(2) << (localTime.tm_mon + 1) << '/'
		<< (1900 + localTime.tm_year) << ' '
		<< std::setfill('0') << std::setw(2) << localTime.tm_hour << ':'
		<< std::setfill('0') << std::setw(2) << localTime.tm_min << ':'
		<< std::setfill('0') << std::setw(2) << localTime.tm_sec << '.'
		<< std::setfill('0') << std::setw(3) << milliseconds
		<< ' ';

	// Displaying source
	if (!source.empty()) {
		stream << source << ' ';
	}

	// Displaying level
	if (level == INFO) stream << "INFO";
	else if (level == WARNING) stream << "WARNING";
	else if (level == ERROR) stream << "ERROR";
	else if (level == CRITICAL) stream << "CRITICAL";
	
	// Displaying message
	stream << ": " << msg;

	// Emit
	std::cout << stream.str() << std::endl;

	std::ofstream logfile("../logs/log.log", std::ios_base::app);
	if (logfile) logfile << stream.str() << std::endl;
	logfile.close();

	return msg;
}

const std::string& info(const std::string& msg,
	const std::string& source) {
	return log(msg, source, INFO);
}

const std::string& warning(const std::string& msg,
	const std::string& source) {
	return log(msg, source, WARNING);
}

const std::string& error(const std::string& msg,
	const std::string& source) {
	return log(msg, source, ERROR);
}

const std::string& critical(const std::string& msg,
	const std::string& source) {
	return log(msg, source, CRITICAL);
}