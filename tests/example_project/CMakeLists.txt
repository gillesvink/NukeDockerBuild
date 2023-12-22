cmake_minimum_required(VERSION 3.10 FATAL_ERROR)
project(MagicBlur)

set(CMAKE_MODULE_PATH "CMake;${CMAKE_MODULE_PATH}")
set(CMAKE_POSITION_INDEPENDENT_CODE TRUE)

find_package(Nuke REQUIRED)


function(add_plugin PLUGIN_NAME)
    add_nuke_plugin(${PLUGIN_NAME} ${ARGN})
    target_compile_definitions(${PLUGIN_NAME} PRIVATE FN_TESTPLUGINS)
endfunction()

add_plugin(TestPlugin src/TestPlugin.cpp)