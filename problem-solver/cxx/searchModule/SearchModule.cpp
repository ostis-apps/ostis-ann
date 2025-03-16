#include "SearchModule.hpp"

#include "agents/FindSolvingMethodAgent.hpp"

using namespace searchModule;

SC_MODULE_REGISTER(SearchModule)->Agent<FindSolvingMethodAgent>();
