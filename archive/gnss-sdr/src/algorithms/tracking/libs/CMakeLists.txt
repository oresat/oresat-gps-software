# Copyright (C) 2012-2018  (see AUTHORS file for a list of contributors)
#
# This file is part of GNSS-SDR.
#
# GNSS-SDR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GNSS-SDR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GNSS-SDR. If not, see <https://www.gnu.org/licenses/>.
#


set(TRACKING_LIB_SOURCES
    cpu_multicorrelator.cc
    cpu_multicorrelator_real_codes.cc
    cpu_multicorrelator_16sc.cc
    lock_detectors.cc
    tcp_communication.cc
    tcp_packet_data.cc
    tracking_2nd_DLL_filter.cc
    tracking_2nd_PLL_filter.cc
    tracking_discriminators.cc
    tracking_FLL_PLL_filter.cc
    tracking_loop_filter.cc
    dll_pll_conf.cc
    bayesian_estimation.cc
)

set(TRACKING_LIB_HEADERS
    cpu_multicorrelator.h
    cpu_multicorrelator_real_codes.h
    cpu_multicorrelator_16sc.h
    lock_detectors.h
    tcp_communication.h
    tcp_packet_data.h
    tracking_2nd_DLL_filter.h
    tracking_2nd_PLL_filter.h
    tracking_discriminators.h
    tracking_FLL_PLL_filter.h
    tracking_loop_filter.h
    dll_pll_conf.h
    bayesian_estimation.h
)


include_directories(
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/src/core/system_parameters
    ${CMAKE_SOURCE_DIR}/src/core/interfaces
    ${CMAKE_SOURCE_DIR}/src/core/receiver
    ${CMAKE_SOURCE_DIR}/src/algorithms/libs
    ${ARMADILLO_INCLUDE_DIRS}
    ${VOLK_INCLUDE_DIRS}
    ${GLOG_INCLUDE_DIRS}
    ${GFlags_INCLUDE_DIRS}
    ${OPT_TRACKING_INCLUDES}
    ${VOLK_GNSSSDR_INCLUDE_DIRS}
)

if(ENABLE_GENERIC_ARCH)
    add_definitions(-DGENERIC_ARCH=1)
endif()

if(SSE3_AVAILABLE)
    add_definitions(-DHAVE_SSE3=1)
endif()

list(SORT TRACKING_LIB_HEADERS)
list(SORT TRACKING_LIB_SOURCES)

add_library(tracking_lib ${TRACKING_LIB_SOURCES} ${TRACKING_LIB_HEADERS})

source_group(Headers FILES ${TRACKING_LIB_HEADERS})

target_link_libraries(tracking_lib
    ${OPT_TRACKING_LIBRARIES}
    ${VOLK_LIBRARIES}
    ${VOLK_GNSSSDR_LIBRARIES}
    ${Boost_LIBRARIES}
    ${GNURADIO_RUNTIME_LIBRARIES}
)

if(VOLKGNSSSDR_FOUND)
    add_dependencies(tracking_lib glog-${glog_RELEASE})
else()
    add_dependencies(tracking_lib glog-${glog_RELEASE} volk_gnsssdr_module)
endif()
