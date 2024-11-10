#include "FindSolvingMethodAgent.hpp"

#include "keynodes/SearchKeynodes.hpp"

using namespace searchModule;

ScAddr FindSolvingMethodAgent::GetActionClass() const
{
  return SearchKeynodes::action_find_problem_solving_method;
}

ScResult FindSolvingMethodAgent::DoProgram(ScActionInitiatedEvent const & event, ScAction & action)
{
  ScMemoryContext context;
  try
  {
    ScAddr problemStruct = action.GetArgument(ScKeynodes::rrel_1);
    ScAddr targetSituationTemplate = getTargetSituationTemplate(problemStruct, context);
    SC_AGENT_LOG_INFO(context.GetElementSystemIdentifier(targetSituationTemplate));
  }

  catch (const std::exception & ex)
  {
    SC_AGENT_LOG_ERROR(ex.what());
    return action.FinishWithError();
  }

  return action.FinishSuccessfully();
}

ScAddr FindSolvingMethodAgent::getTargetSituationTemplate(ScAddr problemStruct, ScMemoryContext & context)
{
  ScTemplate problemActionNodeTemplate;
  problemActionNodeTemplate.Triple(
      problemStruct, ScType::EdgeAccessVarPosPerm, ScType::NodeVar >> "_problemActionNode");
  problemActionNodeTemplate.Triple(SearchKeynodes::action, ScType::EdgeAccessVarPosPerm, "_problemActionNode");
  ScTemplateSearchResult searchResult;
  if (!context.SearchByTemplate(problemActionNodeTemplate, searchResult))
  {
    throw std::runtime_error("Failed to define the problem action node.");
  }
  ScAddr problemActionNode;
  searchResult[0].Get("_problemActionNode", problemActionNode);
  ScIterator5Ptr it5 = context.CreateIterator5(
      problemActionNode,
      ScType::EdgeDCommonConst,
      ScType::NodeConstStruct,
      ScType::EdgeAccessConstPosPerm,
      SearchKeynodes::nrel_target_situation);
  if (!it5->Next())
  {
    throw std::runtime_error("Failed to define the target situation template.");
  }
  return it5->Get(2);
}
