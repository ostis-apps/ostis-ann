#include "sc_agent_recommend_training_parameters.hpp"

#include "sc-agents-common/utils/IteratorUtils.hpp"

#include "keynodes/Keynodes.hpp"
#include "utils/RelationUtils.hpp"

#include <cmath> 

using namespace commonModule;

ScAddr RecommendTrainingParametersAgent::GetActionClass() const
{
  return Keynodes::action_recommend_training_parameters;
}

ScResult RecommendTrainingParametersAgent::DoProgram(ScAction & action)
{
  auto const & [setAddr] = action.GetArguments<1>();
  if (!m_context.IsElement(setAddr))
  {
    SC_AGENT_LOG_ERROR("Params is not specified.");
    return action.FinishWithError();
  }

  

  ScStructure structure = m_context.GenerateStructure();

  std::string number_ep;
  std::string learning_r;
  std::string batch_s;
  std::string accur;
  std::string los;
  ScAddr nrel_new_value = m_context.SearchElementBySystemIdentifier("nrel_new_value");

  if (!nrel_new_value.IsValid())
  {
    nrel_new_value = m_context.GenerateNode(ScType::NodeConstNoRole);
    m_context.SetElementSystemIdentifier("nrel_new_value", nrel_new_value);
  }
  structure << nrel_new_value;

  //5_1
  
  ScIterator5Ptr const it5_1 = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_number_epochs
  );

  while(it5_1->Next())
  {    
    if (m_context.GetElementType(it5_1->Get(2)).IsLink())
    {
      if (m_context.GetLinkContent(it5_1->Get(2), number_ep))
      {
        ScAddr const & params = it5_1->Get(2);
        structure << params;
      }
    }
    
    SC_AGENT_LOG_DEBUG("params_1 = " + number_ep);  
  }

  //5_2

  ScIterator5Ptr const it5_2 = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_learning_rate
  );

  while(it5_2->Next())
  {    
    if (m_context.GetElementType(it5_2->Get(2)).IsLink())
    {
      if (m_context.GetLinkContent(it5_2->Get(2), learning_r))
      {
        ScAddr const & params = it5_2->Get(2);
        structure << params;
      }
    }

    SC_AGENT_LOG_DEBUG("params_2 = " + learning_r);  
  }

  //5_3

  ScIterator5Ptr const it5_3 = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_batch_size
  );

  while(it5_3->Next())
  {    
    if (m_context.GetElementType(it5_3->Get(2)).IsLink())
    {
      if (m_context.GetLinkContent(it5_3->Get(2), batch_s))
      {
        ScAddr const & params = it5_3->Get(2);
        structure << params;
      }
    }

    SC_AGENT_LOG_DEBUG("params_3 = " + batch_s); 
  }
  
  //5_4
  
  ScIterator5Ptr const it5_4 = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::NodeConst,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_accuracy
  );

  std::map<int, std::string> indexedElements1;

  while(it5_4->Next())
  {    
    ScAddr const & vectorNode = it5_4->Get(2);

    ScIterator5Ptr it5_4_1 = m_context.CreateIterator5(
    vectorNode,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    ScType::NodeConstRole);
    SC_AGENT_LOG_DEBUG("params accuracy: down below");

    while(it5_4_1->Next())
    {
      if (m_context.GetElementType(it5_4_1->Get(2)).IsLink())
      {
        if (m_context.GetLinkContent(it5_4_1->Get(2), accur))
        {
          ScAddr role = it5_4_1->Get(4);

          std::string roleIdtf = m_context.GetElementSystemIdentifier(role);
          int index = std::stoi(roleIdtf.substr(5));
          indexedElements1[index] = accur;
          SC_LOG_DEBUG("Element with index " + std::to_string(index) + " added.");
          SC_LOG_DEBUG(accur);
        }
      }
    }

    
  }

  std::vector<std::string> accuracy;
    for (auto const & [index, element] : indexedElements1)
    {
      accuracy.push_back(element);
    }

  //5_5
  
  ScIterator5Ptr const it5_5 = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::NodeConst,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_loss
  );

  std::map<int, std::string> indexedElements2;

  while(it5_5->Next())
  {    
    ScAddr const & vectorNode = it5_5->Get(2);

    ScIterator5Ptr it5_5_1 = m_context.CreateIterator5(
    vectorNode,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    ScType::NodeConstRole);
    SC_AGENT_LOG_DEBUG("params loss: down below");

    while(it5_5_1->Next())
    {
      if (m_context.GetElementType(it5_5_1->Get(2)).IsLink())
      {
        if (m_context.GetLinkContent(it5_5_1->Get(2), los))
        {
          ScAddr role = it5_5_1->Get(4);

          std::string roleIdtf = m_context.GetElementSystemIdentifier(role);
          int index = std::stoi(roleIdtf.substr(5));
          indexedElements2[index] = los;
          SC_LOG_DEBUG("Element with index " + std::to_string(index) + " added.");
          SC_LOG_DEBUG(los);
        }
      }
    }

    
  }

  std::vector<std::string> loss;
    for (auto const & [index, element] : indexedElements2)
    {
      loss.push_back(element);
    }

  //recommendation realization based on input params

  //float numbers for output sc::links
  float number_epochs = std::stof(number_ep);
  float learning_rate = std::stof(learning_r);
  float batch_size = std::stof(batch_s);
  
  //check rules
  adjustNumberEpochs(number_epochs, accuracy, loss);
  adjustLearningRate(learning_rate, accuracy, loss);
  adjustBatchSize(batch_size, loss);
  
  std::string str_learning_rate = std::to_string(learning_rate);

  //generation output structure with recommendation
  
  ScIterator5Ptr const it5_1_end = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_number_epochs
  );

  while(it5_1_end->Next())
  {
    if (m_context.GetElementType(it5_1_end->Get(2)).IsLink())
    {
      if (m_context.GetLinkContent(it5_1_end->Get(2), number_ep))   //number_ep --- это число "idtf" в объекте линк
      {
        ScAddr const & params = it5_1_end->Get(2);
        structure << params;

        ScAddr recom_number_epochs = m_context.GenerateLink();
        m_context.SetLinkContent(recom_number_epochs, std::to_string(static_cast<int>(number_epochs)));
        structure << recom_number_epochs;

        ScAddr number_epochs_edge = m_context.GenerateConnector(ScType::EdgeDCommonConst, params, recom_number_epochs);
        structure << number_epochs_edge;

        ScAddr no_role_edge = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, nrel_new_value, number_epochs_edge);
        structure << no_role_edge;        
      }
    }
  }

  ScIterator5Ptr const it5_2_end = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_learning_rate
  );

  while(it5_2_end->Next())
  {
    if (m_context.GetElementType(it5_2_end->Get(2)).IsLink())
    {
      if (m_context.GetLinkContent(it5_2_end->Get(2), learning_r))
      {
        ScAddr const & params = it5_2_end->Get(2);
        structure << params;

        ScAddr recom_learing_rate = m_context.GenerateLink();

        size_t pos = str_learning_rate.find('.');
        if (pos != std::string::npos) {
            str_learning_rate.erase(str_learning_rate.find_last_not_of('0') + 1, std::string::npos);
            if (str_learning_rate.back() == '.') {
                str_learning_rate.pop_back();
            }
        }

        m_context.SetLinkContent(recom_learing_rate, str_learning_rate);
        structure << recom_learing_rate;

        ScAddr learning_rate_edge = m_context.GenerateConnector(ScType::EdgeDCommonConst, params, recom_learing_rate);
        structure << learning_rate_edge;

        ScAddr no_role_edge = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, nrel_new_value, learning_rate_edge);
        structure << no_role_edge;        
      }
    }
  }

  ScIterator5Ptr const it5_3_end = m_context.CreateIterator5(
    setAddr,
    ScType::EdgeAccessConstPosPerm,
    ScType::Link,
    ScType::EdgeAccessConstPosPerm,
    Keynodes::rrel_batch_size
  );

  while(it5_3_end->Next())
  {
    if (m_context.GetElementType(it5_3_end->Get(2)).IsLink())
    {
      if (m_context.GetLinkContent(it5_3_end->Get(2), batch_s))
      {
        ScAddr const & params = it5_3_end->Get(2);
        structure << params;

        ScAddr recom_batch_size = m_context.GenerateLink();
        m_context.SetLinkContent(recom_batch_size, std::to_string(static_cast<int>(batch_size)));
        structure << recom_batch_size;

        ScAddr batch_size_edge = m_context.GenerateConnector(ScType::EdgeDCommonConst, params, recom_batch_size);
        structure << batch_size_edge;

        ScAddr no_role_edge = m_context.GenerateConnector(ScType::EdgeAccessConstPosPerm, nrel_new_value, batch_size_edge);
        structure << no_role_edge;        
      }
    }
  }

  action.SetResult(structure);

  return action.FinishSuccessfully();
}

