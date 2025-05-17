if (TARGET Nuke::NDK)
    return()
endif()

get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" PATH) # remove one directory level i.e. "cmake/"
message(STATUS "Found NDK: ${_IMPORT_PREFIX}")

include(CMakeFindDependencyMacro)
find_dependency(OpenGL REQUIRED)

add_library(Nuke::NDK INTERFACE IMPORTED)
set_target_properties(Nuke::NDK
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES ${_IMPORT_PREFIX}/include
        INTERFACE_COMPILE_FEATURES cxx_std_11
        INTERFACE_LINK_LIBRARIES ${_IMPORT_PREFIX}/libDDImage.so
)


function(add_nuke_plugin PLUGIN_NAME)
    add_library(${PLUGIN_NAME} MODULE ${ARGN})
    target_link_libraries(${PLUGIN_NAME} PRIVATE Nuke::NDK)
    set_target_properties(${PLUGIN_NAME} PROPERTIES PREFIX "")
    if (APPLE)
        set_target_properties(${PLUGIN_NAME} PROPERTIES SUFFIX ".dylib")
    endif()
endfunction()