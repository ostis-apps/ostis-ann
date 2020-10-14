/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include <iostream>
#include <algorithm>

#include <sc-memory/cpp/sc_stream.hpp>
#include <sc-memory/cpp/sc_link.hpp>

#include <sc-kpm/sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/AgentUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/CommonUtils.hpp>
#include <sc-kpm/sc-agents-common/keynodes/coreKeynodes.hpp>

#include "RunAnnAgent.hpp"
#include "keynodes/keynodes.hpp"

#include "curl/curl.h"
#include <string.h>

#include <curlpp/cURLpp.hpp>
#include <curlpp/Easy.hpp>
#include <curlpp/Options.hpp>
#include <curlpp/Exception.hpp>
#include <curlpp/Infos.hpp>

using namespace utils;
using namespace std;

namespace exampleModule
{

struct ImplementationState {
	string annName;
	string moduleName;
	string fileName;

	ScAddr annNode;
	ScAddr moduleNode;
	ScAddr fileNode;
};

ImplementationState state;
const uint ANN_NODE_INVALID = 1;
const uint ANN_NOT_FOUND = 2;
const uint MODULE_NODE_INVALID = 3;
const uint MODULE_NOT_FOUND = 4;
const uint FILE_NODE_INVALID = 5;
const uint FILE_NOT_SUPPORTED = 6;
const uint PROCESSING_ERROR = 7;

ScAddr createAnswer(ScMemoryContext* ms_context, string result)
{
	ScAddr answerStructNode = ms_context->CreateNode(ScType::NodeConstStruct);
	ScAddr answerLink = ms_context->CreateLink();

	if (answerLink.IsValid())
	{
        ScStreamPtr stream;
        stream.reset(new ScStream((sc_char*)&result, sizeof(result), SC_STREAM_FLAG_READ | SC_STREAM_FLAG_SEEK));
        ms_context->SetLinkContent(answerLink, *stream);

		ScAddr annAnswerEdge = ms_context->CreateEdge(ScType::EdgeDCommonConst, state.annNode, answerLink);
		ScAddr annAnswerEdgeRelation = ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Keynodes::nrel_processing_result, annAnswerEdge);

		ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answerStructNode, answerLink);
		ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answerStructNode, state.annNode);
		ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answerStructNode, annAnswerEdge);
		ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answerStructNode, annAnswerEdgeRelation);
		ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answerStructNode, Keynodes::nrel_processing_result);
	}

	return answerLink;
}

string get(string route)
{
	using namespace curlpp::Options;
	using namespace std::placeholders;

	curlpp::Cleanup cleaner;
	curlpp::Easy getRequest;

	getRequest.setOpt(Verbose(true));
	getRequest.setOpt(Url("http://127.0.0.1:5000/" + route));
	getRequest.perform();

    ostringstream response;
    response << getRequest;

    return string(response.str());
}

string post(string route, string body)
{
	using namespace curlpp::Options;
	using namespace std::placeholders;

	curlpp::Easy postRequest;

    std::list<std::string> header;
    header.push_back("Content-Type: application/json");

	postRequest.setOpt(Verbose(true));
	postRequest.setOpt(Url("http://127.0.0.1:5000/" + route));
    postRequest.setOpt(HttpHeader(header));
    postRequest.setOpt(PostFields(body));
    postRequest.setOpt(PostFieldSize(body.size()));
    postRequest.perform();

    std::ostringstream response;
    response << postRequest;

    return string(response.str());
}

uint validateModule(ScMemoryContext* ms_context)
{
	bool isModuleNodeValid = ms_context->HelperCheckEdge(Keynodes::concept_module, state.moduleNode, ScType::EdgeAccessConstPosPerm);

	if (!isModuleNodeValid)
	{
		return MODULE_NODE_INVALID;
	}

	state.moduleName = CommonUtils::getIdtfValue(ms_context, state.moduleNode, Keynodes::nrel_unique_name);
	string properties = get(state.moduleName);

	if (properties.compare("") != 0)
	{
		return MODULE_NOT_FOUND;
	}

	return 0;
}

