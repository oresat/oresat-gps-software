#include "log_message.h"
#include <iostream>
#include <syslog.h>
#include <cstdarg>

void log_message(int priority, const char *fmt, ...) {
	va_list args;
	va_start(args, fmt);
	vsyslog(priority, fmt, args);
	vfprintf((priority > LOG_WARNING ? stdout : stderr), fmt, args);
	va_end(args);
}

