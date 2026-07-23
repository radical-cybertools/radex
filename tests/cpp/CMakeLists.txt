cmake_minimum_required(VERSION 3.13)
project(RaDex-Tests-Cpp)
enable_language(CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_VISIBILITY_PRESET default)


# RaDex ======================================================================
# TODO: Leaving this for Andrew to fix
find_package(RaDex REQUIRED)
# ============================================================================

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
target_link_libraries(tests PRIVATE RaDex)
target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)
