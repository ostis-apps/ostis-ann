file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library(searchModule
    SHARED ${SOURCES}
)

target_link_libraries(searchModule
    LINK_PRIVATE sc-memory
)

target_include_directories(searchModule
    PRIVATE $(CMAKE_CURRENT_SOURCE_DIR)
)

include_directories(${CMAKE_CURRENT_LIST_DIR})
