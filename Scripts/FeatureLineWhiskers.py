# Name: FeatureLineWhiskers.py
# Purpose: This tool will transform a polyline feature class into "whiskers" or line features at the centroid of
# the line that are perpendicular to the lines start and end points.
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
import os

import arcpy

import linelibrary as fll

# Function Definitions


def feature_line_whisker(
    in_fc, out_whisker_width, out_whisker_field, sample_length, out_fc
):
    """Take a feature class and generate "whiskers" that are perpendicular either to the lines start and end points, or
    a sample line extracted from the center portion of the input polyline feature.
     This version of the tool will join the original fields.
     Parameters
     -------------------
    in_fc (FeatureClass): The input feature class containing the line geometries from which whiskers will be generated. It should consist of line features.
    out_whisker_width (float): The width of each whisker. This value determines the perpendicular distance from the
      line to the end of the whisker.
    out_whisker_field (str): The name of the field in the output feature class where the whisker width will be stored.
      This field will contain the value specified in out_whisker_width for each feature.
    sample_length (float): The length of the line segment (sampled from the center of each input polyline) used to
      generate the whiskers. This parameter defines the portion of the line used for whisker generation.
    out_fc (FeatureClass): The output feature class where the geometries with whiskers will be saved. This feature class
      will include the original attribute fields from in_fc, along with the new out_whisker_field.
    """
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
                    # Function splits linegeometry based on method and split value
                    if sample_length:
                        linegeo = fll.sample_line_from_center(linegeo, sample_length)
                    line_length = fll.line_length(
                        singleline, out_whisker_field, out_whisker_width, f_dict
                    )
                    split_segment_geometry = fll.generate_whisker_from_polyline(
                        linegeo, line_length
                    )
                    segID = 0
                    try:
                        segID += 1
                        segmentedRow = fll.copy_altered_row(
                            singleline,
                            fields,
                            f_dict,
                            {"SHAPE@": split_segment_geometry},
                        )
                        segment_rows.append(segmentedRow)
                    except:
                        fll.arc_print(
                            "Could not iterate through line segment " + str(segID) + "."
                        )
                        break

                    for row in segment_rows:
                        insertCursor.insertRow(row)
                    if lineCounter % 500 == 0:
                        fll.arc_print(
                            "Iterated and generated whiskers for feature "
                            + str(lineCounter)
                            + ".",
                            True,
                        )
                except Exception as e:
                    fll.arc_print(
                        "Failed to iterate through and generated whiskers for feature "
                        + str(lineCounter)
                        + ".",
                        True,
                    )
                    fll.arc_print(e.args[0])
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
if __name__ == "__main__":
    # Define Inputs
    FeatureClass = arcpy.GetParameterAsText(0)
    Desired_Whisker_Width = arcpy.GetParameter(1)
    Feature_Whisker_Field = arcpy.GetParameterAsText(2)
    Line_Sample_Length = arcpy.GetParameterAsText(3)
    OutFeatureClass = arcpy.GetParameterAsText(4)
    feature_line_whisker(
        FeatureClass,
        float(Desired_Whisker_Width),
        Feature_Whisker_Field,
        float(Line_Sample_Length),
        OutFeatureClass,
    )
