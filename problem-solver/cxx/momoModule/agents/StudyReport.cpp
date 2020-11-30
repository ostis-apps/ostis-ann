/*
* This source file is part of an OSTIS project. For the latest info, see http://ostis.net
* Distributed under the MIT License
* (See accompanying file COPYING.MIT or copy at http://opensource.org/licenses/MIT)
*/

#include <sc-memory/cpp/sc_stream.hpp>
#include <sc-kpm/sc-agents-common/utils/IteratorUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/GenerationUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/AgentUtils.hpp>
#include <sc-kpm/sc-agents-common/utils/CommonUtils.hpp>
#include <string>
#include <vector>
#include <iostream>

#include "StudyReport.hpp"
#include "keynodes/keynodes.hpp"

using namespace std;
using namespace utils;

namespace momoModule
{

bool isProjection(ScMemoryContext * context, ScAddr  projection)
{
  return projection.IsValid()
         &&
         context->HelperCheckEdge(Keynodes::concept_projection, projection, ScType::EdgeAccessConstPosPerm);
}


bool isLaterality(ScMemoryContext * context, ScAddr  laterality)
{
  return laterality.IsValid()
         &&
         context->HelperCheckEdge(Keynodes::concept_laterality, laterality, ScType::EdgeAccessConstPosPerm);
}

/*bool isArtifact(ScMemoryContext * context, ScAddr  artifact)
{
    ScAddr artifact_type;
    ScIterator3Ptr artifIT = context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, artifact);
    while (artifIT->Next())
    {
            artifact_type = artifIT->Get(0);
    }

  return artifact_type.IsValid()
         &&
         context->HelperCheckEdge(Keynodes::concept_artifact_type, artifact_type, ScType::EdgeAccessConstPosPerm);
}

bool isArtifactType(ScMemoryContext * context, ScAddr  artifact_type)
{
     return artifact_type.IsValid()
         &&
         context->HelperCheckEdge(Keynodes::concept_artifact_type, artifact_type, ScType::EdgeAccessConstPosPerm);
}*/


SC_AGENT_IMPLEMENTATION(StudyReport)
{
  if (!edgeAddr.IsValid())
    return SC_RESULT_ERROR;


  SC_LOG_INFO("----------study begin----------");

  ScAddr questionNode = ms_context->GetEdgeTarget(edgeAddr);
  ScAddr study = IteratorUtils::getFirstFromSet(ms_context.get(), questionNode);
  if (!study.IsValid())
    return SC_RESULT_ERROR_INVALID_PARAMS;

  ScAddr answer = ms_context->CreateNode(ScType::NodeConstStruct);
  //ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, study);


ScAddr temp = ms_context->CreateNode(ScType::NodeConstStruct);
ScAddr Right = ms_context->CreateNode(ScType::NodeConstStruct);
ScAddr Left = ms_context->CreateNode(ScType::NodeConstStruct);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, temp, Right);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, temp, Left);


string Leftstr = CommonUtils::getIdtfValue(ms_context.get(), Keynodes::concept_left_laterality, Keynodes::nrel_main_idtf );
string Rightstr = CommonUtils::getIdtfValue(ms_context.get(), Keynodes::concept_right_laterality, Keynodes::nrel_main_idtf );

  ScIterator5Ptr imageIT = ms_context->Iterator5(study, ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_image);
  vector<ScAddr> images(4);
    while (imageIT->Next())
    {
     images.push_back(imageIT->Get(2));
    }

    for(int i=0; i<images.size(); i++){
        //ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, images[i]);
    }
    string spatials_report;

    for(int i=0; i<images.size(); i++){
        ScIterator5Ptr metaIT = ms_context->Iterator5(images[i], ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_metadata_of_image);
        ScAddr metadata;
          while (metaIT->Next())
          {
           metadata=metaIT->Get(2);
          }
         // ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, metadata);


          ScIterator5Ptr projIT = ms_context->Iterator5(metadata, ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_projection);
          ScAddr projection;
            while (projIT->Next())
            {
             projection=projIT->Get(2);
            }

            ScAddr projection_type;
            ScIterator3Ptr pro_type = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, projection);
            while (pro_type->Next())
            {
                if(isProjection(ms_context.get(),pro_type->Get(0))==true){
                    projection_type = pro_type->Get(0);
                }
            }




            ScIterator5Ptr latIT = ms_context->Iterator5(metadata, ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_laterality);
            ScAddr laterality;
              while (latIT->Next())
              {
               laterality=latIT->Get(2);
              }

              ScAddr laterality_type;
              ScIterator3Ptr lat_type = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, laterality);
              while (lat_type->Next())
              {
                  if(isLaterality(ms_context.get(),lat_type->Get(0))==true){
                      laterality_type = lat_type->Get(0);
                  }
              }

