file(GLOB_RECURSE SOURCES "*.cpp" "*.hpp")

add_library (ClassifierAnswerWriterModule SHARED ${SOURCES})

target_include_directories(ClassifierAnswerWriterModule PRIVATE ${SC_MEMORY_SRC})
target_link_libraries(ClassifierAnswerWriterModule sc-memory)

add_dependencies(ClassifierAnswerWriterModule sc-memory)

sc_codegen(ClassifierAnswerWriterModule ${CMAKE_CURRENT_LIST_DIR})
