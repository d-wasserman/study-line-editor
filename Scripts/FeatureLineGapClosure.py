# Name: FeatureLineGapClosure.py
# Purpose: This script fills gaps between line feature end points within a specified search radius, 
# improving connectivity. It analyzes spatial relationships to create new lines in an output
# feature class, enhancing network integration.
# Author: David Wasserman
# AI Disclosure: Partial Code Generation Feb 2024 ChatGPT 4. 
# Last Modified: 3/1/2024
# Copyright: David Wasserman
# Python Version:  3.9
# --------------------------------
# Copyright 2024 David J. Wasserman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------
import arcpy
import os
import linelibrary as ll

def create_gap_filling_lines(input_line_features, output_feature_class, search_radius = "500 Feet", connection_count = 1):
    """Identifies and fills gaps between line feature end points within a specified search radius.
    Adds the FIDs of the line end points as start and end attributes and includes a field for the near distance.

    Parameters:
    - input_line_features (FeatureClass): The input line features to analyze.
    - output_feature_class (FeatureClass): The output feature class for storing new lines that fill the identified gaps.
    - search_radius (LinearUnit): The search radius within which to identify the closest end points for gap filling.
    - connection_count(int): The number of connections to create between end points in the order of proximity. 
    """
    # try:
    ll.arc_print("Feature class validation...")
    arcpy.env.overwriteOutput = True
    oid = arcpy.Describe(input_line_features).OIDFieldName
    workspace = "in_memory"
    pt_id, ln_id = "PT_ID" , "LINE_ID"
    workspace, output_fc_name = os.path.split(output_feature_class)
    arcpy.AddField_management(input_line_features, ln_id, "LONG")
    arcpy.CalculateField_management(input_line_features, ln_id, "!{0}!".format(oid), "PYTHON3")
    ll.arc_print("Explode the line features to their end points...")
    end_points_temp = os.path.join(workspace,"end_points")
    arcpy.FeatureVerticesToPoints_management(input_line_features, end_points_temp, "BOTH_ENDS")
    
    ll.arc_print("Add a unique identifier to each end point...")
    arcpy.AddField_management(end_points_temp, pt_id, "LONG")
    arcpy.CalculateField_management(end_points_temp, pt_id, "!{0}!".format(oid), "PYTHON3")
    ll.arc_print("Construct the near table to find closest points within the search radius...")
    near_table_temp = os.path.join(workspace,"end_points_near")
    arcpy.GenerateNearTable_analysis(end_points_temp, end_points_temp, near_table_temp, 
                                        search_radius, "NO_LOCATION", "NO_ANGLE","ALL",closest_count = connection_count)
    ll.arc_print("Filter out points that are from the same line feature...")
    # Load data into a DataFrame
    df = ll.arcgis_table_to_df(end_points_temp, input_fields=["SHAPE@", pt_id,ln_id])
    df.set_index(pt_id)
    # Create a dictionary from the columns
    sm_df = df[[ln_id,pt_id]].copy()
    groups = sm_df.groupby(pt_id)
    line_dict=  {pt_id: group[ln_id].values[0] for pt_id, group in groups}
    
    # ll.arc_print(line_dict)
    filtered_near_table = [row for row in arcpy.da.SearchCursor(near_table_temp, ["IN_FID", "NEAR_FID", "NEAR_DIST"]) 
                            if line_dict[row[0]] != line_dict[row[1]]]
    
    ll.arc_print("Create the output feature class...")
    arcpy.CreateFeatureclass_management(workspace, output_fc_name, "POLYLINE", spatial_reference=input_line_features)
    a_nd, b_nd = "A_NODE", "B_NODE"
    arcpy.AddField_management(output_feature_class, a_nd,"LONG")
    arcpy.AddField_management(output_feature_class,b_nd,"LONG")
    ll.arc_print("Insert new lines into the output feature class...")
    sr = arcpy.Describe(input_line_features).spatialReference
    count_hash = {}
    with arcpy.da.InsertCursor(output_feature_class, ["SHAPE@",a_nd,b_nd]) as insert_cursor:
        for row in filtered_near_table:
            counter = count_hash.setdefault(row[0],0)
            if counter >= connection_count:
                # Don't create new lines for those beyond
                continue
            start_point = df[df[pt_id]==row[0]]["SHAPE@"].values[0]
            end_point = df[df[pt_id]==row[1]]["SHAPE@"].values[0]
            line = arcpy.Polyline(arcpy.Array([start_point.firstPoint, end_point.lastPoint]), sr)
            insert_cursor.insertRow([line,row[0], row[1]])
            count_hash[row[0]] += 1
            
        ll.arc_print("Gap filling lines created successfully.")
        
    # except Exception as e:
    #     arcpy.AddError(str(e))

if __name__ == '__main__':
    # Define Inputs
    InputLineFeatures = arcpy.GetParameterAsText(0)
    OutputFeatureClass = arcpy.GetParameterAsText(1)
    SearchRadius = arcpy.GetParameterAsText(2)
    NumberOfConnections = int(arcpy.GetParameterAsText(3))
    
    create_gap_filling_lines(InputLineFeatures, OutputFeatureClass, SearchRadius,NumberOfConnections)
