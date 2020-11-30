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
#include <string>

#include "PatientReport.hpp"
#include "keynodes/keynodes.hpp"

using namespace std;
using namespace utils;

namespace momoModule
{

bool isHormonalStatus(ScMemoryContext * context, ScAddr  hormonal_status)
{
  return hormonal_status.IsValid()
         &&
         context->HelperCheckEdge(Keynodes::concept_hormonal_status, hormonal_status, ScType::EdgeAccessConstPosPerm);
}

SC_AGENT_IMPLEMENTATION(PatientReport)
{
  if (!edgeAddr.IsValid())
    return SC_RESULT_ERROR;


SC_LOG_INFO("----------patient begin----------");
  ScAddr questionNode = ms_context->GetEdgeTarget(edgeAddr);
  ScAddr patient = IteratorUtils::getFirstFromSet(ms_context.get(), questionNode);
  if (!patient.IsValid())
    return SC_RESULT_ERROR_INVALID_PARAMS;

  //находим гормональный статус пациента

  ScIterator5Ptr iterator5 = ms_context->Iterator5(patient, ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_patients_hormonal_status);

  ScAddr hormonal;
    if (iterator5->Next())
    {
     hormonal = iterator5->Get(2);
    }


    ScAddr hormonal_status;
    ScIterator3Ptr iterator3 = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, hormonal);
    while (iterator3->Next())
    {
        if(isHormonalStatus(ms_context.get(),iterator3->Get(0))==true){
            hormonal_status = iterator3->Get(0);
        }
    }


//находим возраст пациента
    ScIterator5Ptr iterator5age = ms_context->Iterator5(patient, ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_age);

    ScAddr age;
      if (iterator5age->Next())
      {
       age = iterator5age->Get(2);
      }


  ScAddr answer = ms_context->CreateNode(ScType::NodeConstStruct);

//состовляем отчет о пациенте и записываем в линк
  string hormonal_status_str = CommonUtils::getIdtfValue(ms_context.get(), hormonal_status, Keynodes::nrel_main_idtf );
  string age_str = CommonUtils::getIdtfValue(ms_context.get(), patient, Keynodes::nrel_age );
  string pation_rep_str = "hormonal status - " + hormonal_status_str +" \n age - " + age_str;

SC_LOG_INFO(pation_rep_str);
  ScAddr answer_link = ms_context->CreateLink();
  string value = pation_rep_str;

  ScStreamPtr stream;
  stream.reset(new ScStream(value.c_str(),(sc_uint32) value.size(), SC_STREAM_FLAG_READ ));
  ms_context->SetLinkContent(answer_link, *stream);


//формируем ответ
  ScAddr edge_answer = ms_context->CreateEdge(ScType::EdgeDCommonConst, patient, answer_link);

  ScAddr edge_edge_answer = ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Keynodes::nrel_patient_report, edge_answer);


  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, answer_link);
  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, patient);
   ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, edge_answer);
    ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, edge_edge_answer);
     ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer,Keynodes::nrel_patient_report );

SC_LOG_INFO("----------patient end----------");
  AgentUtils::finishAgentWork(ms_context.get(), questionNode, answer);
  return SC_RESULT_OK;
}
}
