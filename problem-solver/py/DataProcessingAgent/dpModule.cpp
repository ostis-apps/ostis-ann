/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "dpModule.hpp"

SC_IMPLEMENT_MODULE(DataProcessingAgentModule)

sc_result DataProcessingAgentModule::InitializeImpl()
{
  m_dpService.reset(new DataProcessingAgentPythonService("DataProcessingAgent/DataProcessingModule.py"));
  m_dpService->Run();
  return SC_RESULT_OK;
}

sc_result DataProcessingAgentModule::ShutdownImpl()
{
  m_dpService->Stop();
  m_dpService.reset();
  return SC_RESULT_OK;
}