uint validateAnn(ScMemoryContext* ms_context)
{
	bool isAnnNodeValid = ms_context->HelperCheckEdge(Keynodes::concept_ann, state.annNode, ScType::EdgeAccessConstPosPerm);

	if (!isAnnNodeValid)
	{
		return ANN_NODE_INVALID;
	}
	
	state.annName = CommonUtils::getIdtfValue(ms_context, state.annNode, Keynodes::nrel_unique_name);
	string properties = get(state.moduleName + "/" + state.annName);

	if (properties.compare("") != 0)
	{
		return ANN_NOT_FOUND;
	}

	return 0;
}

uint validateFile(ScMemoryContext* ms_context)
{
	bool isFileNodeValid = ms_context->HelperCheckEdge(Keynodes::concept_file, state.fileNode, ScType::EdgeAccessConstPosPerm);

	if (!isFileNodeValid)
	{
		return FILE_NODE_INVALID;
	}

	state.fileName = CommonUtils::getIdtfValue(ms_context, state.fileNode, Keynodes::nrel_unique_name);
	string extension = state.fileName.substr(state.fileName.find('.') + 1);
	string extensions = get(state.annName + "/extensions");
	
	if (extensions.find("\"" + extension + "\"") == string::npos)
	{
		return FILE_NOT_SUPPORTED;
	}

	return 0;
}

string runAnn(ScMemoryContext* ms_context)
{
	string response = post(state.moduleName + "/" + state.annName, state.fileName);

	return response;
}

SC_AGENT_IMPLEMENTATION(RunAnnAgent)
{
	if (!edgeAddr.IsValid())
	{
		return SC_RESULT_ERROR;
	}

	ScAddr questionNode = ms_context->GetEdgeTarget(edgeAddr);
	state.annNode = IteratorUtils::getFirstByOutRelation(ms_context.get(), questionNode, Keynodes::rrel_1);
	state.moduleNode = IteratorUtils::getFirstByInRelation(ms_context.get(), state.annNode, Keynodes::nrel_module);
	state.fileNode = IteratorUtils::getFirstByOutRelation(ms_context.get(), questionNode, Keynodes::rrel_2);

	if (!(state.annNode.IsValid() && state.fileNode.IsValid() && state.moduleNode.IsValid()))
	{
		std::cout << "Params missing/invalid" << endl;
		return SC_RESULT_ERROR_INVALID_PARAMS;
	}

	uint moduleValidationCode = validateModule(ms_context.get());

	if (moduleValidationCode != 0)
	{
		switch (moduleValidationCode)
		{
			case MODULE_NODE_INVALID:
			{
				std::cout << "Module node don't belong to proper class" << endl;
				break;
			}
			case MODULE_NOT_FOUND:
			{
				std::cout << "Module is not supported" << endl;
				break;
			}
		}

		return SC_RESULT_ERROR_INVALID_PARAMS;
	}

	uint annValidationCode = validateAnn(ms_context.get());
	uint fileValidationCode = validateFile(ms_context.get());

	if (annValidationCode != 0)
	{
		switch (annValidationCode)
		{
			case ANN_NODE_INVALID:
			{
				std::cout << "ANN node don't belong to proper class" << endl;
				break;
			}
			case ANN_NOT_FOUND:
			{
				std::cout << "ANN is not supported" << endl;
				break;
			}
		}

		return SC_RESULT_ERROR_INVALID_PARAMS;
	}

	if (fileValidationCode != 0)
	{
		switch (fileValidationCode)
		{
			case FILE_NODE_INVALID:
			{
				std::cout << "File node don't belong to proper class" << endl;
				break;
			}
			case ANN_NOT_FOUND:
			{
				std::cout << "File extension for ANN given is not supported" << endl;
				break;
			}
		}
		
		return SC_RESULT_ERROR_INVALID_PARAMS;
	}

	std::cout << "OHOHO!" << endl;

	string processingResponse = runAnn(ms_context.get());
	ScAddr answerLink = createAnswer(ms_context.get(), processingResponse);

	return answerLink.IsValid() ? SC_RESULT_OK : SC_RESULT_ERROR;
}

}
