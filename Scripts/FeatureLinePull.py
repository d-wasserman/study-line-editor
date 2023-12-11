# Name: FeatureLinePull.py
# Purpose: Take a feature class and pull back a line equal to a target distance from either a start or end point
# position. This version of the tool will join the original fields.
# of the old feature class.
# Author: David Wasserman
# Last Modified: 10/20/2019
# Copyright: David Wasserman
# Python Version:  2.7/3.6
# --------------------------------
# Copyright 2019 David J. Wasserman
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
@fll.arc_tool_report
def pull_line_geometry(linegeometry, pull_value, end_point_bool=True, start_point_bool=True):
    """This function will take an ArcPolyline, a pull value, and a start and end point boolean. The function returns
    a line geometry whose length are pulled back based on the input parameters.
    Parameters:
    ---------------------
    linegeometry (ArcPolyline): The ArcPolyline geometry to be modified. It represents the original line geometry before any modification.
    pull_value (float): The distance by which the line's start and/or end points will be retracted. This value determines how much the line geometry is shortened.
    end_point_bool (bool, optional): A flag to indicate whether the end point of the line should be retracted. If set to True, the end point of the line is pulled back by the distance specified in pull_value. Defaults to True.
    start_point_bool (bool, optional): A flag to indicate whether the start point of the line should be retracted. If set to True, the start point of the line is pulled back by the distance specified in pull_value. Defaults to True.

    Returns:
    - ArcPolyline: A modified ArcPolyline geometry with its start and/or end points retracted by the specified pull_value."""
    segment_returned = None
    line_length = float(linegeometry.length)
    end_point_start_position = line_length
    start_point_start_position = 0
    total_pull = 0
    try:
        if end_point_bool:
            end_point_start_position = line_length - pull_value
            total_pull += pull_value
        if start_point_bool:
            start_point_start_position = 0 + pull_value
            total_pull += pull_value
        if total_pull >= line_length:
            segment_returned = None #"The total pull value is greater than the length of the line, returning None."
        else:
            segment_returned = linegeometry.segmentAlongLine(start_point_start_position, end_point_start_position)
    except:  # Should the function failr, return null geometry. 
        return None
    return segment_returned


def feature_line_pull(in_fc, out_pull_value, out_pull_field, start_point_bool, end_point_bool, out_fc):
    """Take a feature class and pull back a line equal to a target distance from either a start or end point position.
     This version of the tool will join the original fields.
      Parameters:
      ---------------------
      in_fc (FeatureClass): The input feature class containing the line geometries to be modified. It should consist of line features.
      out_pull_value (float): The distance by which the lines' start and/or end points will be retracted. This value determines how much each line geometry in the feature class is shortened.
      out_pull_field (str): The name of the field in the output feature class where the pull back value will be stored. This field will contain the value specified in out_pull_value for each feature.
      start_point_bool (bool): A flag to indicate whether the start points of the lines should be retracted. If True, the start point of each line in the feature class is pulled back by the distance specified in out_pull_value.
      end_point_bool (bool): A flag to indicate whether the end points of the lines should be retracted. If True, the end point of each line in the feature class is pulled back by the distance specified in out_pull_value.
      out_fc (FeatureClass): The output feature class where the modified line geometries will be saved. This feature class will include the original attribute fields from in_fc, along with the new out_pull_field.
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
    FeatureClass = arcpy.GetParameterAsText(0)
    Desired_Feature_Pull = arcpy.GetParameter(1)
    Feature_Pull_Field = arcpy.GetParameterAsText(2)
    Start_Point_Bool = arcpy.GetParameter(3)
    End_Point_Bool = arcpy.GetParameter(4)
    OutFeatureClass = arcpy.GetParameterAsText(5)
    feature_line_pull(FeatureClass, Desired_Feature_Pull, Feature_Pull_Field, Start_Point_Bool, End_Point_Bool,
                      OutFeatureClass)
