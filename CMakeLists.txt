cmake_minimum_required( VERSION 3.10 )
find_package( brainvisa-cmake REQUIRED )
BRAINVISA_PROJECT()
enable_testing()

BRAINVISA_FIND_PACKAGE( axon REQUIRED )
BRAINVISA_FIND_PACKAGE( morphologist-nonfree QUIET )
BRAINVISA_FIND_PACKAGE( aims-til QUIET )
BRAINVISA_DEPENDENCY( RUN DEPENDS "axon" RUN
                      ">= ${axon_VERSION_MAJOR}.${axon_VERSION_MINOR}" )
BRAINVISA_DEPENDENCY( RUN RECOMMENDS "morphologist-nonfree" RUN
                      ">= ${morphologist-nonfree_VERSION_MAJOR}.${morphologist-nonfree_VERSION_MINOR}" )
BRAINVISA_DEPENDENCY( RUN RECOMMENDS "aims-til" RUN "= ${aims-til_VERSION}" )
BRAINVISA_DEPENDENCY( RUN RECOMMENDS "anatomist-gpl" RUN
                      "= ${anatomist-gpl_VERSION}" )
BRAINVISA_DEPENDENCY( DEV DEPENDS "${PROJECT_NAME}" RUN "= ${${PROJECT_NAME}_VERSION}" )
BRAINVISA_DEPENDENCY( DEV RECOMMENDS "aims-til" DEV "= ${aims-til_VERSION}" )
BRAINVISA_DEPENDENCY( DEV RECOMMENDS "anatomist-gpl" DEV
                      "= ${anatomist-gpl_VERSION}" )
BRAINVISA_DEPENDENCY(
    RUN DEPENDS "brainvisa_spm" RUN
    ">= ${brainvisa_spm_VERSION_MAJOR}.${brainvisa_spm_VERSION_MINOR}" )

BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/brainvisa"
                                 ${PROJECT_NAME} )
BRAINVISA_COPY_PYTHON_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/python"
                                 ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/bin"
                          bin
                          ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/share/foms"
                          share/foms
                          ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( ${CMAKE_CURRENT_SOURCE_DIR}/share/morphologist
                          share/morphologist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}
                          ${PROJECT_NAME} )

BRAINVISA_COPY_DIRECTORY( "${CMAKE_CURRENT_SOURCE_DIR}/doc"
                          "share/doc/morphologist-${${PROJECT_NAME}_VERSION_MAJOR}.${${PROJECT_NAME}_VERSION_MINOR}"
                          ${PROJECT_NAME}-usrdoc )

brainvisa_add_test(morphologist-tests TIMEOUT 5400 "${PYTHON_EXECUTABLE_NAME}" -m brainvisa.tests.test_morphologist --no-ann TESTREF) # timeout: 1h30
brainvisa_add_test(morphologist-test-capsul TIMEOUT 5400 "${PYTHON_EXECUTABLE_NAME}" -m morphologist.tests.test_morphologist_capsul) # timeout: 1h30
set_tests_properties(morphologist-test-capsul PROPERTIES DEPENDS morphologist-tests)

find_package( Sphinx )
BRAINVISA_GENERATE_SPHINX_DOC( "sphinx/user_doc"
  "share/doc/morphologist-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/user_doc" USER )
BRAINVISA_GENERATE_SPHINX_DOC( "sphinx/dev_doc"
  "share/doc/morphologist-${BRAINVISA_PACKAGE_VERSION_MAJOR}.${BRAINVISA_PACKAGE_VERSION_MINOR}/dev_doc" )

BRAINVISA_CREATE_CMAKE_CONFIG_FILES()

