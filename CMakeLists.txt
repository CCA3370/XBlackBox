cmake_minimum_required(VERSION 3.16)
project(XBlackBox VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Platform detection
if(WIN32)
    set(PLATFORM_NAME "win")
    set(PLUGIN_EXTENSION ".xpl")
elseif(APPLE)
    set(PLATFORM_NAME "mac")
    set(PLUGIN_EXTENSION ".xpl")
else()
    set(PLATFORM_NAME "lin")
    set(PLUGIN_EXTENSION ".xpl")
endif()

# X-Plane SDK paths
set(XPLM_SDK_PATH "${CMAKE_SOURCE_DIR}/SDK/CHeaders/XPLM")
set(WIDGETS_SDK_PATH "${CMAKE_SOURCE_DIR}/SDK/CHeaders/Widgets")

# ImGui paths
set(IMGUI_PATH "${CMAKE_SOURCE_DIR}/SDK/imgui-1.92.5")

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${XPLM_SDK_PATH}
    ${WIDGETS_SDK_PATH}
    ${IMGUI_PATH}
    ${IMGUI_PATH}/backends
)

# Source files
set(SOURCES
    src/main.cpp
    src/DatarefManager.cpp
    src/Recorder.cpp
    src/Settings.cpp
    src/UIManager.cpp
    
    # ImGui core
    ${IMGUI_PATH}/imgui.cpp
    ${IMGUI_PATH}/imgui_demo.cpp
    ${IMGUI_PATH}/imgui_draw.cpp
    ${IMGUI_PATH}/imgui_tables.cpp
    ${IMGUI_PATH}/imgui_widgets.cpp
    
    # ImGui backend for X-Plane (we'll use OpenGL3)
    ${IMGUI_PATH}/backends/imgui_impl_opengl3.cpp
)

# Header files
set(HEADERS
    include/DatarefManager.h
    include/Recorder.h
    include/Settings.h
    include/UIManager.h
    include/common.h
)

# Create the plugin library
add_library(XBlackBox SHARED ${SOURCES} ${HEADERS})

# Set output name
set_target_properties(XBlackBox PROPERTIES
    PREFIX ""
    OUTPUT_NAME "${PLATFORM_NAME}"
    SUFFIX "${PLUGIN_EXTENSION}"
)

# Platform-specific settings
if(WIN32)
    target_compile_definitions(XBlackBox PRIVATE IBM=1 XPLM420=1 XPLM400=1 XPLM301=1 XPLM300=1 XPLM210=1 XPLM200=1)
    target_link_libraries(XBlackBox
        ${CMAKE_SOURCE_DIR}/SDK/Libraries/Win/XPLM_64.lib
        ${CMAKE_SOURCE_DIR}/SDK/Libraries/Win/XPWidgets_64.lib
        opengl32
    )
elseif(APPLE)
    target_compile_definitions(XBlackBox PRIVATE APL=1 XPLM420=1 XPLM400=1 XPLM301=1 XPLM300=1 XPLM210=1 XPLM200=1)
    target_link_libraries(XBlackBox
        "-framework OpenGL"
        "-framework CoreFoundation"
    )
    set_target_properties(XBlackBox PROPERTIES
        LINK_FLAGS "-fvisibility=hidden -bundle -flat_namespace -undefined suppress"
    )
else()
    target_compile_definitions(XBlackBox PRIVATE LIN=1 XPLM420=1 XPLM400=1 XPLM301=1 XPLM300=1 XPLM210=1 XPLM200=1)
    find_library(OPENGL_LIBRARY NAMES GL PATHS /usr/lib/x86_64-linux-gnu /usr/lib)
    if(OPENGL_LIBRARY)
        target_link_libraries(XBlackBox ${OPENGL_LIBRARY})
    else()
        message(STATUS "OpenGL library not found, plugin may not link correctly")
    endif()
endif()

# Compiler flags
if(MSVC)
    target_compile_options(XBlackBox PRIVATE /W4)
else()
    target_compile_options(XBlackBox PRIVATE -Wall -Wextra)
endif()

# Install target
install(TARGETS XBlackBox
    LIBRARY DESTINATION .
    RUNTIME DESTINATION .
)
