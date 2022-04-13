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
import os, arcpy, math
import linelibrary as fll


# Function Definitions

@fll.arc_tool_report
def get_azimuth(angle):
    """Converts headings represented by angles in degrees  180 to -180to Azimuth Angles.
    Will also normalize any number to 0-360 """
    if angle <= 180 and angle > 90:
        azimuth_angles = 360.0 - (angle - 90)
    else:
        azimuth_angles = abs(angle - 90)
    if abs(azimuth_angles) > 360:
        azimuth_angles % 360
    return azimuth_angles


@fll.arc_tool_report
def get_line_heading(polyline_obj, in_azimuth=False):
    """Takes in an ArcPolyline Object, and returns its heading based on its start and end point positions. """
    first_point = polyline_obj.firstPoint
    last_point = polyline_obj.lastPoint
    first_x = first_point.X
    first_y = first_point.Y
    last_x = last_point.X
    last_y = last_point.Y
    dx = last_x - first_x
    dy = last_y - first_y
    rads = math.atan2(dx, dy)
    angle = math.degrees(rads)
    if in_azimuth:
        angle = get_azimuth(angle)
    return angle


@fll.arc_tool_report
def get_angle_difference(angle, difference=90):
    """Given an azimuth angle (0-360), it will return the two azimuth angles (0-360) as a tuple that are perpendicular to it."""
    angle_lower, angle_higher = (angle + difference) % 360, (angle - difference) % 360
    return (angle_lower, angle_higher)


@fll.arc_tool_report
def translate_point(point, angle, radius, is_degree=True):
    """Passed a point object (arcpy) this funciton will translate it and
     return a modified clone based on a given angle out a set radius."""
    if is_degree:
        angle = math.radians(angle)
    new_x = math.cos(angle) * radius + point.X
    new_y = math.sin(angle) * radius + point.Y
    new_point = arcpy.Point(new_x, new_y)
    return new_point


@fll.arc_tool_report
def sample_line_from_center(polyline, length_to_sample):
    """Takes a polyline and samples it a target length using the segmentAlongLine method."""
    line_length = float(polyline.length)
    half_way_point = float(polyline.length) / 2
    start_point = half_way_point - length_to_sample / 2
    end_point = half_way_point + length_to_sample / 2
    if line_length <= length_to_sample / 2:
        start_point = 0
        end_point = line_length
    segment_returned = polyline.segmentAlongLine(start_point, end_point)
    return segment_returned


@fll.arc_tool_report
def generate_whisker_from_polyline(linegeometry, whisker_width):
    """This function will take an ArcPolyline and a target whisker width,and it will create a new line from the
    lines centroid (or label point) that is perpendicular to the bearing of the current polyline. """
    segment_returned = None
    center = linegeometry.centroid
    sr = linegeometry.spatialReference
    line_heading = get_line_heading(linegeometry)
    perpendicular_angle_start, perpendicular_angle_end = get_angle_difference(line_heading)
    point_start = translate_point(center, perpendicular_angle_start, whisker_width)
    point_end = translate_point(center, perpendicular_angle_end, whisker_width)
    inputs_line = arcpy.Array([point_start, point_end])
    segment_returned = arcpy.Polyline(inputs_line, sr)
    # This function fails if the line is shorter than the pull value, in this case no geometry is returned.
    return segment_returned


def feature_line_whisker(in_fc, out_whisker_width, out_whisker_field, sample_length, Out_FC):
    """Take a feature class and generate whiskers that are perpendicular either to the lines start and end points, or
    a sample line extracted from the center portion of the input polyline feature.
     This version of the tool will join the original fields."""
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(Out_FC)[0]
        FileName = os.path.split(Out_FC)[1]
        arcpy.CreateFeatureclass_management(OutWorkspace, FileName, "POLYLINE", in_fc, spatial_reference=in_fc,
                                            has_m="SAME_AS_TEMPLATE", has_z="SAME_AS_TEMPLATE")
        preFields = fll.get_fields(in_fc)
        fields = ["SHAPE@"] + preFields
        cursor = arcpy.da.SearchCursor(in_fc, fields)
        f_dict = fll.construct_index_dict(fields)
        with arcpy.da.InsertCursor(Out_FC, fields) as insertCursor:
            fll.arc_print("Established insert cursor for " + str(FileName) + ".", True)
            lineCounter = 0
            for singleline in cursor:
                try:
                    segment_rows = []
                    lineCounter += 1
                    linegeo = singleline[f_dict["SHAPE@"]]
                    # Function splits linegeometry based on method and split value
                    if sample_length:
                        linegeo = sample_line_from_center(linegeo, sample_length)
                    line_length = fll.line_length(singleline,
                                                  out_whisker_field,
                                                  out_whisker_width,
                                                  f_dict)
                    split_segment_geometry = generate_whisker_from_polyline(linegeo, line_length)
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
                        fll.arc_print("Iterated and generated whiskers for feature " + str(lineCounter) + ".", True)
                except Exception as e:
                    fll.arc_print(
                        "Failed to iterate through and generated whiskers for feature " + str(lineCounter) + ".",
                        True)
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
if __name__ == '__main__':
    # Define Inputs
    FeatureClass = arcpy.GetParameterAsText(0)
    Desired_Whisker_Width = arcpy.GetParameter(1)
    Feature_Whisker_Field = arcpy.GetParameterAsText(2)
    Line_Sample_Length = arcpy.GetParameterAsText(3)
    OutFeatureClass = arcpy.GetParameterAsText(4)
    feature_line_whisker(FeatureClass, float(Desired_Whisker_Width), Feature_Whisker_Field, float(Line_Sample_Length),
                         OutFeatureClass)
