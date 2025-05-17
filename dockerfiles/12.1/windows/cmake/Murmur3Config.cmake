if (TARGET Murmur3::Murmur3)
    return()
endif()

get_filename_component(_IMPORT_PREFIX "${CMAKE_CURRENT_LIST_FILE}" DIRECTORY)
get_filename_component(_IMPORT_PREFIX "${_IMPORT_PREFIX}" DIRECTORY) # remove one directory level i.e. "cmake/"
message(STATUS "Found Murmur3: ${_IMPORT_PREFIX}")

add_library(Murmur3::Murmur3 SHARED IMPORTED)
set_target_properties(Murmur3::Murmur3
    PROPERTIES
        INTERFACE_INCLUDE_DIRECTORIES ${_IMPORT_PREFIX}/include
        IMPORTED_LOCATION "${_IMPORT_PREFIX}/Murmur3.dll"
        IMPORTED_IMPLIB "${_IMPORT_PREFIX}/Murmur3.lib"
)