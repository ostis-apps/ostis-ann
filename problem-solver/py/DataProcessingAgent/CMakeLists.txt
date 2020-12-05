file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library (DataProcessingModule SHARED ${SOURCES})

target_include_directories(DataProcessingModule PRIVATE ${SC_MEMORY_SRC})
target_link_libraries(DataProcessingModule sc-memory)

add_dependencies(DataProcessingModule sc-memory)

sc_codegen(DataProcessingModule ${CMAKE_CURRENT_LIST_DIR})
