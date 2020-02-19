#include <syslog.h> // so other file don't need to include this

/*
 * Logs the message in syslog and will output to stderr/stdout, if available.
 * see man vsyslog for prioprity levels
 */
void log_message(int priority, const char *fmt, ...);

