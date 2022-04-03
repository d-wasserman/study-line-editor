# Name: FeatureLineRoll.py
# Purpose: Take a feature line and extend its end points based on the angle implied by a sample of the line identified
# from its start and end point. This tool has an optional ability to use the Integrate geoprocessing tools after line
# extensions to match the lines ahead of its vertex. Intended to enable rolling window operations.
# Author: David Wasserman
# Last Modified: 3/11/2022
# Copyright: David Wasserman
# Python Version:   2.7/3.6
# --------------------------------
# Copyright 2022 David J. Wasserman
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
def get_line_ends(linegeometry, pull_value, percentage=False):
    """This function will take an ArcPolyline and a pull value. The function returns
    a the start and end points of the line as separate geometries.
    Parameters
    ---------------------
    Line Geometry - arc polyline input
    pull_value - the distance the line will be pulled back from either the start or end point
    percentage - if true, pull value is treated as a percentage."""
    segment_returned = None
    line_length = float(linegeometry.length)
    end_point_end_position = line_length
    start_point_end_position = 0
    try:
        end_point_start_position = line_length - pull_value
        start_point_start_position = 0 + pull_value
        start_segment = linegeometry.segmentAlongLine(start_point_start_position, start_point_end_position, percentage)
        end_segment = linegeometry.segmentAlongLine(end_point_start_position, end_point_end_position, percentage)
    except:  # This function fails if the line is shorter than the pull value, in this case no geometry is returned.
        return None,None
    return start_segment, end_segment


def feature_line_roll(in_fc,extension_distance, post_extension_integration,integration_tolerance,
                      end_sampling_percentage, out_fc):
    """Take a feature line and extend its end points based on the angle implied by a sample of the line identified
    from its start and end point. This tool has an optional ability to use the Integrate geoprocessing tools after
    line extensions to match the lines ahead of its vertex.
    Parameters
    ---------------------
    in_fc - Line Geometry- input arc polyline to extend/roll
    extension_distance - the distance to extend the line in both directions (units of projection)
    post_extension_integration- if true, the integrate tool will be run post extension
    integration_tolerance - the distance vertices will be merged of the rolling network to the original
    end_sampling_percentage - the length segment to sample end from in current projection units
    out_fc - output feature class with extended lines based on sampling of end segments
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
            for singleline in cursor:
                try:
                    segment_rows = []
                    lineCounter += 1
                    linegeo = singleline[f_dict["SHAPE@"]]
                    # Function splits line geometry based on method and split value
                    line_length = fll.line_length(singleline, out_count_field, out_count_value, f_dict)
                    split_segment_list = split_line_geometry(linegeo, line_length, split_method, best_fit_bool)
                    segID = 0
                    for segment in split_segment_list:
                        try:
                            segID += 1
                            segmentedRow = fll.copy_altered_row(singleline, fields, f_dict, {"SHAPE@": segment})
                            segment_rows.append(segmentedRow)
                        except:
                            fll.arc_print("Could not iterate through line segment " + str(segID) + ".")
                            break
                    if len(segment_rows) == len(
                            split_segment_list):  # Unload by feature so partial segments are not made.
                        for row in segment_rows:
                            insertCursor.insertRow(row)
                    if lineCounter % 500 == 0:
                        fll.arc_print("Iterated through and split feature " + str(lineCounter) + ".", True)
                except Exception as e:
                    fll.arc_print("Failed to iterate through and a split feature " + str(lineCounter) + ".", True)
                    fll.arc_print(e.args[0])
            del cursor, insertCursor, fields, preFields, OutWorkspace, lineCounter, split_segment_list
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
    ExtensionDistance = arcpy.GetParameter(1)
    PostExtensionIntegration = arcpy.GetParameterAsText(2)
    IntegrationTolerance = arcpy.GetParameterAsText(3)
    EndSamplingPercentage = arcpy.GetParameter(4)
    OutFeatureClass = arcpy.GetParameterAsText(5)
    feature_line_roll(FeatureClass,ExtensionDistance, PostExtensionIntegration, IntegrationTolerance,
                      EndSamplingPercentage,O utFeatureClass)
