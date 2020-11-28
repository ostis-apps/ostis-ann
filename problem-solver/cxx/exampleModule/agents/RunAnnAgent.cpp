/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include <iostream>
#include <algorithm>
#include <string.h>
#include <sys/stat.h>
#include <vector>
#include <iterator>

#include <sc-memory/cpp/sc_stream.hpp>
#include <sc-memory/cpp/sc_link.hpp>

#include <sc-kpm/sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/AgentUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/CommonUtils.hpp>
#include <sc-kpm/sc-agents-common/keynodes/coreKeynodes.hpp>

#include "RunAnnAgent.hpp"
#include "keynodes/keynodes.hpp"

#include "curl/curl.h"

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
	string fileName;
	string fileExtension;

	ScAddr annNode;
	ScAddr fileNode;
};

ImplementationState state;
const uint ANN_NODE_INVALID = 1;
const uint ANN_NOT_FOUND = 2;
const uint FILE_NODE_INVALID = 5;
const uint FILE_NOT_SUPPORTED = 6;

std::vector<unsigned char> readImage(string path) {
	// Define file stream object, and open the file
	std::ifstream file(path, ios::binary);

	// Prepare iterator pairs to iterate the file content
	std::istream_iterator<unsigned char> begin(file), end;

	// Reading the file content using the iterator
	std::vector<unsigned char> buffer(begin, end);

	std::copy(buffer.begin(), buffer.end(), std::ostream_iterator<unsigned int>(std::cout, ","));

	return buffer;
}

void createAnswers(ScMemoryContext* ms_context, string result)
{
	// Process text result
	{
		ScAddr textAnswerStructNode = ms_context->CreateNode(ScType::NodeConstStruct);
		ScAddr textAnswerLink = ms_context->CreateLink();
	
		if (textAnswerLink.IsValid())
		{
			// ScStreamMemory wtf;
			// ScStreamPtr stream = ScStreamConverter::StreamFromString(result, wtf);
			// std::cout << "Content in stream: " << result << endl;
			// ms_context->SetLinkContent(textAnswerLink, *stream);
	
			ScAddr annAnswerEdge = ms_context->CreateEdge(ScType::EdgeDCommonConst, state.annNode, textAnswerLink);
			ScAddr annAnswerEdgeRelation = ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Keynodes::nrel_processing_result, annAnswerEdge);
	
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, textAnswerStructNode, textAnswerLink);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, textAnswerStructNode, state.annNode);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, textAnswerStructNode, annAnswerEdge);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, textAnswerStructNode, annAnswerEdgeRelation);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, textAnswerStructNode, Keynodes::nrel_processing_result);
		}
	}

	// Process image result
	{
		string relativeMove = "../../../../";
		string imagePath = relativeMove + "kb/neural_network_instances/" + state.annName + "/data/" + state.fileName + "." + state.fileExtension + "_processed.png";
		
		std::cout << relativeMove + imagePath << endl;

		struct stat buffer;
		int statResult = stat((relativeMove + imagePath).c_str(), &buffer);

		std::cout << "Stat result: " << statResult << endl;

		bool isImageExists = statResult == 0;

		if (isImageExists)
		{
			std::cout << "Image result can be found at " << imagePath << endl;

			ScAddr imageAnswerStructNode = ms_context->CreateNode(ScType::NodeConstStruct);
			ScAddr imageAnswerLink = ms_context->CreateLink();

			std::vector<unsigned char> imageBytes = readImage(relativeMove + imagePath);
			std::string imageBytesString(imageBytes.begin(), imageBytes.end());
			
			// ScStreamMemory wtf;
			// ScStreamPtr stream = ScStreamConverter::StreamFromString(imageBytesString, wtf);
			// ms_context->SetLinkContent(imageAnswerLink, *stream);
	
			ScAddr annAnswerEdge = ms_context->CreateEdge(ScType::EdgeDCommonConst, state.annNode, imageAnswerLink);
			ScAddr annAnswerEdgeRelation = ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Keynodes::nrel_processing_result, annAnswerEdge);
	
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, imageAnswerStructNode, imageAnswerLink);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, imageAnswerStructNode, state.annNode);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, imageAnswerStructNode, annAnswerEdge);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, imageAnswerStructNode, annAnswerEdgeRelation);
			ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, imageAnswerStructNode, Keynodes::nrel_processing_result);
		}
	}
}

