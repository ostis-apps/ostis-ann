set(SC_nn_Output_Itropretator_Module_SRC "${PROBLEM_SOLVER_ROOT}/nnOutputItropretatorModule")

set(SOURCES
		"nnOutputItropretatorModule.cpp"
		"keynodes/keynodes.cpp"
		"agents/nnOutputItropretatorAgent.cpp"
		)

set(HEADERS
		"nnOutputItropretatorModule.hpp"
		"keynodes/keynodes.hpp"
		"agents/nnOutputItropretatorAgent.hpp"
		)

include_directories(${SC_nn_Output_Itropretator_Module_SRC} ${SC_MEMORY_SRC} ${GLIB2_INCLUDE_DIRS})

add_library(nnOutputItropretatorModule SHARED ${SOURCES} ${HEADERS})
add_dependencies(nnOutputItropretatorModule sc-memory-cpp sc-kpm-common sc-agents-common)
target_link_libraries(nnOutputItropretatorModule sc-memory-cpp sc-kpm-common sc-agents-common)

sc_codegen(nnOutputItropretatorModule ${SC_nn_Output_Itropretator_Module_SRC})

