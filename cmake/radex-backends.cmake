include_guard(GLOBAL)

function(radex_find_backends)
    if(BUILD_SMARTREDIS)
        find_package(smartredis REQUIRED)
        message(STATUS "smartredis support enabled")
    endif()

    if(BUILD_DRAGON)
        find_path(DRAGON_INCLUDE_DIR
            NAMES dragon/ddict.h
            HINTS ENV DRAGON_BASE_DIR
            HINTS ${dragon_DIR}
            PATH_SUFFIXES include
        )
        find_library(DRAGON_LIBRARY
            NAMES dragon
            HINTS ENV DRAGON_BASE_DIR
            HINTS ${dragon_DIR}
            PATH_SUFFIXES lib
        )

        if(NOT DRAGON_LIBRARY)
            message(FATAL_ERROR
                "Dragon backend requested, but library cannot be found. Set dragon_DIR"
            )
        endif()

        if(NOT TARGET dragon)
            add_library(dragon UNKNOWN IMPORTED)
            set_target_properties(dragon PROPERTIES
                IMPORTED_LOCATION ${DRAGON_LIBRARY}
                INTERFACE_INCLUDE_DIRECTORIES "${DRAGON_INCLUDE_DIR}"
            )
        endif()
        message(STATUS "Dragon support enabled")
    endif()
endfunction()