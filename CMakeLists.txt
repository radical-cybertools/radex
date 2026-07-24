cmake_minimum_required(VERSION 3.13)

# Policy for VERSION in project()
if (POLICY CMP0048)
    cmake_policy(SET CMP0048 NEW)
endif (POLICY CMP0048)

include(${CMAKE_CURRENT_LIST_DIR}/cmake/radex-version.cmake)

project(radex VERSION ${RADEX_VERSION} LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_VISIBILITY_PRESET default)

# Default build type
if(NOT DEFINED CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

# Set install prefix
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
    set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/install)
endif()

# Include GNU install directories
include(GNUInstallDirs)

# ============================================================================
# Options
# ============================================================================
include(${CMAKE_CURRENT_LIST_DIR}/cmake/radex-options.cmake)
radex_define_root_options()

# ============================================================================
# Find required packages
# ============================================================================
find_package(Threads REQUIRED)
include(${CMAKE_CURRENT_LIST_DIR}/cmake/radex-backends.cmake)
radex_find_backends()

if(BUILD_EXAMPLES)
    add_subdirectory(example)
endif()

if(BUILD_SHARED_LIBS OR BUILD_STATIC_LIBS)
    add_subdirectory(src)
endif()

if(BUILD_TESTS)
    add_subdirectory(tests/cpp)
endif()