/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "nnOutputItropretatorModule.hpp"
#include "keynodes/keynodes.hpp"
#include "agents/nnOutputItropretatorAgent.hpp"

using namespace nnOutputItropretator;

SC_IMPLEMENT_MODULE(NNOutputItropretatorModule)

sc_result NNOutputItropretatorModule::InitializeImpl()
{
  if (!nnOutputItropretator::Keynodes::InitGlobal())
    return SC_RESULT_ERROR;

  SC_AGENT_REGISTER(NNOutputItropretatorAgent)

  return SC_RESULT_OK;
}

sc_result NNOutputItropretatorModule::ShutdownImpl()
{
  SC_AGENT_UNREGISTER(NNOutputItropretatorAgent)

  return SC_RESULT_OK;
}
