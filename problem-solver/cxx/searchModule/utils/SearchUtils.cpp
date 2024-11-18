#include "SearchUtils.hpp"

#include "keynodes/SearchKeynodes.hpp"

using namespace searchModule;

ScAddrSet SearchUtils::findAllProblemSolvingMethods(ScMemoryContext * m_context)
{
  ScAddrSet result;
  ScTemplate solvingMethodClassTemplate;
  solvingMethodClassTemplate.Quintuple(
      SearchKeynodes::concept_problem_solving_method,
      ScType::EdgeDCommonVar,
      ScType::NodeVarClass >> "_solvingMethodClass",
      ScType::EdgeAccessVarPosPerm,
      ScKeynodes::nrel_inclusion);
  solvingMethodClassTemplate.Triple(
      "_solvingMethodClass", ScType::EdgeAccessVarPosPerm, ScType::NodeVar >> "_solvingMethod");
  ScTemplateSearchResult solvingMethodClassSearchResult;
  if (m_context->SearchByTemplate(solvingMethodClassTemplate, solvingMethodClassSearchResult))
  {
    for (size_t i = 0; i < solvingMethodClassSearchResult.Size(); ++i)
    {
      ScAddr item;
      solvingMethodClassSearchResult[i].Get("_solvingMethod", item);
      result.insert(item);
    }
  }

  // in case if there are solving methods in memory that directly belongs to 'concept_problem_solving_method'
  ScIterator3Ptr it3 = m_context->CreateIterator3(
      SearchKeynodes::concept_problem_solving_method, ScType::EdgeAccessConstPosPerm, ScType::NodeConst);

  while (it3->Next())
  {
    result.insert(it3->Get(2));
  }
  return result;
}

ScAddrSet SearchUtils::filterProblemSolvingMethodsByRelatedProblemConcept(
    ScMemoryContext * m_context,
    const ScAddrSet & problemSolvingMethods,
    const ScAddr & problemConcept)
{
  if (problemConcept == SearchKeynodes::concept_problem)
  {
    return problemSolvingMethods;
  }
  ScAddrSet result;
  for (ScAddr method : problemSolvingMethods)
  {
    ScIterator5Ptr it5 = m_context->CreateIterator5(
        method,
        ScType::EdgeDCommonConst,
        problemConcept,
        ScType::EdgeAccessConstPosPerm,
        SearchKeynodes::nrel_class_of_can_be_solved_problems);
    if (it5->Next())
    {
      result.insert(method);
    }
  }
  return result;
}
