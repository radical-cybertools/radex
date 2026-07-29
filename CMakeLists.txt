cmake_minimum_required(VERSION 3.13)

# Policy for VERSION in project()
if (POLICY CMP0048)
    cmake_policy(SET CMP0048 NEW)
endif (POLICY CMP0048)

include(${CMAKE_CURRENT_LIST_DIR}/cmake/radex-version.cmake)
project(radex VERSION ${RADEX_VERSION} LANGUAGES CXX)

include(${CMAKE_CURRENT_LIST_DIR}/cmake/radex-standalone.cmake)

radex_setup_standalone_build(
    OPTIONS_FUNCTION radex_define_root_options
    ENABLE_LANGUAGE_SUPPORT
    FIND_THREADS
    FIND_BACKENDS
)

# ============================================================================
# Options
# ============================================================================
if(ENABLE_CXX AND (BUILD_SHARED_LIBS OR BUILD_STATIC_LIBS))
    add_subdirectory(src)
endif()

if(BUILD_EXAMPLES)
    add_subdirectory(example)
endif()

if(BUILD_TESTS)
    add_subdirectory(tests/cpp)
endif()