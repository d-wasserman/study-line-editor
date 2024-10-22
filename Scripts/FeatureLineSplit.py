# Name: FeatureLineSplit.py
# Purpose: Take a feature class and proportionally split each unique feature line into segments of a target count
# or target distance. Similar to editing tools done manually.This version of the tool will join the original fields
# of the old feature class. This tool also has the ability to split a line so that it includes a percentage overlap
# with other segments based
# Author: David Wasserman
# Last Modified: 3/8/2023
# Copyright: David Wasserman
# Python Version:   2.7/3.6
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
import os

import arcpy

import linelibrary as fll


# Function Definitions
# @fll.arc_tool_report
def split_line_geometry(
    linegeometry,
    split_value,
    split_method="LENGTH",
    overlap_percentage=0,
    best_fit_bool=True,
):
    """This function will take an ArcPolyline, a split value, a split method of either 'LENGTH' or 'SEGMENT COUNT', and
    boolean that determines if the lines split are the best of fit based on the length. The function returns a list of
    line geometries whose length and number are determined by the split value, split method, and best fit settings.
    Parameters
    ----------------
    linegeometry - arc polyline
    split_value - the length in current projection or desired number of segments
    split_method - determines if split value is treated as a length target or segment count target
    overlap_percentage - the amount lines will overlap in terms of a percentage of the target length. No overlap at end points.
    best_fit_bool -  determines if the length is rounded to be segments of equal length.
    Returns
    ------------
    segment_list - list of split geometries.
    """
    segment_list = []
    if str(split_method).upper() == "LENGTH":
        segment_list = fll.split_segment_by_length(
            linegeometry, split_value, overlap_percentage, best_fit_bool
        )
    else:
        segment_list = fll.split_segment_by_count(
            linegeometry, split_value, overlap_percentage
        )
    return segment_list


def feature_line_split(
    in_fc,
    out_count_value,
    out_count_field,
    split_method,
    overlap_percentage,
    best_fit_bool,
    out_fc,
):
    """This function will split each feature in a feature class into a desired number of equal length segments based
    on a specified distance or target segment count based on an out count value or field.
    Parameters
    ----------------
    in_fc - input arc polyline to split
    out_count_value - the length or desired number of segments
    out_count_field - optional field to use for custom splitting using the desired type of out_count_value/split method
    split_method- determines if split value is treated as a length target or segment count target
    overlap_percentage - the amount lines will overlap in terms of a percentage of the target length. No overlap at end points.
    best_fit_bool determines if the length is roundedto be segments of equal length.
    out_fc - output split feature class"""
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(out_fc)[0]
        FileName = os.path.split(out_fc)[1]
        arcpy.CreateFeatureclass_management(
            OutWorkspace,
            FileName,
            "POLYLINE",
            in_fc,
            spatial_reference=in_fc,
            has_m="SAME_AS_TEMPLATE",
            has_z="SAME_AS_TEMPLATE",
        )
        preFields = fll.get_fields(in_fc)
        fields = ["SHAPE@"] + preFields
        cursor = arcpy.da.SearchCursor(in_fc, fields)
        f_dict = fll.construct_index_dict(fields)
        with arcpy.da.InsertCursor(out_fc, fields) as insertCursor:
            fll.arc_print("Established insert cursor for " + str(FileName) + ".", True)
            lineCounter = 0
            for singleline in cursor:
                try:
                    segment_rows = []
                    lineCounter += 1
                    linegeo = singleline[f_dict["SHAPE@"]]
                    # Function splits line geometry based on method and split value
                    line_length = fll.line_length(
                        singleline, out_count_field, out_count_value, f_dict
                    )
                    split_segment_list = split_line_geometry(
                        linegeo,
                        line_length,
                        split_method,
                        overlap_percentage,
                        best_fit_bool,
                    )
                    segID = 0
                    for segment in split_segment_list:
                        try:
                            segID += 1
                            segmentedRow = fll.copy_altered_row(
                                singleline, fields, f_dict, {"SHAPE@": segment}
                            )
                            segment_rows.append(segmentedRow)
                        except:
                            fll.arc_print(
                                "Could not iterate through line segment "
                                + str(segID)
                                + "."
                            )
                            break
                    if len(segment_rows) == len(
                        split_segment_list
                    ):  # Unload by feature so partial segments are not made.
                        for row in segment_rows:
                            insertCursor.insertRow(row)
                    if lineCounter % 500 == 0:
                        fll.arc_print(
                            "Iterated through and split feature "
                            + str(lineCounter)
                            + ".",
                            True,
                        )
                except Exception as e:
                    fll.arc_print(
                        "Failed to iterate through and a split feature "
                        + str(lineCounter)
                        + ".",
                        True,
                    )
                    fll.arc_print(e.args[0])
            del (
                cursor,
                insertCursor,
                fields,
                preFields,
                OutWorkspace,
                lineCounter,
                split_segment_list,
            )
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
if __name__ == "__main__":
    # Define Inputs
    FeatureClass = arcpy.GetParameterAsText(0)
    Desired_Feature_Count = arcpy.GetParameter(1)
    Feature_Count_Field = arcpy.GetParameterAsText(2)
    Split_Method = arcpy.GetParameterAsText(3)
    Overlap_Percentage = arcpy.GetParameter(4)
    Best_Fit_Bool = arcpy.GetParameter(5)
    OutFeatureClass = arcpy.GetParameterAsText(6)
    feature_line_split(
        FeatureClass,
        Desired_Feature_Count,
        Feature_Count_Field,
        Split_Method,
        Overlap_Percentage,
        Best_Fit_Bool,
        OutFeatureClass,
    )
