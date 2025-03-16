#pragma once

#include <sc-memory/sc_agent.hpp>
#include <sc-memory/sc_memory.hpp>

namespace searchModule
{
class FindSolvingMethodAgent : public ScActionInitiatedAgent
{
public:
  ScAddr GetActionClass() const override;

  ScResult DoProgram(ScActionInitiatedEvent const & event, ScAction & action) override;

private:
  ScStructure getTargetSituationTemplate(ScAddr const & problemStruct);
  ScAddr getProblemActionNode(ScAddr const & problemStruct);
  ScAddr getProblemConcept(ScAddr const & problemStruct);
  ScAddr getSolvingMethodWorkingResultTemplate(ScAddr const & solvingMethod);
  void formResult(ScAction & action, ScAddrSet const & suitableMethods);
  void removeGeneratedStructures(ScAddrSet const & structuresToRemove, ScAddrSet const & elementsToSave);
};
}  // namespace searchModule