#include "FindSolvingMethodAgent.hpp"

#include "keynodes/SearchKeynodes.hpp"
#include "utils/CombinationUtils.hpp"
#include "utils/RelationUtils.hpp"
#include "utils/SearchUtils.hpp"

using namespace searchModule;

ScAddr FindSolvingMethodAgent::GetActionClass() const
{
  return SearchKeynodes::action_find_problem_solving_method;
}

ScResult FindSolvingMethodAgent::DoProgram(ScActionInitiatedEvent const & event, ScAction & action)
{
  try
  {
    ScAddrSet elementsToSave;

    ScAddr problemStruct = action.GetArgument(ScKeynodes::rrel_1);

    ScAddr problemConcept = getProblemConcept(problemStruct);
    ScAddrSet problemSolvingMethods = SearchUtils::findAllProblemSolvingMethods(&m_context);

    ScAddrSet filteredByProblemConceptSolvingMethods = SearchUtils::filterProblemSolvingMethodsByRelatedProblemConcept(
        &m_context, problemSolvingMethods, problemConcept);

    ScAddr problemActionNode = getProblemActionNode(problemStruct);
    ScStructure targetSituationStruct = getTargetSituationTemplate(problemActionNode);

    ScIterator3Ptr elementsToSaveFromTargetSituationIter =
        m_context.CreateIterator3(targetSituationStruct, ScType::EdgeAccessConstPosPerm, ScType::Unknown);

    while (elementsToSaveFromTargetSituationIter->Next())
    {
      elementsToSave.insert(elementsToSaveFromTargetSituationIter->Get(2));
    }

    ScTemplate targetSituationTemplate;
    m_context.BuildTemplate(targetSituationTemplate, targetSituationStruct);

    ScAddrVector problemActionObjects =
        RelationUtils::getNodeRoleRelationsByFilter(&m_context, problemActionNode, [](const ScAddr &) -> bool {
          return true;  // no filtering, return all action objects
        });

    ScAddrSet suitableMethods;
    ScAddrSet structuresToRemove;

    for (ScAddr solvingMethod : filteredByProblemConceptSolvingMethods)
    {
      try
      {
        ScAddr workingResultStructure;
        workingResultStructure = getSolvingMethodWorkingResultTemplate(solvingMethod);

        ScIterator3Ptr elementsToSaveFromWorkingResultIter =
            m_context.CreateIterator3(workingResultStructure, ScType::EdgeAccessConstPosPerm, ScType::Unknown);

        while (elementsToSaveFromWorkingResultIter->Next())
        {
          elementsToSave.insert(elementsToSaveFromWorkingResultIter->Get(2));
        }

        ScAddrVector solvingMethodVariables = RelationUtils::getNodeRoleRelationsByFilter(
            &m_context, workingResultStructure, [this](const ScAddr & addr) -> bool {
              return m_context.GetElementType(addr).IsVar();  // filtering variables
            });

        std::vector<ScTemplateParams> replacements =
            CombinationUtils::getAllReplacementCombinations(problemActionObjects, solvingMethodVariables);

        for (auto const & replacement : replacements)
        {
          ScTemplate replacementTemplate;
          m_context.BuildTemplate(replacementTemplate, workingResultStructure, replacement);
          ScTemplateResultItem templateResult;
          m_context.GenerateByTemplate(replacementTemplate, templateResult);
          ScStructure generatedStruct = m_context.GenerateStructure();
          structuresToRemove.insert(generatedStruct);
          auto templateReplacements = templateResult.GetReplacements();
          for (size_t i = 0; i < templateResult.Size(); ++i)
          {
            generatedStruct << templateResult[i];
          }
          ScTemplateSearchResult searchResult;

          if (m_context.SearchByTemplate(targetSituationTemplate, searchResult) &&
              isGeneratedStructureFound(generatedStruct, searchResult))
          {
            suitableMethods.insert(solvingMethod);
            break;
          }
        }
      }
      catch (std::exception & e)
      {
        SC_AGENT_LOG_WARNING(e.what());
      }
    }

    formResult(action, suitableMethods);
    removeGeneratedStructures(structuresToRemove, elementsToSave);
  }

  catch (const std::exception & ex)
  {
    SC_AGENT_LOG_ERROR(ex.what());
    return action.FinishWithError();
  }

  return action.FinishSuccessfully();
}

ScAddr FindSolvingMethodAgent::getProblemActionNode(ScAddr const & problemStruct)
{
  ScTemplate problemActionNodeTemplate;
  problemActionNodeTemplate.Triple(
      problemStruct, ScType::EdgeAccessVarPosPerm, ScType::NodeVar >> "_problemActionNode");
  problemActionNodeTemplate.Triple(ScKeynodes::action, ScType::EdgeAccessVarPosPerm, "_problemActionNode");
  ScTemplateSearchResult searchResult;
  if (!m_context.SearchByTemplate(problemActionNodeTemplate, searchResult))
  {
    throw std::runtime_error("Failed to define the problem action node.");
  }
  ScAddr problemActionNode;
  searchResult[0].Get("_problemActionNode", problemActionNode);
  return problemActionNode;
}

