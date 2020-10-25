#pragma once
#include <string>

enum LogLevel {
	INFO,
	WARNING,
	ERROR,
	CRITICAL,
};

const std::string& log(const std::string& msg,
	const std::string& source = "", LogLevel level = INFO);

const std::string& info(const std::string& msg, 
	const std::string& source = "");

const std::string& warning(const std::string& msg, 
	const std::string& source = "");

const std::string& error(const std::string& msg, 
	const std::string& source = "");

const std::string& critical(const std::string& msg, 
	const std::string& source = "");