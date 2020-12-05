/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include "cawModule.hpp"

SC_IMPLEMENT_MODULE(ClassifierAnswerWriterAgentModule)

sc_result ClassifierAnswerWriterAgentModule::InitializeImpl()
{
  m_cawService.reset(new ClassifierAnswerWriterAgentPythonService("ClassifierAnswerWriterAgent/ClassifierAnswerWriterModule.py"));
  m_cawService->Run();
  return SC_RESULT_OK;
}

sc_result ClassifierAnswerWriterAgentModule::ShutdownImpl()
{
  m_cawService->Stop();
  m_cawService.reset();
  return SC_RESULT_OK;
}
