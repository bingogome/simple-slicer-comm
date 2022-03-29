cmake_minimum_required(VERSION 3.13.4)

project(SimpleSlicerComm)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/SimpleSlicerComm")
set(EXTENSION_CATEGORY "SimpleSlicerComm")
set(EXTENSION_CONTRIBUTORS "Yihao Liu (Johns Hopkins University)")
set(EXTENSION_DESCRIPTION "This is an extension intended for testing experiments of simple-slicer-comm.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/SimpleSlicerComm.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/SimpleSlicerComm/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(Connections)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
