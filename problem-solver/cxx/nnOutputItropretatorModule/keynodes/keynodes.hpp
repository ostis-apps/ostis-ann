/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#pragma once

#include "sc-memory/cpp/sc_addr.hpp"
#include "sc-memory/cpp/sc_object.hpp"

#include "keynodes.generated.hpp"

namespace nnOutputItropretator
{

class Keynodes : public ScObject
{
  SC_CLASS()
  SC_GENERATED_BODY()

public:

  SC_PROPERTY(Keynode("question_nn_output_itropretator"), ForceCreate)
  static ScAddr question_nn_output_itropretator;

  SC_PROPERTY(Keynode("rrel_1"), ForceCreate)
  static ScAddr rrel_1;

  SC_PROPERTY(Keynode("rrel_2"), ForceCreate)
  static ScAddr rrel_2;

  SC_PROPERTY(Keynode("nrel_nn_answer"), ForceCreate)
  static ScAddr nrel_nn_answer;

  SC_PROPERTY(Keynode("image"), ForceCreate)
  static ScAddr image;
  
  SC_PROPERTY(Keynode("action_use_ann"), ForceCreate)
  static ScAddr action_use_ann;

  SC_PROPERTY(Keynode("nrel_semantic_conext"), ForceCreate)
  static ScAddr nrel_semantic_conext;
};

} // namespace nnOutputItropretator
