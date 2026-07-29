set(RADEX_STANDALONE_MODULE_DIR "${CMAKE_CURRENT_LIST_DIR}")

function(radex_set_target_install_rpath target_name)
    if(NOT DEFINED RADEX_INSTALL_RPATH)
        include(GNUInstallDirs)
        if(IS_ABSOLUTE "${CMAKE_INSTALL_LIBDIR}")
            set(RADEX_INSTALL_RPATH "${CMAKE_INSTALL_LIBDIR}")
        else()
            set(RADEX_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
        endif()
    endif()

    set(_target_install_rpath "${RADEX_INSTALL_RPATH}")
    foreach(dep_target IN LISTS ARGN)
        if(TARGET ${dep_target})
            list(APPEND _target_install_rpath "$<TARGET_FILE_DIR:${dep_target}>")
        endif()
    endforeach()

    set_target_properties(${target_name} PROPERTIES
        BUILD_WITH_INSTALL_RPATH TRUE
        INSTALL_RPATH "${_target_install_rpath}"
        INSTALL_RPATH_USE_LINK_PATH TRUE
    )
endfunction()

function(radex_setup_standalone_build)
    set(options
        FIND_THREADS
        FIND_BACKENDS
        FIND_INSTALLED_RADEX
        ENABLE_LANGUAGE_SUPPORT
    )
    set(oneValueArgs
        OPTIONS_FUNCTION
    )
    cmake_parse_arguments(RADEX_STANDALONE "${options}" "${oneValueArgs}" "" ${ARGN})

    if(NOT CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
        return()
    endif()

    set(CMAKE_CXX_STANDARD 17)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(CMAKE_CXX_VISIBILITY_PRESET default)

    if(NOT DEFINED CMAKE_BUILD_TYPE)
        set(CMAKE_BUILD_TYPE "Release")
    endif()

    if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
        set(CMAKE_INSTALL_PREFIX ${CMAKE_SOURCE_DIR}/install)
    endif()

    include(GNUInstallDirs)

    if(IS_ABSOLUTE "${CMAKE_INSTALL_LIBDIR}")
        set(RADEX_INSTALL_RPATH "${CMAKE_INSTALL_LIBDIR}")
    else()
        set(RADEX_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/${CMAKE_INSTALL_LIBDIR}")
    endif()

    # Export computed install lib path for target-level helper usage.
    set(RADEX_INSTALL_RPATH "${RADEX_INSTALL_RPATH}" PARENT_SCOPE)

    include(${RADEX_STANDALONE_MODULE_DIR}/radex-options.cmake)
    if(RADEX_STANDALONE_OPTIONS_FUNCTION STREQUAL "radex_define_root_options")
        radex_define_root_options()
    elseif(RADEX_STANDALONE_OPTIONS_FUNCTION STREQUAL "radex_define_example_options")
        radex_define_example_options()
    elseif(RADEX_STANDALONE_OPTIONS_FUNCTION STREQUAL "radex_define_library_options")
        radex_define_library_options()
    elseif(RADEX_STANDALONE_OPTIONS_FUNCTION)
        message(FATAL_ERROR
            "Unknown standalone options function '${RADEX_STANDALONE_OPTIONS_FUNCTION}'."
        )
    endif()

    if(RADEX_STANDALONE_ENABLE_LANGUAGE_SUPPORT)
        radex_language_support()
    endif()

    if(RADEX_STANDALONE_FIND_INSTALLED_RADEX)
        find_package(radex REQUIRED)
    endif()

    if(RADEX_STANDALONE_FIND_THREADS)
        find_package(Threads REQUIRED)
    endif()

    if(RADEX_STANDALONE_FIND_BACKENDS)
        include(${RADEX_STANDALONE_MODULE_DIR}/radex-backends.cmake)
        radex_find_backends()
    endif()
endfunction()