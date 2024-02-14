file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

include_directories(${CMAKE_CURRENT_LIST_DIR} ${SC_MEMORY_SRC} ${SC_KPM_SRC})

add_library (nnOutputItropretatorModule SHARED ${SOURCES})
target_link_libraries(nnOutputItropretatorModule sc-memory sc-agents-common)

sc_codegen(nnOutputItropretatorModule ${CMAKE_CURRENT_LIST_DIR})