void RecommendTrainingParametersAgent::adjustNumberEpochs(float& number_epochs, const std::vector<std::string>& accuracy, const std::vector<std::string>& loss)
{
    if (accuracy.size() < 2 || loss.size() < 2)
    {
        SC_LOG_ERROR("NEEDED MORE ACCURACY OR LOSS DATA");
        return;
    }
    

    float last_accuracy = std::stof(accuracy[accuracy.size() - 1]);
    float prev_accuracy = std::stof(accuracy[accuracy.size() - 2]);
    
    float last_loss = std::stof(loss[loss.size() - 1]);
    float prev_loss = std::stof(loss[loss.size() - 2]);

    if (last_accuracy >= prev_accuracy + 0.01 && last_loss <= prev_loss)
    {
        number_epochs += 1.0;
    }
    else if (last_accuracy <= prev_accuracy && last_loss >= prev_loss)
    {
        number_epochs -= 1.0;
    }
    else if (last_accuracy < prev_accuracy)
    {
        number_epochs -= 1.0;
    }
}

void RecommendTrainingParametersAgent::adjustLearningRate(float& learning_rate, const std::vector<std::string>& accuracy, const std::vector<std::string>& loss)
{
    if (accuracy.size() < 2 || loss.size() < 2)
    {
        SC_LOG_ERROR("NEEDED MORE ACCURACY OR LOSS DATA");
        return;
    }

    float last_accuracy = std::stof(accuracy[accuracy.size() - 1]);
    float prev_accuracy = std::stof(accuracy[accuracy.size() - 2]);
    
    float last_loss = std::stof(loss[loss.size() - 1]);
    float prev_loss = std::stof(loss[loss.size() - 2]);

    float first_loss = std::stof(loss[0]);
    float second_loss = std::stof(loss[1]);

    if (std::abs(last_accuracy - prev_accuracy) < 0.01 && last_loss <= prev_loss - 0.01)
    {
        learning_rate *= 0.9;   //-10%
    }
    else if (first_loss > 1.0 && second_loss > 1.0)
    {
        learning_rate *= 1.1;
    }
}

void RecommendTrainingParametersAgent::adjustBatchSize(float& batch_size, const std::vector<std::string>& loss)
{
    if (loss.size() < 2)
    {
        SC_LOG_ERROR("NEEDED MORE LOSS DATA");
        return;
    }

    int n = static_cast<int>(std::log2(batch_size));

    float last_loss = std::stof(loss[loss.size() - 1]);
    float prev_loss = std::stof(loss[loss.size() - 2]);

    bool loss_fluctuates = false;
    for (size_t i = 1; i < loss.size(); ++i) {
        float prev_loss = std::stof(loss[i - 1]);
        float curr_loss = std::stof(loss[i]);

        if ((curr_loss > prev_loss && i > 1 && std::stof(loss[i - 2]) > curr_loss) || 
            (curr_loss < prev_loss && i > 1 && std::stof(loss[i - 2]) < curr_loss)) {
            loss_fluctuates = true;
            break;
        }
    }

    if (loss_fluctuates)
    {
        n -= 1;
    }
    else if (last_loss <= prev_loss - 0.01 && last_loss > 0.5 && prev_loss > 0.5)
    {
        n += 1;
    }

    batch_size = std::pow(2, n);
}