ScStructure FindSolvingMethodAgent::getTargetSituationTemplate(ScAddr const & problemActionNode)
{
  ScIterator5Ptr it5 = m_context.CreateIterator5(
      problemActionNode,
      ScType::EdgeDCommonConst,
      ScType::NodeConstStruct,
      ScType::EdgeAccessConstPosPerm,
      SearchKeynodes::nrel_target_situation);
  if (!it5->Next())
  {
    throw std::runtime_error("Failed to define the target situation template.");
  }
  ScAddr targetSituationTemplate = it5->Get(2);
  return m_context.ConvertToStructure(targetSituationTemplate);
}

ScAddr FindSolvingMethodAgent::getProblemConcept(ScAddr const & problemStruct)
{
  ScTemplate scTemplate;
  scTemplate.Triple(ScType::NodeVarClass >> "_problemConcept", ScType::EdgeAccessVarPosPerm, problemStruct);
  scTemplate.Quintuple(
      SearchKeynodes::concept_problem,
      ScType::EdgeDCommonVar,
      "_problemConcept",
      ScType::EdgeAccessVarPosPerm,
      ScKeynodes::nrel_inclusion);

  ScTemplateSearchResult searchResult;

  if (m_context.SearchByTemplate(scTemplate, searchResult))
  {
    ScAddr problemConcept;
    searchResult[0].Get("_problemConcept", problemConcept);
    return problemConcept;
  }

  // in case if problem belongs to 'concept_problem' only
  else
  {
    ScIterator3Ptr it3 =
        m_context.CreateIterator3(SearchKeynodes::concept_problem, ScType::EdgeAccessConstPosPerm, problemStruct);
    if (it3->Next())
    {
      return SearchKeynodes::concept_problem;
    }
  }

  throw std::runtime_error("Input structure does not belong to concept problem");
}

ScAddr FindSolvingMethodAgent::getSolvingMethodWorkingResultTemplate(ScAddr const & solvingMethod)
{
  ScIterator5Ptr it5 = m_context.CreateIterator5(
      solvingMethod,
      ScType::EdgeDCommonConst,
      ScType::EdgeDCommonConst,
      ScType::EdgeAccessConstPosPerm,
      SearchKeynodes::nrel_condition_of_use_and_result);

  if (!it5->Next())
  {
    throw std::runtime_error("Problem solving method does not contain condition of use and result templates");
  }

  ScAddr conditionOfUseAndResultEdge = it5->Get(2);
  if (m_context.GetElementType(conditionOfUseAndResultEdge) == ScType::EdgeDCommonConst)
  {
    ScAddr workingResultTemplate = m_context.GetArcTargetElement(conditionOfUseAndResultEdge);
    if (m_context.GetElementType(workingResultTemplate) == ScType::NodeConstStruct)
    {
      return workingResultTemplate;
    }
    throw std::runtime_error("Problem solving method has incorrect working result template");
  }

  throw std::runtime_error("Problem solving method has incorrect condition of use and result edge");
}

bool FindSolvingMethodAgent::isGeneratedStructureFound(
    ScStructure const & generatedStruct,
    ScTemplateSearchResult const & searchResult)
{
  bool isFound;
  for (size_t i = 0; i < searchResult.Size(); i++)
  {
    isFound = true;
    ScTemplateResultItem resultItem;
    searchResult.Get(i, resultItem);
    for (size_t j = 0; j < resultItem.Size(); j++)
    {
      ScAddr el;
      resultItem.Get(j, el);
      if (!m_context.CheckConnector(generatedStruct, el, ScType::EdgeAccessConstPosPerm))
      {
        isFound = false;
        break;
      }
    }
    if (isFound)
    {
      break;
    }
  }
  return isFound;
}

void FindSolvingMethodAgent::formResult(ScAction & action, ScAddrSet const & suitableMethods)
{
  ScAddr resEdge;
  if (suitableMethods.empty())
  {
    action.SetResult(SearchKeynodes::empty_set);
  }
  else
  {
    ScStructure resultStruct = m_context.GenerateStructure();
    for (auto const & method : suitableMethods)
    {
      resultStruct << method;
    }
    action.SetResult(resultStruct);
  }
}

void FindSolvingMethodAgent::removeGeneratedStructures(
    ScAddrSet const & structuresToRemove,
    ScAddrSet const & elementsToSave)
{
  for (auto structure : structuresToRemove)
  {
    ScIterator3Ptr it3 = m_context.CreateIterator3(structure, ScType::EdgeAccessConstPosPerm, ScType::Unknown);
    while (it3->Next())
    {
      ScAddr element = it3->Get(2);
      if (elementsToSave.find(element) == elementsToSave.end())
      {
        m_context.EraseElement(element);
      }
    }
    m_context.EraseElement(structure);
  }
}
