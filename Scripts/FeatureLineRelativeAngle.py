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

def feature_line_relative_angle(target_lines_fc,reference_lines_fc,search_radius,angle_threshold,output_feature_line_fc):
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
        workspace = r"in_memory"
        desc = arcpy.Describe(output_feature_line_fc)
        bearing_field = "RefAzimuth"
        corr_bearing_field = "TarAzimuth"
        arcpy.CopyFeatures_management(reference_lines_fc,output_feature_line_fc)
        fll.arc_print("Output file copied...",True)
        arcpy.Near_analysis(output_feature_line_fc,target_lines_fc,search_radius=search_radius)
        fll.arc_print("Near Analysis complete...",True)
        arcpy.AddField_management(output_feature_line_fc,bearing_field,"DOUBLE")
        reference_bearing_dict = fll.calculate_line_bearing(output_feature_line_fc,bearing_field,True)
        arcpy.AddField_management(target_lines_fc,corr_bearing_field ,"DOUBLE")
        target_bearing_dict = fll.calculate_line_bearing(target_lines_fc,corr_bearing_field,True)
        ref_fields = fll.get_fields(output_feature_line_fc)
        ref_df = fll.arcgis_table_to_df(output_feature_line_fc,ref_fields)
        target_fields = fll.get_fields(target_lines_fc)
        target_df = fll.arcgis_table_to_df(target_lines_fc,target_fields)
        OIDFieldName = desc.OIDFieldName
        ref_df[OIDFieldName] = ref_df.index
        ref_df["AngleDiff"] = (ref_df["NtAzimuth"] - ref_df["CrAzimuth"])%360
        ref_df["Angle_1"] = ref_df["AngleDiff"].apply(fll.find_smallest_angle,args = (0,True,))
        ref_df["Angle_2"] = ref_df["AngleDiff"].apply(fll.find_smallest_angle,args = (180,True,))
        ref_df["Relative_Angle"] = ref_df[["Angle_1","Angle_2"]].min(axis=1)
        ref_df["Parallel_Target"] = np.where(ref_df["Relative_Angle"]<angle_threshold,1,0)
        corridor_oid = arcpy.Describe(target_lines_fc).OIDFieldName
        ref_df = ref_df.merge(target_df,how='left',right_on = corridor_oid, left_on = "NEAR_FID",suffixes = ("_Ref","_Tar"))
        ref_df = ref_df[[OIDFieldName,"Angle_1","Angle_2","Relative_Angle"]].copy()
        fll.arc_print("Exporing relative angle results as array.")
        finalStandardArray = ref_df.to_records()
        fll.arc_print("Joining new score fields to feature class.")
        arcpy.da.ExtendTable(output_feature_line_fc, OIDFieldName, finalStandardArray, OIDFieldName, append_only=False)
        fll.arc_print("Join Complete")
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

