cmake_minimum_required(VERSION 3.13)

if(POLICY CMP0109)
    cmake_policy(SET CMP0109 NEW)
endif()

project(RaDexDocs VERSION 0.0.1 LANGUAGES NONE)

get_filename_component(RADEX_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/.." ABSOLUTE)
set(RADEX_PROJECT_VERSION ${PROJECT_VERSION})

find_package(Doxygen REQUIRED)
find_program(SPHINX_EXECUTABLE NAMES sphinx-build REQUIRED)

set(DOXYFILE_IN ${CMAKE_CURRENT_SOURCE_DIR}/Doxyfile.in)
set(DOXYFILE_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
set(DOXYGEN_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/doxygen)
set(DOXYGEN_XML_DIR ${DOXYGEN_OUTPUT_DIR}/xml)
set(SPHINX_SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR})
set(SPHINX_BUILD_DIR ${CMAKE_CURRENT_BINARY_DIR}/sphinx)

configure_file(${DOXYFILE_IN} ${DOXYFILE_OUT} @ONLY)

add_custom_target(doxygen
    COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYFILE_OUT}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Generating Doxygen XML"
    VERBATIM
)

add_custom_target(docs ALL
    COMMAND ${SPHINX_EXECUTABLE}
            -b html
            -Dbreathe_projects.raddex=${DOXYGEN_XML_DIR}
            ${SPHINX_SOURCE_DIR}
            ${SPHINX_BUILD_DIR}
    DEPENDS doxygen
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
    COMMENT "Generating Sphinx documentation"
    VERBATIM
)