string laterality_str;
              if(laterality_type.IsValid() && projection_type.IsValid()){
              //ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, projection_type);
              //ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, laterality_type);

               laterality_str = CommonUtils::getIdtfValue(ms_context.get(), laterality_type, Keynodes::nrel_main_idtf );
              string projection_str = CommonUtils::getIdtfValue(ms_context.get(), projection_type, Keynodes::nrel_main_idtf );
              string study_basic_report="latrelity - "+laterality_str+"\n projection - "+projection_str;
              spatials_report=spatials_report+"\n"+study_basic_report;


              //SC_LOG_INFO(laterality_str);
              //SC_LOG_INFO(study_basic_report);
}
              ///////////////////////////////////////////////////////////////

              ScIterator5Ptr spatIT = ms_context->Iterator5(images[i], ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_spatial_artefacts);
              ScAddr spatials;
                while (spatIT->Next())
                {
                 spatials=spatIT->Get(2);
                }


                //ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, spatials);



               vector<ScAddr> artifacts;
                ScIterator3Ptr artif = ms_context->Iterator3(spatials, ScType::EdgeAccessConstPosPerm, ScType::Unknown);
                while (artif->Next())
                {
                    if(artif->Get(2).IsValid()){
                        artifacts.push_back(artif->Get(2));
                    }
                }



                //SC_LOG_INFO("DELETE"+spatials_report+"DELETE");
                //SC_LOG_INFO("NEW ARTIFACT");
                /////////////////////

                for(int j=0; j<artifacts.size(); j++){
                    //spatials_report = spatials_report +"\n number:"+to_string(j);

                    ScAddr artifact_type;
                    ScIterator3Ptr artifIT = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, artifacts[j]);
                    while (artifIT->Next())
                    {
                            artifact_type =artifIT->Get(0);
                    }

                if(artifact_type.IsValid()){
                 spatials_report = spatials_report + "\n artifacts: ";
                 //ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, artifact_type);
                 string artifact_str = CommonUtils::getIdtfValue(ms_context.get(), artifact_type, Keynodes::nrel_main_idtf );
                 spatials_report=spatials_report+artifact_str+"  ";


                //if(laterality_str==Leftstr){
                  //   string strtemp="LEFT LEFT"+laterality_str;
                 //SC_LOG_INFO(strtemp);


                 ////////////////////////////образование
                    //форма
                 ScIterator5Ptr shapeIT = ms_context->Iterator5(artifacts[j], ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_shape_of_mass);
                 ScAddr shape;
                   while (shapeIT->Next())
                   {
                    shape=shapeIT->Get(2);
                   }


                   ScAddr shape_type;
                   ScIterator3Ptr shapeTypeIT = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, shape);
                   while (shapeTypeIT->Next())
                   {
                           shape_type =shapeTypeIT->Get(0);
                   }


                   if(shape_type.IsValid()){
                   if(!ms_context->HelperCheckEdge(Left, shape_type, ScType::EdgeAccessConstPosPerm)){
                    ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm,Left, shape_type);
                   }
                    string shape_str = CommonUtils::getIdtfValue(ms_context.get(), shape_type, Keynodes::nrel_main_idtf );
                    spatials_report= spatials_report+"\n shape - "+ shape_str+" ";
                    }
                    //края

                    ScIterator5Ptr margIT = ms_context->Iterator5(artifacts[j], ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_margins_of_mass);
                    ScAddr marg;
                      while (margIT->Next())
                      {
                       marg=margIT->Get(2);
                      }


                      ScAddr marg_type;
                      ScIterator3Ptr margTypeIT = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, marg);
                      while (margTypeIT->Next())
                      {
                              marg_type =margTypeIT->Get(0);
                      }

                      if(marg_type.IsValid()){
                          if(!ms_context->HelperCheckEdge(Left, marg_type, ScType::EdgeAccessConstPosPerm)){
                       ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Left, marg_type);
}
                       string marg_str = CommonUtils::getIdtfValue(ms_context.get(), marg_type, Keynodes::nrel_main_idtf );
                       spatials_report= spatials_report+"\n margins - "+ marg_str+" ";
                      }

                       //плотность

                       ScIterator5Ptr denIT = ms_context->Iterator5(artifacts[j], ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_mass_density);
                       ScAddr den;
                         while (denIT->Next())
                         {
                          den=denIT->Get(2);
                         }


                         ScAddr den_type;
                         ScIterator3Ptr denTypeIT = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, den);
                         while (denTypeIT->Next())
                         {
                                 den_type =denTypeIT->Get(0);
                         }

                         if(den_type.IsValid()){
                             if(!ms_context->HelperCheckEdge(Left, den_type, ScType::EdgeAccessConstPosPerm)){
                          ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Left, den_type);
}
                          string den_str = CommonUtils::getIdtfValue(ms_context.get(), den_type, Keynodes::nrel_main_idtf );
                          spatials_report= spatials_report+"\n density - "+ den_str+" ";
                         }

                          //размер

                          ScIterator5Ptr sizeIT = ms_context->Iterator5(artifacts[j], ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_artifact_size);
                          ScAddr size;
                            while (sizeIT->Next())
                            {
                             size=sizeIT->Get(2);
                            }


                            if(size.IsValid()){
                                if(!ms_context->HelperCheckEdge(Left, size, ScType::EdgeAccessConstPosPerm)){
                             ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Left, size);
}
                             string size_str = CommonUtils::getIdtfValue(ms_context.get(), artifacts[j], Keynodes::nrel_artifact_size );
                             spatials_report= spatials_report+"\n size - "+ size_str+" ";
                            }



                       //////////////////////////кальцинаты


                             ScIterator5Ptr distIT = ms_context->Iterator5(artifacts[j], ScType::EdgeDCommonConst, ScType::Unknown, ScType::EdgeAccessConstPosPerm, Keynodes::nrel_calc_distribution);
                             ScAddr dist;
                               while (distIT->Next())
                               {
                                dist=distIT->Get(2);
                               }


                               ScAddr dist_type;
                               ScIterator3Ptr distTypeIT = ms_context->Iterator3(ScType::Unknown, ScType::EdgeAccessConstPosPerm, dist);
                               while (distTypeIT->Next())
                               {
                                       dist_type =distTypeIT->Get(0);
                               }

                               if(dist_type.IsValid()){
                                   if(!ms_context->HelperCheckEdge(Left, dist_type, ScType::EdgeAccessConstPosPerm)){
                                ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Left, dist_type);
}
                                string dist_str = CommonUtils::getIdtfValue(ms_context.get(), dist_type, Keynodes::nrel_main_idtf );
                                spatials_report= spatials_report+"\n distribution - "+ dist_str+" ";
                                }

                }
                // else if(laterality_str==Rightstr){
                 //SC_LOG_INFO("RIGHT RIGHT");
                 //}

                    }
                }








SC_LOG_INFO(spatials_report);

ScAddr answer_link = ms_context->CreateLink();
string value = spatials_report;

ScStreamPtr stream;
stream.reset(new ScStream(value.c_str(),(sc_uint32) value.size(), SC_STREAM_FLAG_READ ));
ms_context->SetLinkContent(answer_link, *stream);



ScAddr edge_answer = ms_context->CreateEdge(ScType::EdgeDCommonConst, study, answer_link);

ScAddr edge_edge_answer = ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, Keynodes::nrel_study_report, edge_answer);

ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, Left);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, answer_link);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, study);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, edge_answer);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer, edge_edge_answer);
ms_context->CreateEdge(ScType::EdgeAccessConstPosPerm, answer,Keynodes::nrel_study_report );

SC_LOG_INFO("----------study end----------");

  AgentUtils::finishAgentWork(ms_context.get(), questionNode, answer);
  return SC_RESULT_OK;
}
}
