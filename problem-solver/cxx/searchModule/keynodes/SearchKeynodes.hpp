#pragma once

#include <sc-memory/sc_keynodes.hpp>

namespace searchModule
{
class SearchKeynodes
{
public:
  static inline ScKeynode const action_find_problem_solving_method{
      "action_find_problem_solving_method",
      ScType::NodeConstClass};

  static inline ScKeynode const nrel_result{"nrel_result", ScType::NodeConstNoRole};

  static inline ScKeynode const empty_set{"empty_set", ScType::NodeConstClass};

  static inline ScKeynode const nrel_target_situation{"nrel_target_situation", ScType::NodeConstNoRole};

  static inline ScKeynode const concept_problem{"concept_problem", ScType::NodeConstClass};

  static inline ScKeynode const nrel_class_of_can_be_solved_problems{
      "nrel_class_of_can_be_solved_problems",
      ScType::NodeConstNoRole};

  static inline ScKeynode const concept_problem_solving_method{
      "concept_problem_solving_method",
      ScType::NodeConstClass};

  static inline ScKeynode const nrel_condition_of_use_and_result{
      "nrel_condition_of_use_and_result",
      ScType::NodeConstNoRole};
};
}  // namespace searchModule