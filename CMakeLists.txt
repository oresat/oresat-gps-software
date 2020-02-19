cmake_minimum_required(VERSION 3.13 FATAL_ERROR)
project(oresat-gps CXX)


##############################################################################
# Deal with dependencies

# pthreads
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

# pkg-config
find_package(PkgConfig REQUIRED)

# libsystemd
pkg_check_modules(LIBSYSTEMD REQUIRED libsystemd)


##############################################################################
# Release vs debug modes (set CXXFLAGS, LDFLAGS, etc)
# to use: cmake -DCMAKE_BUILD_TYPE=Debug .

# default to release
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "-Wall")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")


##############################################################################
# Check if make or ninja

if(CMAKE_MAKE_PROGRAM MATCHES "make")
    set(CMAKE_MAKE_PROGRAM_PRETTY_NAME "make")
endif()
if(CMAKE_MAKE_PROGRAM MATCHES "ninja")
    set(CMAKE_MAKE_PROGRAM_PRETTY_NAME "ninja")
endif()
if(NOT CMAKE_MAKE_PROGRAM_PRETTY_NAME)
    set(CMAKE_MAKE_PROGRAM_PRETTY_NAME "${CMAKE_MAKE_PROGRAM}")
endif()


##############################################################################
# Get source files

# all paths to source directories
set(SRC_DIR src)

# add all headers in source directories
include_directories(${SRC_DIR})

set(SOURCE_FILES
    ${SRC_DIR}/main.cpp
    ${SRC_DIR}/controller.cpp
    ${SRC_DIR}/state_machine.cpp
    ${SRC_DIR}/log_message.cpp
)


##############################################################################
# Create an executable

add_executable(oresat-gps ${SOURCE_FILES})
target_link_libraries(oresat-gps ${LIBSYSTEMD_LIBRARIES} Threads::Threads)
target_include_directories(oresat-gps PUBLIC ${LIBSYSTEMD_INCLUDE_DIRS})
target_compile_options(oresat-gps PUBLIC ${LIBSYSTEMD_CFLAGS_OTHER})


############################################################
# Install

# Binaries
install(TARGETS candaemon DESTINATION /usr/bin)

# Daemon service file
install(FILES oresat-candaemon.service DESTINATION /lib/systemd/system)

# DBus config file
install(FILES org.OreSat.GPS.conf DESTINATION /usr/share/dbus-1/system.d)

