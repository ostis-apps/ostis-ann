/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "momoModule.hpp"
#include "keynodes/keynodes.hpp"
#include "agents/ReportGeneration.hpp"
#include "agents/PatientReport.hpp"
#include "agents/StudyReport.hpp"

using namespace momoModule;

SC_IMPLEMENT_MODULE(MomoModule)

sc_result MomoModule::InitializeImpl()
{
  if (!momoModule::Keynodes::InitGlobal())
    return SC_RESULT_ERROR;

  SC_AGENT_REGISTER(ReportGeneration)
          SC_AGENT_REGISTER(PatientReport)
          SC_AGENT_REGISTER(StudyReport)

  return SC_RESULT_OK;
}

sc_result MomoModule::ShutdownImpl()
{
  SC_AGENT_UNREGISTER(ReportGeneration)
          SC_AGENT_UNREGISTER(PatientReport)
          SC_AGENT_UNREGISTER(StudyReport)

  return SC_RESULT_OK;
}
