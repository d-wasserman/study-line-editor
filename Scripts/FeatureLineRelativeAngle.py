# Name: FeatureLineRelativeAngle.py
# Purpose: This tool will take in target line file and a reference line file and find the smallest relative angle between all reference lines and the target lines.
# This tool has an optional threshold that can be set to identify all facilities that are parallel (within the threshold) to the target corridors.
# of the old feature class.
# Author: David Wasserman
# Last Modified: 2/16/2024
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
# Import Modules
import os, arcpy, math
import linelibrary as fll


# Function Definitions

def feature_line_relative_angle(tartet_lines_fc,reference_lines_fc,search_radius,angle_threshold,output_feature_line_fc):
    """
    Analyzes two sets of line geometries to find the smallest relative angle between each line in the target 
    feature class and all lines in the reference feature class. Optionally, it can apply an angle threshold to 
    identify lines that are parallel (within the threshold) to the target lines. The results are output to a 
    new feature class.

    Parameters:
    ---------------------
    target_lines_fc (FeatureClass): The input feature class containing the target line geometries for comparison to reference lines.
    reference_lines_fc (FeatureClass): The input feature class containing the reference line geometries to compare against the target lines.
        This is the output feature class with new attributes added including target_angle
    search_radius (LinearUnit): The search radius within which the tool will look for reference lines relative to each target line.
    angle_threshold (float): An optional angle threshold (in degrees) to identify lines that are nearly parallel to the target lines. 
                             Lines within this threshold angle from the target lines will be considered parallel.
    output_feature_line_fc (FeatureClass): The output feature class where the lines that meet the angle criteria will be stored.
    This feature class will include the attributes from the reference lines fc, along with the computed smallest relative angle to the reference lines.
    """
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(out_fc)[0]
        FileName = os.path.split(out_fc)[1]
        desc = arcpy.Describe(out_file)
        arcpy.CopyFeatures_management(reference_lines_fc,output_feature_line_fc)
        OIDFieldName = desc.OIDFieldName
        network_df[OIDFieldName] = network_df.index
        network_df[OIDFieldName].head()
        JoinField = arcpy.ValidateFieldName("DFIndJoin", workspace)
        
        network_df["Angle_1"] = network_df["AngleDiff"].apply(fll.find_smallest_angle,args = (0,True,))
        network_df["Angle_2"] = network_df["AngleDiff"].apply(fll.find_smallest_angle,args = (180,True,))
        network_df["Relative_Angle"] = network_df[["Angle_1","Angle_2"]].min(axis=1)
        network_df= network_df[[OIDFieldName,"Angle_1","Angle_2","Relative_Angle"]].copy()
        print("Exporting new percentile dataframe to structured numpy array.")
        finalStandardArray = network_df.to_records()
        print("Joining new score fields to feature class.")
        arcpy.da.ExtendTable(out_file, OIDFieldName, finalStandardArray, OIDFieldName, append_only=False)
        print("Join Complete")
        fll.arc_print("Script Completed Successfully.", True)
    except arcpy.ExecuteError:
        fll.arc_print(arcpy.GetMessages(2))
    except Exception as e:
        fll.arc_print(e.args[0])

        # End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Define Inputs
    Target_Lines = arcpy.GetParameterAsText(0)
    Reference_Lines = arcpy.GetParameterAsText(1)
    Search_Radius = arcpy.GetParameter(2)
    Angle_Threshold = float(arcpy.GetParameter(3))
    Output_Feature_Line = arcpy.GetParameterAsText(4)
    feature_line_relative_angle(Target_Lines, Reference_Lines, Search_Radius, Angle_Threshold, Output_Feature_Line)

