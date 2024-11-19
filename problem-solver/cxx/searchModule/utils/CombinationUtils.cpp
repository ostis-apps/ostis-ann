#include "CombinationUtils.hpp"

std::vector<ScTemplateParams> CombinationUtils::getAllReplacementCombinations(
    ScAddrVector const & substitutes,
    ScAddrVector const & variables)
{
  std::vector<std::vector<ScAddr>> combinations;
  std::vector<ScAddr> current;
  generateCombinations(substitutes, variables.size(), current, combinations);
  std::vector<ScTemplateParams> result;
  for (auto combination : combinations)
  {
    ScTemplateParams replacement;
    for (size_t i = 0; i < variables.size(); i++)
    {
      replacement.Add(variables[i], combination[i]);
    }
    result.push_back(replacement);
  }
  return result;
}

void CombinationUtils::generateCombinations(
    const ScAddrVector & arr,
    size_t length,
    ScAddrVector & current,
    std::vector<ScAddrVector> & result)
{
  if (current.size() == length)
  {
    result.push_back(current);
    return;
  }

  for (size_t i = 0; i < arr.size(); ++i)
  {
    current.push_back(arr[i]);
    generateCombinations(arr, length, current, result);
    current.pop_back();
  }
}