string get(string route)
{
	using namespace curlpp::Options;
	using namespace std::placeholders;

	curlpp::Easy getRequest;
    string url = "http://127.0.0.1:5000/" + route;

	getRequest.setOpt(Url("http://127.0.0.1:5000/" + route));

	try {
		getRequest.perform();		
	}
    catch (curlpp::LibcurlRuntimeError error) {
    	std::cerr << "Error performing GET " << url << " request! what(): " << error.what() << endl;
    	return "";
    }

    ostringstream response;
    response << getRequest;

    return string(response.str());
}

string post(string route, string body)
{
	using namespace curlpp::Options;
	using namespace std::placeholders;

    std::list<std::string> header;
    header.push_back("Content-Type: application/json");

	curlpp::Easy postRequest;
    string url = "http://127.0.0.1:5000/" + route;

	postRequest.setOpt(Url(url));
    postRequest.setOpt(HttpHeader(header));
    postRequest.setOpt(PostFields(body));
    postRequest.setOpt(PostFieldSize(body.size()));

    try {
    	postRequest.perform();
    }
    catch (curlpp::LibcurlRuntimeError error) {
    	std::cerr << "Error performing POST " << url << " request! what(): " << error.what() << endl;
    	return "";
    }

    std::ostringstream response;
    response << postRequest;

    return string(response.str());
}

uint validateAnn(ScMemoryContext* ms_context)
{
	bool isAnnNodeValid = ms_context->HelperCheckEdge(Keynodes::concept_neural_network_in_graphical_representation, state.annNode, ScType::EdgeAccessConstPosPerm);

	if (!isAnnNodeValid)
	{
		return ANN_NODE_INVALID;
	}

	ScAddr annNameLink = IteratorUtils::getFirstByOutRelation(ms_context, state.annNode, Keynodes::nrel_api_idtf);
	state.annName =  CommonUtils::readString(ms_context, annNameLink);
	string properties = get(state.annName);

	if (properties.compare("") == 0)
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

	ScAddr fileNameLink = IteratorUtils::getFirstByOutRelation(ms_context, state.fileNode, Keynodes::nrel_file_name);
	ScAddr fileExtensionLink = IteratorUtils::getFirstByOutRelation(ms_context, state.fileNode, Keynodes::nrel_file_extension);
	state.fileName = CommonUtils::readString(ms_context, fileNameLink);
	state.fileExtension = CommonUtils::readString(ms_context, fileExtensionLink);
	string extensions = get(state.annName + "/extensions");
	
	if (extensions.find("\"" + state.fileExtension + "\"") == string::npos)
	{
		return FILE_NOT_SUPPORTED;
	}

	return 0;
}

string runAnn()
{
	string body = "{ \"filename\": \"" + state.fileName + "." + state.fileExtension + "\" }";
	string response = post(state.annName, body);

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
	state.fileNode = IteratorUtils::getFirstByOutRelation(ms_context.get(), questionNode, Keynodes::rrel_2);

	if (!(state.annNode.IsValid() && state.fileNode.IsValid()))
	{
		std::cout << "Params missing/invalid" << endl;
		return SC_RESULT_ERROR_INVALID_PARAMS;
	}

	uint annValidationCode = validateAnn(ms_context.get());

	if (annValidationCode != 0)
	{
		switch (annValidationCode)
		{
			case ANN_NODE_INVALID:
			{
				std::cout << "ANN node don't belong to proper class/have invalid properties" << endl;
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
	
	uint fileValidationCode = validateFile(ms_context.get());

	if (fileValidationCode != 0)
	{
		switch (fileValidationCode)
		{
			case FILE_NODE_INVALID:
			{
				std::cout << "File node don't belong to proper class/have invalid properties" << endl;
				break;
			}
			case FILE_NOT_SUPPORTED:
			{
				std::cout << "File extension for ANN given is not supported" << endl;
				break;
			}
		}
		
		return SC_RESULT_ERROR_INVALID_PARAMS;
	}

	string processingResponse = runAnn();
	createAnswers(ms_context.get(), processingResponse);

	return SC_RESULT_OK;
}

}
