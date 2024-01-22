# Global toolchain file to setup CMake for OSXCross

set(CMAKE_C_COMPILER o64-clang)
set(CMAKE_CXX_COMPILER o64-clang++)
set(CMAKE_SYSTEM_NAME Darwin)
set(CMAKE_OSX_SYSROOT $ENV{MACOS_SDK})
set(CMAKE_OSX_DEPLOYMENT_TARGET $ENV{DEPLOYMENT_TARGET} CACHE STRING "Minimum macOS deployment target version")
