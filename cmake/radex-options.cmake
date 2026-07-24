include_guard(GLOBAL)

function(radex_backend_selection_options)
    option(BUILD_SMARTREDIS "Build with smartredis support" ON)
    option(BUILD_DRAGON "Build with Dragon support" ON)
endfunction()

function(radex_define_library_options)
    option(BUILD_SHARED_LIBS "Build shared libraries" ON)
    option(BUILD_STATIC_LIBS "Build static libraries" ON)
    radex_backend_selection_options()
endfunction()

function(radex_define_example_options)
    radex_backend_selection_options()
endfunction()

function(radex_define_root_options)
    option(BUILD_EXAMPLES "Build example applications" ON)
    option(BUILD_TESTS "Build test applications and dependencies" ON)
    radex_define_library_options()
    radex_define_example_options()
endfunction()
