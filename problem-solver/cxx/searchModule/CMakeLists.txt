SET(CMAKE_BUILD_TYPE Debug)
set(SOURCES
        "SearchModule.cpp"
        "agents/FindSolvingMethodAgent.cpp"
        "utils/SearchUtils.cpp"
        "utils/RelationUtils.cpp"
        "utils/CombinationUtils.cpp"
)

set(HEADERS
        "SearchModule.hpp"
        "agents/FindSolvingMethodAgent.hpp"
        "keynodes/SearchKeynodes.hpp"
        "utils/SearchUtils.hpp"
        "utils/RelationUtils.hpp"
        "utils/CombinationUtils.hpp"
)

include_directories(${CMAKE_CURRENT_LIST_DIR} ${SC_MEMORY_SRC} ${SC_KPM_SRC} ${SC_TOOLS_SRC})

add_library(searchModule SHARED ${SOURCES} ${HEADERS})

target_link_libraries(searchModule sc-memory sc-agents-common)
