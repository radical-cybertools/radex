cmake_minimum_required(VERSION 3.13)

# Policy for VERSION in project()
if (POLICY CMP0048)
    cmake_policy(SET CMP0048 NEW)
endif (POLICY CMP0048)

project(RaDex VERSION "0.0.1" LANGUAGES CXX)

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
option(BUILD_EXAMPLES "Build example applications" OFF)
option(BUILD_SHARED_LIBS "Build using shared libraries" ON)
option(BUILD_SMARTREDIS "Build with smartredis support" ON)
option(BUILD_DRAGON "Build with Dragon support" ON)

# ============================================================================
# Find required packages
# ============================================================================
find_package(Threads REQUIRED)

# smartredis - optional
if(BUILD_SMARTREDIS)
    find_package(smartredis REQUIRED)
    message(STATUS "smartredis support enabled")
endif()

if(BUILD_DRAGON)
    find_path(DRAGON_INCLUDE_DIR
        NAMES dragon/ddict.h
        HINTS ENV DRAGON_BASE_DIR
        PATH_SUFFIXES include
    )
    find_library(DRAGON_LIBRARY
        NAMES dragon
        HINTS ENV DRAGON_BASE_DIR
        PATH_SUFFIXES lib
    )
    add_library(dragon UNKNOWN IMPORTED)
    set_target_properties(dragon PROPERTIES
        IMPORTED_LOCATION ${DRAGON_LIBRARY}
        INTERFACE_INCLUDE_DIRECTORIES "${DRAGON_INCLUDE_DIR}"
    )
    message(STATUS "Dragon support enabled")
endif()

# ============================================================================
# RaDex Library
# ============================================================================
set(RADDEX_SOURCES)

if(BUILD_SMARTREDIS)
    list(APPEND RADDEX_SOURCES src/cpp/smartredis.cpp)
endif()

if(BUILD_DRAGON)
    list(APPEND RADDEX_SOURCES src/cpp/dragon.cpp)
endif()

if(NOT RADDEX_SOURCES)
    message(FATAL_ERROR "At least one backend must be enabled: BUILD_SMARTREDIS or BUILD_DRAGON")
endif()

add_library(raddex ${RADDEX_SOURCES})

if(BUILD_SHARED_LIBS)
    set_target_properties(raddex PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()

# Include directories for the library
target_include_directories(raddex PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
)

# Link dependencies
if(BUILD_SMARTREDIS)
    target_link_libraries(raddex PUBLIC smartredis)
endif()

if(BUILD_DRAGON)
    target_link_libraries(raddex PUBLIC dragon)
endif()

target_link_libraries(raddex PUBLIC Threads::Threads)

# ============================================================================
# Install library and headers
# ============================================================================
install(
    TARGETS raddex
    EXPORT raddex-targets
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
    INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(DIRECTORY ${CMAKE_SOURCE_DIR}/include/
        DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

install(EXPORT raddex-targets
    FILE raddex-targets.cmake
    NAMESPACE RaDex::
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/raddex
)

include(CMakePackageConfigHelpers)
configure_package_config_file(
    ${CMAKE_CURRENT_SOURCE_DIR}/cmake/raddex-config.cmake.in
    ${CMAKE_CURRENT_BINARY_DIR}/raddex-config.cmake
    INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/raddex
)

write_basic_package_version_file(
    ${CMAKE_CURRENT_BINARY_DIR}/raddex-config-version.cmake
    VERSION ${CMAKE_PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

install(FILES
    ${CMAKE_CURRENT_BINARY_DIR}/raddex-config.cmake
    ${CMAKE_CURRENT_BINARY_DIR}/raddex-config-version.cmake
    DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/raddex
)

# ============================================================================
# Examples
# ============================================================================
if(BUILD_EXAMPLES)
    message(STATUS "Examples will be built")

    set(EXAMPLES)

    # Redis examples
    if(BUILD_SMARTREDIS)
        add_executable(redis-producer
            example/cpp-exchange/redis/producer.cpp
        )
        target_link_libraries(redis-producer PRIVATE raddex)
        target_include_directories(redis-producer PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )
        list(APPEND EXAMPLES redis-producer)

        add_executable(redis-consumer
            example/cpp-exchange/redis/consumer.cpp
        )
        target_link_libraries(redis-consumer PRIVATE raddex)
        target_include_directories(redis-consumer PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )
        list(APPEND EXAMPLES redis-consumer)
    endif()

    if(BUILD_DRAGON)
        # Dragon examples
        add_executable(dragon-producer
            example/cpp-exchange/dragon/producer.cpp
        )
        target_link_libraries(dragon-producer PRIVATE raddex dragon)
        target_include_directories(dragon-producer PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )
        list(APPEND EXAMPLES dragon-producer)

        add_executable(dragon-consumer
            example/cpp-exchange/dragon/consumer.cpp
        )
        target_link_libraries(dragon-consumer PRIVATE raddex dragon)
        target_include_directories(dragon-consumer PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )
        list(APPEND EXAMPLES dragon-consumer)

        add_executable(in-mem-poc
            example/cpp-exchange/in-mem/proof_of_concept_iface.cpp
        )
        target_link_libraries(in-mem-poc PRIVATE raddex dragon)
        target_include_directories(in-mem-poc PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )
        list(APPEND EXAMPLES in-mem-poc)

        # Simulation example
        find_package(MPI)
        add_executable(simulation
            example/sim/simulation.cpp
        )
        target_link_libraries(simulation PRIVATE raddex MPI::MPI_CXX dragon)
        target_include_directories(simulation PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )
        list(APPEND EXAMPLES in-mem-poc)

    endif()

    # Install examples (optional)
    install(
        TARGETS ${EXAMPLES}
        DESTINATION ${CMAKE_INSTALL_BINDIR}/examples
    )
else()
    message(STATUS "Examples will NOT be built (use -DBUILD_EXAMPLES=ON to enable)")
endif()
