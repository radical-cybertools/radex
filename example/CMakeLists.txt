cmake_minimum_required(VERSION 3.13)

# Policy for VERSION in project()
if (POLICY CMP0048)
    cmake_policy(SET CMP0048 NEW)
endif (POLICY CMP0048)

include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-standalone.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-options.cmake)
include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-backends.cmake)

radex_define_example_options()

# Standalone build support
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    include(${CMAKE_CURRENT_LIST_DIR}/../cmake/radex-version.cmake)
    project(RADEX-Examples
        VERSION ${RADEX_VERSION}
        LANGUAGES CXX
    )
    find_package(radex REQUIRED)
    radex_find_backends()
endif()

radex_setup_standalone_build()

# ============================================================================
# Examples
# ============================================================================
set(EXAMPLES)

# In memory example
add_executable(in-mem-poc
    cpp-exchange/in-mem/proof_of_concept_iface.cpp
)
list(APPEND EXAMPLES in-mem-poc)

# Redis examples
if(BUILD_SMARTREDIS)
    set(SMARTREDIS_EXAMPLES)
    add_executable(redis-cpp-producer cpp-exchange/redis/producer.cpp)
    list(APPEND SMARTREDIS_EXAMPLES redis-cpp-producer)

    add_executable(redis-cpp-consumer cpp-exchange/redis/consumer.cpp)
    list(APPEND SMARTREDIS_EXAMPLES redis-cpp-consumer)

    foreach(target IN LISTS SMARTREDIS_EXAMPLES)
        target_link_libraries(${target} PRIVATE smartredis)
    endforeach()

    list(APPEND EXAMPLES ${SMARTREDIS_EXAMPLES})

endif()

if(BUILD_DRAGON)
    set(DRAGON_EXAMPLES)
    add_executable(dragon-cpp-producer
        cpp-exchange/dragon/producer.cpp
    )
    list(APPEND DRAGON_EXAMPLES dragon-cpp-producer)

    add_executable(dragon-cpp-consumer
        cpp-exchange/dragon/consumer.cpp
    )
    list(APPEND DRAGON_EXAMPLES dragon-cpp-consumer)

    # Dragon Python/C++ examples
    add_executable(dragon-cpp-with-py
        py-cpp-exchange/dragon/app.cpp
    )
    list(APPEND DRAGON_EXAMPLES dragon-cpp-with-py)

    # Simulation example
    find_package(MPI)
    add_executable(simulation
        active-learn/cpp-mpi-with-ddict/simulation.cpp
    )
    target_link_libraries(simulation PRIVATE MPI::MPI_CXX)
    list(APPEND DRAGON_EXAMPLES simulation)

    foreach(target in LISTS DRAGON_EXAMPLES)
        target_link_libraries(dragon-cpp-consumer PRIVATE dragon)
        target_include_directories(dragon-cpp-consumer PRIVATE
            ${CMAKE_CURRENT_SOURCE_DIR}/include
        )
    endforeach()
    list(APPEND EXAMPLES ${DRAGON_EXAMPLES})

endif()

foreach(target IN LISTS EXAMPLES)
    radex_set_target_install_rpath(${target})
    target_include_directories(${target} PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/../include
    )
    target_link_libraries(${target} PRIVATE radex::radex)
endforeach()

# Install examples
install(
    TARGETS ${EXAMPLES}
    DESTINATION ${CMAKE_INSTALL_BINDIR}/examples
)