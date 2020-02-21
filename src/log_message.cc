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


#include <iostream>
#include <string>

class MyException : public std::exception
{
public:
    MyException(const std::string& msg) : m_msg(msg)
    {
        std::cout << "MyException::MyException - set m_msg to:" << m_msg << std::endl;
    }

   ~MyException()
   {
        std::cout << "MyException::~MyException" << std::endl;
   }

   virtual const char* what() const throw ()
   {
        std::cout << "MyException - what" << std::endl;
        return m_msg.c_str();
   }

   const std::string m_msg;
};


throw (MyException(std::string("MyException thrown"));
