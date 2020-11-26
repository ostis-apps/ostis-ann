set(SC_EXAMPLE_MODULE_SRC "${PROBLEM_SOLVER_ROOT}/momoModule")

set(SOURCES
		"momoModule.cpp"
		"keynodes/keynodes.cpp"
		"agents/ReportGeneration.cpp"
		"agents/PatientReport.cpp"
		"agents/StudyReport.cpp"
		)

set(HEADERS
		"momoModule.hpp"
		"keynodes/keynodes.hpp"
		"agents/ReportGeneration.hpp"
		"agents/PatientReport.hpp"
		"agents/StudyReport.hpp"
		)

include_directories(${SC_EXAMPLE_MODULE_SRC} ${SC_MEMORY_SRC} ${GLIB2_INCLUDE_DIRS})

add_library(momoModule SHARED ${SOURCES} ${HEADERS})
add_dependencies(momoModule sc-memory-cpp sc-kpm-common sc-agents-common)
target_link_libraries(momoModule sc-memory-cpp sc-kpm-common sc-agents-common)

sc_codegen(momoModule ${SC_EXAMPLE_MODULE_SRC})

