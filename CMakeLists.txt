cmake_minimum_required( VERSION 2.6 )
find_package( brainvisa-cmake REQUIRED )
BRAINVISA_PROJECT()

BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/brainvisa"
                                 ${PROJECT_NAME} )
BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/python"
                                 ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/bin"
                          bin
                          ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/doc"
                          "share/doc/morphologist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}"
                          ${PROJECT_NAME}-usrdoc )

BRAINVISA_CREATE_CMAKE_CONFIG_FILES()

