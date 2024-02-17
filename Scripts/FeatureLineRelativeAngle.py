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

def feature_line_relative_angle(in_fc, out_pull_value, out_pull_field, start_point_bool, end_point_bool, out_fc):
    """
    Analyzes two sets of line geometries to find the smallest relative angle between each line in the target 
    feature class and all lines in the reference feature class. Optionally, it can apply an angle threshold to 
    identify lines that are parallel (within the threshold) to the target lines. The results are output to a 
    new feature class.

    Parameters:
    ---------------------
    target_lines_fc (FeatureClass): The input feature class containing the target line geometries for comparison.
    reference_lines_fc (FeatureClass): The input feature class containing the reference line geometries to compare against the target lines.
    search_radius (LinearUnit): The search radius within which the tool will look for reference lines relative to each target line.
    angle_threshold (float): An optional angle threshold (in degrees) to identify lines that are nearly parallel to the target lines. 
                             Lines within this threshold angle from the target lines will be considered parallel.
    output_feature_line_fc (FeatureClass): The output feature class where the lines that meet the angle criteria will be stored.
    This feature class will include the attributes from the target_lines_fc, along with the computed smallest relative angle to the reference lines.
    """
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(out_fc)[0]
        FileName = os.path.split(out_fc)[1]
        arcpy.CreateFeatureclass_management(OutWorkspace, FileName, "POLYLINE", in_fc, spatial_reference=in_fc,
                                            has_m="SAME_AS_TEMPLATE", has_z="SAME_AS_TEMPLATE")
        preFields = fll.get_fields(in_fc)
        fields = ["SHAPE@"] + preFields
        cursor = arcpy.da.SearchCursor(in_fc, fields)
        f_dict = fll.construct_index_dict(fields)
        with arcpy.da.InsertCursor(out_fc, fields) as insertCursor:
            fll.arc_print("Established insert cursor for " + str(FileName) + ".", True)
            lineCounter = 0
            null_counter = 0
            for singleline in cursor:
                try:
                    segment_rows = []
                    lineCounter += 1
                    linegeo = singleline[f_dict["SHAPE@"]]
                    # Function splits linegeometry based on method and split value
                    split_segment_geometry = pull_line_geometry(linegeo,
                                                                fll.line_length(singleline, out_pull_field,
                                                                                out_pull_value, f_dict),
                                                                start_point_bool, end_point_bool)
                    if split_segment_geometry is None:
                        null_counter += 1
                        # continue - # Uncomment to skip null geometries, otherwise empty geometries will be inserted.
                    segID = 0
                    try:
                        segID += 1
                        segmentedRow = fll.copy_altered_row(singleline, fields, f_dict,
                                                            {"SHAPE@": split_segment_geometry})
                        segment_rows.append(segmentedRow)
                    except:
                        fll.arc_print("Could not iterate through line segment " + str(segID) + ".")
                        break
                    for row in segment_rows:
                        insertCursor.insertRow(row)
                    if lineCounter % 500 == 0:
                        fll.arc_print("Iterated through and pulled feature " + str(lineCounter) + ".", True)
                except Exception as e:
                    fll.arc_print("Failed to iterate through and a pulled feature " + str(lineCounter) + ".", True)
                    fll.arc_print(e.args[0])
            if null_counter > 0:
                arcpy.AddWarning("There were " + str(null_counter) + " features that were shorter than the pull value.")
            del cursor, insertCursor, fields, preFields, OutWorkspace, lineCounter
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

