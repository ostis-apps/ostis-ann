#include "CommonModule.hpp"

#include "agent/NonAtomicActionInterpreterAgent.hpp"
#include "agent/sc_agent_recommend_training_parameters.hpp"

using namespace commonModule;

SC_MODULE_REGISTER(CommonModule)
  ->Agent<NonAtomicActionInterpreterAgent>()
  ->Agent<RecommendTrainingParametersAgent>();
