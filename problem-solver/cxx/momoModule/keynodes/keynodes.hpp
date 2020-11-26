/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#pragma once

#include "sc-memory/cpp/sc_addr.hpp"
#include "sc-memory/cpp/sc_object.hpp"

#include "keynodes.generated.hpp"

namespace momoModule
{

class Keynodes : public ScObject
{
  SC_CLASS()
  SC_GENERATED_BODY()

public:



  SC_PROPERTY(Keynode("nrel_patients_study"), ForceCreate)
  static ScAddr nrel_patients_study;

  SC_PROPERTY(Keynode("nrel_patients_hormonal_status"), ForceCreate)
  static ScAddr nrel_patients_hormonal_status;

  SC_PROPERTY(Keynode("nrel_age"), ForceCreate)
  static ScAddr nrel_age;

  SC_PROPERTY(Keynode("concept_hormonal_status"), ForceCreate)
  static ScAddr concept_hormonal_status;

  SC_PROPERTY(Keynode("question_report_generation"), ForceCreate)
  static ScAddr question_report_generation;

  SC_PROPERTY(Keynode("question_patient_report"), ForceCreate)
  static ScAddr question_patient_report;

  SC_PROPERTY(Keynode("nrel_main_idtf"), ForceCreate)
  static ScAddr nrel_main_idtf;

SC_PROPERTY(Keynode("nrel_patient_report"), ForceCreate)
static ScAddr nrel_patient_report;

SC_PROPERTY(Keynode("nrel_study_report"), ForceCreate)
static ScAddr nrel_study_report;

SC_PROPERTY(Keynode("question_study_report"), ForceCreate)
static ScAddr question_study_report;

SC_PROPERTY(Keynode("nrel_image"), ForceCreate)
static ScAddr nrel_image;
SC_PROPERTY(Keynode("nrel_spatial_artefacts"), ForceCreate)
static ScAddr nrel_spatial_artefacts;
SC_PROPERTY(Keynode("nrel_laterality_artefacts"), ForceCreate)
static ScAddr nrel_laterality_artefacts;
SC_PROPERTY(Keynode("nrel_metadata_of_image"), ForceCreate)
static ScAddr nrel_metadata_of_image;
SC_PROPERTY(Keynode("nrel_projection"), ForceCreate)
static ScAddr nrel_projection;
SC_PROPERTY(Keynode("nrel_laterality"), ForceCreate)
static ScAddr nrel_laterality;

SC_PROPERTY(Keynode("concept_projection"), ForceCreate)
static ScAddr concept_projection;
SC_PROPERTY(Keynode("concept_laterality"), ForceCreate)
static ScAddr concept_laterality;
SC_PROPERTY(Keynode("concept_artifact_type"), ForceCreate)
static ScAddr concept_artifact_type;

SC_PROPERTY(Keynode("nrel_shape_of_mass"), ForceCreate)
static ScAddr nrel_shape_of_mass;
SC_PROPERTY(Keynode("nrel_margins_of_mass"), ForceCreate)
static ScAddr nrel_margins_of_mass;
SC_PROPERTY(Keynode("nrel_artifact_size"), ForceCreate)
static ScAddr nrel_artifact_size;
SC_PROPERTY(Keynode("nrel_mass_density"), ForceCreate)
static ScAddr nrel_mass_density;

SC_PROPERTY(Keynode("nrel_calc_distribution"), ForceCreate)
static ScAddr nrel_calc_distribution;

SC_PROPERTY(Keynode("concept_left_laterality"), ForceCreate)
static ScAddr concept_left_laterality;

SC_PROPERTY(Keynode("concept_right_laterality"), ForceCreate)
static ScAddr concept_right_laterality;


};

} // namespace exampleModule
