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
  ScAddr getTargetSituationTemplate(ScAddr problemStruct, ScMemoryContext & context);
};
}  // namespace searchModule