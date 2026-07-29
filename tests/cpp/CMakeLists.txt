cmake_minimum_required(VERSION 3.13)

include(${CMAKE_CURRENT_LIST_DIR}/../../cmake/radex-standalone.cmake)

if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
  include(${CMAKE_CURRENT_LIST_DIR}/../../cmake/radex-version.cmake)
  project(RADEX-Tests
    VERSION ${RADEX_VERSION}
    LANGUAGES CXX
  )
endif()

radex_setup_standalone_build(
    OPTIONS_FUNCTION radex_define_example_options
    FIND_INSTALLED_RADEX
    FIND_BACKENDS
)

# Catch2 =====================================================================
Include(FetchContent)
FetchContent_Declare(
  Catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG        v3.8.1
)
FetchContent_MakeAvailable(Catch2)

# Compile test executable
add_executable(tests test_local_client.cpp)
radex_set_target_install_rpath(
  tests
  smartredis
  dragon
  Catch2::Catch2
  Catch2::Catch2Main
)
target_link_libraries(tests PRIVATE radex::radex)
target_link_libraries(tests PRIVATE Catch2::Catch2WithMain)
install(
    TARGETS tests
    DESTINATION ${CMAKE_INSTALL_BINDIR}/tests
)
