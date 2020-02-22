cmake_minimum_required(VERSION 3.13 FATAL_ERROR)
project(oresat-gps CXX)


##############################################################################
# Release vs debug modes (set CXXFLAGS, LDFLAGS, etc)
# to use: cmake -DCMAKE_BUILD_TYPE=Debug .

include(CheckCXXCompilerFlag)
CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
if(COMPILER_SUPPORTS_CXX11)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
else()
    message(SEND_ERROR "The compiler ${CMAKE_CXX_COMPILER} doesnt support C++11.")
endif()


# default to release
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall")
set(CMAKE_CXX_FLAGS_DEBUG "-g")
set(CMAKE_CXX_FLAGS_RELEASE "-O3")
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
set(SGP4_DIR src/sgp4/libsgp4)

# add all headers in source directories
include_directories(${SRC_DIR})
include_directories(${SGP4_DIR})

set(SOURCE_FILES
    ${SRC_DIR}/main.cc
    ${SRC_DIR}/controller.cc
    ${SRC_DIR}/log_message.cc
    ${SGP4_DIR}/CoordGeodetic.cc
    ${SGP4_DIR}/CoordTopocentric.cc
    ${SGP4_DIR}/DateTime.cc
    ${SGP4_DIR}/DecayedException.cc
    ${SGP4_DIR}/Eci.cc
    ${SGP4_DIR}/Globals.cc
    ${SGP4_DIR}/Observer.cc
    ${SGP4_DIR}/OrbitalElements.cc
    ${SGP4_DIR}/SatelliteException.cc
    ${SGP4_DIR}/SGP4.cc
    ${SGP4_DIR}/SolarPosition.cc
    ${SGP4_DIR}/TimeSpan.cc
    ${SGP4_DIR}/Tle.cc
    ${SGP4_DIR}/TleException.cc
    ${SGP4_DIR}/Util.cc
    ${SGP4_DIR}/Vector.cc
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
install(TARGETS oresat-gps DESTINATION /usr/bin)

# Daemon service file
install(FILES oresat-gpsd.service DESTINATION /lib/systemd/system)

# DBus config file
install(FILES org.OreSat.GPS.conf DESTINATION /usr/share/dbus-1/system.d)

