cmake_minimum_required(VERSION 3.13)
project(RaDex-Tests-Cpp)
enable_language(CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_VISIBILITY_PRESET default)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-version.cmake)

    project(RADEX-Tests
        VERSION ${RADEX_VERSION}
        LANGUAGES CXX
    )

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

    include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-options.cmake)
    radex_define_example_options()

    # Assume library was installed somewhere
    find_package(radex REQUIRED)

endif()

# Catch2 =====================================================================
Include(FetchContent)
FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v3.8.1
)
FetchContent_MakeAvailable(Catch2)
# ============================================================================

add_executable(tests test_local_client.cpp)
target_link_libraries(tests PRIVATE radex::radex)
target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)
