#pragma once

#include <sc-memory/sc_agent.hpp>

class SearchUtils
{
public:
  static ScAddrSet findAllProblemSolvingMethods(ScMemoryContext * m_context);
  static ScAddrSet filterProblemSolvingMethodsByRelatedProblemConcept(
      ScMemoryContext * m_context,
      ScAddrSet const & problemSolvingMethods,
      ScAddr const & problemConcept);
};