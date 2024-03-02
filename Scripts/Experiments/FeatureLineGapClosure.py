# Name: FeatureLineGapClosure.py
# Purpose: This script fills gaps between line feature end points within a specified search radius, 
# improving connectivity. It analyzes spatial relationships to create new lines in an output
# feature class, enhancing network integration.
# Author: David Wasserman
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

def create_gap_filling_lines(input_line_features, output_feature_class, search_radius):
    """Identifies and fills gaps between line feature end points within a specified search radius.
    Adds the FIDs of the line end points as start and end attributes and includes a field for the near distance.

    Parameters:
    - input_line_features (FeatureClass): The input line features to analyze.
    - output_feature_class (FeatureClass): The output feature class for storing new lines that fill the identified gaps.
    - search_radius (float): The search radius within which to identify the closest end points for gap filling.
    """
    try:
        arcpy.env.overwriteOutput = True
        workspace = "in_memory"
        workspace, output_fc_name = os.path.split(output_feature_class)
        
        # Explode the line features to their end points
        end_points_temp = os.path.join(workspace,"end_points")
        arcpy.FeatureVerticesToPoints_management(input_line_features, end_points_temp, "BOTH_ENDS")
        
        # Add a unique identifier to each end point
        arcpy.AddField_management(end_points_temp, "LINE_ID", "LONG")
        arcpy.CalculateField_management(end_points_temp, "LINE_ID", "!FID!", "PYTHON3")
        
        # Construct the near table to find closest points within the search radius
        near_table_temp = os.path.join(workspace,"end_points_near")
        arcpy.GenerateNearTable_analysis(end_points_temp, end_points_temp, near_table_temp, 
                                         search_radius, "NO_LOCATION", "NO_ANGLE", "CLOSEST")
        
        # Filter out points that are from the same line feature
        filtered_near_table = [row for row in arcpy.da.SearchCursor(near_table_temp, ["IN_FID", "NEAR_FID", "NEAR_DIST"]) 
                               if row[0] != row[1]]
        
        # Create the output feature class
        arcpy.CreateFeatureclass_management(workspace, output_fc_name, "POLYLINE", spatial_reference=input_line_features)
        
        # Insert new lines into the output feature class
        with arcpy.da.InsertCursor(output_feature_class, ["SHAPE@"]) as insert_cursor:
            for row in filtered_near_table:
                start_point = arcpy.da.SearchCursor(end_points_temp, ["SHAPE@"], "FID = {}".format(row[0])).__next__()[0]
                end_point = arcpy.da.SearchCursor(end_points_temp, ["SHAPE@"], "FID = {}".format(row[1])).__next__()[0]
                line = arcpy.Polyline(arcpy.Array([start_point.firstPoint, end_point.firstPoint]), 
                                      start_point.spatialReference)
                insert_cursor.insertRow([line])
                
        arcpy.AddMessage("Gap filling lines created successfully.")
        
    except Exception as e:
        arcpy.AddError(str(e))

if __name__ == '__main__':
    # Define Inputs
    InputLineFeatures = arcpy.GetParameterAsText(0)
    OutputFeatureClass = arcpy.GetParameterAsText(1)
    SearchRadius = float(arcpy.GetParameterAsText(2))
    
    create_gap_filling_lines(InputLineFeatures, OutputFeatureClass, SearchRadius)
