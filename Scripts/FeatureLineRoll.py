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
    pull_value - the distance or percentage the line will be pulled back from either the start or end point
    percentage - if true, pull value is treated as a percentage."""
    line_length = 1 if percentage else float(linegeometry.length)
    end_point_end_position = 1 if percentage else line_length
    start_point_end_position = 0
    try:
        end_point_start_position = line_length - pull_value
        start_point_start_position = 0 + pull_value
        start_segment = linegeometry.segmentAlongLine(start_point_start_position, start_point_end_position, percentage)
        end_segment = linegeometry.segmentAlongLine(end_point_start_position, end_point_end_position, percentage)
    except:  # This function fails if the line is shorter than the pull value, in this case no geometry is returned.
        return None, None
    return start_segment, end_segment


def feature_line_roll(in_fc, extension_distance, end_sampling_percentage, out_fc):
    """Take a feature line and extend its end points based on the angle implied by a sample of the line identified
    from its start and end point. This tool has an optional ability to use the Integrate geoprocessing tools after
    line extensions to match the lines ahead of its vertex.
    Parameters
    ---------------------
    in_fc - Line Geometry- input arc polyline to extend/roll
    extension_distance - the distance to extend the line in both directions (units of projection)
    end_sampling_percentage - the length segment to sample end from in current projection units
    out_fc - output feature class with extended lines based on sampling of end segments
    """
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(out_fc)[0]
        FileName = os.path.split(out_fc)[1]
        fll.arc_print("Creating new feature class for lines...")
        arcpy.CreateFeatureclass_management(OutWorkspace, FileName, "POLYLINE", in_fc, spatial_reference=in_fc,
                                            has_m="SAME_AS_TEMPLATE", has_z="SAME_AS_TEMPLATE")
        preFields = fll.get_fields(in_fc)
        fields = ["SHAPE@"] + preFields
        cursor = arcpy.da.SearchCursor(in_fc, fields)
        f_dict = fll.construct_index_dict(fields)
        sr = arcpy.Describe(in_fc).spatialReference
        fll.arc_print("Extending lines based on heading calculations...")

        with arcpy.da.InsertCursor(out_fc, fields) as insertCursor:
            lineCounter = 0
            fll.arc_print("Established insert cursor for " + str(FileName) + ".", True)
            for singleline in cursor:
                try:
                    segment_rows = []
                    lineCounter += 1
                    linegeo = singleline[f_dict["SHAPE@"]]
                    # Function splits line geometry based on method and split value
                    start_seg, end_seg = get_line_ends(linegeo, float(end_sampling_percentage), True)
                    start_bearing  = fll.convert_to_azimuth(fll.calculate_segment_bearing(start_seg))
                    end_bearing = fll.convert_to_azimuth(fll.calculate_segment_bearing(end_seg))
                    start_start_pt = arcpy.PointGeometry(start_seg.firstPoint, sr)
                    end_end_pt = arcpy.PointGeometry(end_seg.lastPoint, sr)
                    new_start_end_pt = start_start_pt.pointFromAngleAndDistance(start_bearing, extension_distance)
                    new_end_end_pt = end_end_pt.pointFromAngleAndDistance(end_bearing, extension_distance)
                    segID = 0
                    part_number = 0
                    all_parts = []
                    for part in linegeo:
                        part_list = []
                        point_number = 0
                        for point in linegeo.getPart(part_number):
                            if part_number == 0 and point_number == 0:
                                part_list.append(new_start_end_pt.getPart(0))
                            if point:
                                part_list.append(point)
                            point_number += 1
                        all_parts.append(part_list)
                        part_number += 1
                    all_parts[-1].append(new_end_end_pt.getPart(0))
                    all_pt_array = arcpy.Array(all_parts)
                    new_line = arcpy.Polyline(all_pt_array, sr)
                    row = fll.copy_altered_row(singleline, fields, f_dict, {"SHAPE@": new_line})
                    insertCursor.insertRow(row)
                    if lineCounter % 500 == 0:
                        fll.arc_print("Iterated through and extend feature " + str(lineCounter) + ".", True)
                except Exception as e:
                    fll.arc_print("Failed to iterate through features.", True)
                    fll.arc_print(e.args[0])
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
    ExtensionDistance = float(arcpy.GetParameter(1))
    EndSamplingPercentage = float(arcpy.GetParameter(2))
    OutFeatureClass = arcpy.GetParameterAsText(3)
    feature_line_roll(FeatureClass, ExtensionDistance,
                      EndSamplingPercentage, OutFeatureClass)
