/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include <sc-memory/cpp/sc_stream.hpp>
#include <sc-kpm/sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/GenerationUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/AgentUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/CommonUtils.hpp>

#include "ReportGeneration.hpp"
#include "keynodes/keynodes.hpp"

using namespace std;
using namespace utils;

namespace momoModule
{

SC_AGENT_IMPLEMENTATION(ReportGeneration)
{
  if (!edgeAddr.IsValid())
    return SC_RESULT_ERROR;

SC_LOG_INFO("START");

  ScAddr questionNode = ms_context->GetEdgeTarget(edgeAddr);
  ScAddr study = IteratorUtils::getFirstFromSet(ms_context.get(), questionNode);
  if (!study.IsValid())
    return SC_RESULT_ERROR_INVALID_PARAMS;



  ScAddr answer = ms_context->CreateNode(ScType::NodeConstStruct);



   ScIterator5Ptr iterator5 = ms_context->Iterator5(study, ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_patients_study);

ScAddr patient;
  if (iterator5->Next())
  {
   patient = iterator5->Get(2);
  }


ScAddr patient_reportSC= AgentUtils::initAgentAndWaitResult(ms_context.get(), Keynodes::question_patient_report, { patient });
ScAddr study_reportSC = AgentUtils::initAgentAndWaitResult(ms_context.get(), Keynodes::question_study_report, { study });


string patient_report = CommonUtils::getIdtfValue(ms_context.get(), patient, Keynodes::nrel_patient_report );
string study_report = CommonUtils::getIdtfValue(ms_context.get(), study, Keynodes::nrel_study_report);
SC_LOG_INFO("PATIENT");
SC_LOG_INFO(patient_report);
SC_LOG_INFO("STUDY");
SC_LOG_INFO(study_report);

string common_report = patient_report+" \n "+study_report;
SC_LOG_INFO("COMMON");
SC_LOG_INFO(study_report);




ScAddr answer_link = ms_context->CreateLink();
string value = common_report;

ScStreamPtr stream;
stream.reset(new ScStream(value.c_str(),(sc_uint32) value.size(), SC_STREAM_FLAG_READ ));
ms_context->SetLinkContent(answer_link, *stream);

ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, answer_link);

ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, patient_reportSC);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, study_reportSC);
SC_LOG_INFO("END");

  AgentUtils::finishAgentWork(ms_context.get(), questionNode, answer);
  return SC_RESULT_OK;
}
}
