cmake_minimum_required(VERSION 3.13)

# Policy for VERSION in project()
if (POLICY CMP0048)
    cmake_policy(SET CMP0048 NEW)
endif (POLICY CMP0048)


# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_VISIBILITY_PRESET default)

# Default build type
if(NOT DEFINED CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE "Release")
endif()

# Standalone build support
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-version.cmake)
    project(radex VERSION ${RADEX_VERSION} LANGUAGES CXX)

    project(RADEX-Library
                VERSION ${RADEX_VERSION}
        LANGUAGES CXX
    )
    # Include GNU install directories
    include(GNUInstallDirs)

    # Assume library was installed somewhere
    find_package(radex REQUIRED)

    include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-options.cmake)
    radex_define_library_options()
    radex_language_support()

    find_package(Threads REQUIRED)
    include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-backends.cmake)
    radex_find_backends()

endif()

if(ENABLE_CXX)
    # ============================================================================
    # RaDex Library
    # ============================================================================
    set(RADEX_SOURCES)
    list(APPEND RADEX_SOURCES cpp/client.cpp)

    if(BUILD_SMARTREDIS)
        list(APPEND RADEX_SOURCES cpp/smartredis.cpp)
    endif()

    if(BUILD_DRAGON)
        list(APPEND RADEX_SOURCES cpp/dragon.cpp)
    endif()

    add_library(objlib OBJECT ${RADEX_SOURCES})

    set(LIBRARY_TARGETS objlib)
    if(BUILD_SHARED_LIBS)
        set_target_properties(objlib PROPERTIES POSITION_INDEPENDENT_CODE ON)
        add_library(radex_shared SHARED $<TARGET_OBJECTS:objlib>)
        list(APPEND LIBRARY_TARGETS radex_shared)
    endif()

    if(BUILD_STATIC_LIBS)
        add_library(radex_static STATIC $<TARGET_OBJECTS:objlib>)
        list(APPEND LIBRARY_TARGETS radex_static)
    endif()

    # Canonical target for consumers: shared when available, otherwise static.
    if(TARGET radex_shared)
        set(RADEX_PRIMARY_TARGET radex_shared)
    elseif(TARGET radex_static)
        set(RADEX_PRIMARY_TARGET radex_static)
    else()
        message(FATAL_ERROR "No RaDex library target was created. Enable BUILD_SHARED_LIBS and/or BUILD_STATIC_LIBS.")
    endif()

    add_library(radex INTERFACE)
    add_library(radex::radex ALIAS radex)
    target_link_libraries(radex INTERFACE ${RADEX_PRIMARY_TARGET})
    target_include_directories(radex INTERFACE
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
        $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
    )

    # Apply include and properties to each library being built
    foreach(target IN LISTS LIBRARY_TARGETS)
        target_include_directories(${target} PUBLIC
            $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/../include>
            $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>
        )
        set_target_properties(${target} PROPERTIES OUTPUT_NAME radex)
        if(BUILD_SMARTREDIS)
            target_link_libraries(${target} PUBLIC smartredis)
        endif()
        if(BUILD_DRAGON)
            target_link_libraries(${target} PUBLIC dragon)
        endif()
    endforeach()


    # ============================================================================
    # Install library and headers
    # ============================================================================
    list(REMOVE_ITEM LIBRARY_TARGETS objlib)
    install(
        TARGETS ${LIBRARY_TARGETS}
        EXPORT radex-targets
        LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
        ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
        INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )

    install(
        TARGETS radex
        EXPORT radex-targets
        INCLUDES DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )

    install(DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../include/
            DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
    )

    install(EXPORT radex-targets
        FILE radex-targets.cmake
        NAMESPACE radex::
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/radex
    )

    include(CMakePackageConfigHelpers)
    configure_package_config_file(
        ${CMAKE_CURRENT_SOURCE_DIR}/cmake/radex-config.cmake.in
        ${CMAKE_CURRENT_BINARY_DIR}/radex-config.cmake
        INSTALL_DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/radex
    )

    write_basic_package_version_file(
        ${CMAKE_CURRENT_BINARY_DIR}/radex-config-version.cmake
        VERSION ${CMAKE_PROJECT_VERSION}
        COMPATIBILITY AnyNewerVersion
    )

    install(FILES
        ${CMAKE_CURRENT_BINARY_DIR}/radex-config.cmake
        ${CMAKE_CURRENT_BINARY_DIR}/radex-config-version.cmake
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/cmake/radex
    )
endif()

# ============================================================================
# Install the Python client
# ============================================================================
if(ENABLE_PYTHON)
  if(NOT ALLOW_SYSTEM_PYTHON)
      if(NOT (DEFINED ENV{VIRTUAL_ENV} OR DEFINED ENV{CONDA_PREFIX}))
          message(FATAL_ERROR
              "Python virtual environment not detected. To force installation in the system Python set the ALLOW_SYSTEM_PYTHON option"
          )
      endif()
      set(Python_FIND_VIRTUALENV ONLY)
      find_package(Python COMPONENTS Interpreter REQUIRED)
      message(STATUS "Python package will be installed")
      message(STATUS "\tFound Python Executable: ${Python_EXECUTABLE}")
      message(STATUS "\tFound Python Version: ${Python_VERSION}")
  endif()
  add_custom_target(install_python_package ALL
      COMMAND ${CMAKE_COMMAND} -E env
          DRAGON_INCLUDE_DIR=${DRAGON_INCLUDE_DIR}
          DRAGON_LIB_DIR=${DRAGON_LIB_DIR}
          ${Python_EXECUTABLE} -m pip install "${CMAKE_CURRENT_SOURCE_DIR}/python"
      COMMENT "Building and installing Python package"
  )
endif()