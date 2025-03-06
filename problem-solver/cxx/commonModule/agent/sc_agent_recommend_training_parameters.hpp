#pragma once

#include <sc-memory/sc_agent.hpp>

class RecommendTrainingParametersAgent: public ScActionInitiatedAgent
{
public:
  ScAddr GetActionClass() const override;

  ScResult DoProgram(ScAction & action) override;

  void adjustNumberEpochs(float& number_epochs, const std::vector<std::string>& accuracy, const std::vector<std::string>& loss);

  void adjustLearningRate(float& learning_rate, const std::vector<std::string>& accuracy, const std::vector<std::string>& loss);

  void adjustBatchSize(float& batch_size, const std::vector<std::string>& loss);
};