#pragma once
#include <string>

enum LogLevel {
	DEBUG,
	INFO,
	WARNING,
	ERROR,
	CRITICAL,
};

const std::string& log(const std::string& msg, LogLevel level = INFO);

#ifdef _DEBUG
	#define debuginfo(msg) log(msg, DEBUG)
#else
	#define debuginfo do {} while (0)
#endif

const std::string& info(const std::string& msg);
const std::string& warning(const std::string& msg);
const std::string& error(const std::string& msg);
const std::string& critical(const std::string& msg);