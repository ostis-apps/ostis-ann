/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/
#include <iostream>
#include <sstream>
#include <sc-memory/cpp/sc_stream.hpp>
#include <sc-kpm/sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/AgentUtils.hpp>

#include "nnOutputItropretatorAgent.hpp"
#include "keynodes/keynodes.hpp"


using namespace std;
using namespace utils;

namespace nnOutputItropretator
{

SC_AGENT_IMPLEMENTATION(NNOutputItropretatorAgent)
{
  if (!edgeAddr.IsValid())
    return SC_RESULT_ERROR;

  ScAddr questionNode = ms_context->GetEdgeTarget(edgeAddr);

  ScAddr image = IteratorUtils::getFirstByOutRelation(ms_context.get(), questionNode, Keynodes::rrel_1);
  ScAddr nn_result = IteratorUtils::getFirstByOutRelation(ms_context.get(), questionNode, Keynodes::rrel_2);


  if(!ms_context->HelperCheckEdge(Keynodes::image, image, ScType::EdgeAccessConstPosPerm))
   return SC_RESULT_ERROR_INVALID_PARAMS;

  if(!ms_context->HelperCheckEdge(Keynodes::action_use_ann, nn_result, ScType::EdgeAccessConstPosPerm))
   return SC_RESULT_ERROR_INVALID_PARAMS;

  ScIterator5Ptr iterator5 = ms_context->Iterator5(nn_result, ScType::EdgeDCommonConst, ScType::NodeConstTuple, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_nn_answer);

  ScAddr set_of_answers;
  if (iterator5->Next())
  {
   set_of_answers = iterator5->Get(2);
  }
  else
   return SC_RESULT_ERROR_INVALID_PARAMS;


  ScIterator3Ptr iterator3 = ms_context->Iterator3(set_of_answers, ScType::EdgeAccessConstPosPerm, ScType::NodeConstTuple);

  ScAddr answer_node;
  ScAddr temp_set_answer_node;
  int max_percent=0;
  int temp_max_percent=0;

  while(iterator3->Next())
  {
      std::cout<<1;
      temp_set_answer_node= iterator3->Get(2);
      ScAddr temp_answer_node = IteratorUtils::getFirstByOutRelation(ms_context.get(), temp_set_answer_node, Keynodes::rrel_2);

      string number_str = ms_context->HelperGetSystemIdtf(temp_answer_node);
      temp_max_percent = stoi(number_str);

      if(temp_max_percent> max_percent)
      {
          max_percent = temp_max_percent;
          answer_node =  IteratorUtils::getFirstByOutRelation(ms_context.get(), temp_set_answer_node, Keynodes::rrel_1);
      }
  }

  ScAddr semantic_context = ms_context->CreateNode(ScType::NodeConstStruct);
  ScAddr conectionEdge = ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, semantic_context, answer_node);

  ScAddr annAnswerEdge = ms_context->CreateEdge(ScType::EdgeDCommonConst, image, semantic_context);
  ScAddr annAnswerEdgeRelation = ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Keynodes::nrel_semantic_conext, annAnswerEdge);

  ScAddr answer = ms_context->CreateNode(ScType::NodeConstStruct);

  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, answer_node);
  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, semantic_context);
  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, image);
  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, annAnswerEdge);
  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, annAnswerEdgeRelation);
  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, Keynodes::nrel_semantic_conext);
  ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, conectionEdge);

  AgentUtils::finishAgentWork(ms_context.get(), questionNode, answer);
  return SC_RESULT_OK;
}
}
