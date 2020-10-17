/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#pragma once

#include "sc-memory/cpp/sc_addr.hpp"
#include "sc-memory/cpp/sc_object.hpp"

#include "keynodes.generated.hpp"

namespace exampleModule
{

class Keynodes : public ScObject
{
  SC_CLASS()
  SC_GENERATED_BODY()

public:

  SC_PROPERTY(Keynode("question_find_subdividing"), ForceCreate)
  static ScAddr question_find_subdividing;

  SC_PROPERTY(Keynode("nrel_subdividing"), ForceCreate)
  static ScAddr nrel_subdividing;

  SC_PROPERTY(Keynode("question_run_ann"), ForceCreate)
  static ScAddr question_run_ann;

  SC_PROPERTY(Keynode("concept_ann"), ForceCreate)
  static ScAddr concept_ann;

  SC_PROPERTY(Keynode("concept_file"), ForceCreate)
  static ScAddr concept_file;

  SC_PROPERTY(Keynode("nrel_processing_result"), ForceCreate)
  static ScAddr nrel_processing_result;
  
  SC_PROPERTY(Keynode("nrel_api_idtf"), ForceCreate)
  static ScAddr nrel_api_idtf;

  SC_PROPERTY(Keynode("nrel_extension"), ForceCreate)
  static ScAddr nrel_extension;

  SC_PROPERTY(Keynode("rrel_1"), ForceCreate)
  static ScAddr rrel_1;

  SC_PROPERTY(Keynode("rrel_2"), ForceCreate)
  static ScAddr rrel_2;

};

} // namespace exampleModule
