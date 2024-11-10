#pragma once

#include <sc-memory/sc_keynodes.hpp>

namespace searchModule
{
class SearchKeynodes
{
public:
  static inline ScKeynode const action_find_problem_solving_method{"action_find_problem_solving_method", ScType::NodeConstClass};

  static inline ScKeynode const nrel_result{"nrel_result", ScType::NodeConstNoRole};

  static inline ScKeynode const empty_set{"empty_set", ScType::NodeConstClass};

  static inline ScKeynode const action{"action", ScType::NodeConstClass};

  static inline ScKeynode const nrel_target_situation{"nrel_target_situation", ScType::NodeConstNoRole};
};
}  // namespace searchModule