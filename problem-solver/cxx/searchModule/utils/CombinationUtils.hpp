#pragma once

#include <sc-memory/sc_agent.hpp>

class CombinationUtils
{
public:
  static std::vector<ScTemplateParams> getAllReplacementCombinations(
      ScAddrVector const & substitutes,
      ScAddrVector const & variables);

private:
  static void generateCombinations(
      const ScAddrVector & arr,
      size_t length,
      ScAddrVector & current,
      std::vector<ScAddrVector> & result);
};