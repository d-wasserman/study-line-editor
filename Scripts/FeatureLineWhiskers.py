# Name: FeatureLineWhiskers.py
# Purpose: This tool will transform a polyline feature class into "whiskers" or line features at the centroid of
# the line that are perpendicular to the lines start and end points.
# of the old feature class.
# Author: David Wasserman
# Last Modified: 8/27/2017
# Copyright: David Wasserman
# Python Version:   2.7
# --------------------------------
# Copyright 2015 David J. Wasserman
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


# Function Definitions
def func_report(function=None, report_bool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def func_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if report_bool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Ouput(s):{0}".format(str(func_result)))
                return func_result
            except Exception as e:
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return func_wrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return func_report_decorator(function)

        return waiting_for_function
    else:
        return func_report_decorator(function)


def arc_tool_report(function=None, arc_tool_message_bool=False, arc_progressor_bool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def arc_tool_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if arc_tool_message_bool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(func_result)))
                if arc_progressor_bool:
                    arcpy.SetProgressorLabel("Function:{0}".format(str(function.__name__)))
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel("     Ouput(s):{0}".format(str(func_result)))
                return func_result
            except Exception as e:
                arcpy.AddMessage(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__),
                                                                                    str(args)))
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])

        return func_wrapper

    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return arc_tool_report_decorator(function)

        return waiting_for_function
    else:
        return arc_tool_report_decorator(function)


@arc_tool_report
def arc_print(string, progressor_Bool=False):
    """ This function is used to simplify using arcpy reporting for tool creation,if progressor bool is true it will
    create a tool label."""
    casted_string = str(string)
    if progressor_Bool:
        arcpy.SetProgressorLabel(casted_string)
        arcpy.AddMessage(casted_string)
        print(casted_string)
    else:
        arcpy.AddMessage(casted_string)
        print(casted_string)


def copy_altered_row(row, fieldList, replacementDict):
    """This utility function copy a row with the listed fields, but if there is a key in the replacement dictionary
    the item in that dictionary will replace the item that was originally in that row. Useful for cursor short hand."""
    try:
        newRow = []
        keyList = replacementDict.keys()
        for field in fieldList:
            try:
                if field in keyList:
                    newRow.append(replacementDict[field])
                else:
                    newRow.append(row[get_f_index(fieldList, field)])
            except:
                arc_print("Could not replace field {0} with its accepted value. Check field names for match.".format(
                    str(field)), True)
                newRow.append(None)  # Append a null value where it cannot find a value to the list.
        return newRow
    except:
        arc_print("Could not get row fields for the following input {0}, returned an empty list.".format(str(row)),
                  True)
        arcpy.AddWarning(
            "Could not get row fields for the following input {0}, returned an empty list.".format(str(row)))
        newRow = []
        return newRow


@arc_tool_report
def line_length(row, Field, constantLen, fNames, printBool=False):
    """Returns the appropriate value type  based on the options selected: retrieved form field or uses a constant"""
    if Field in fNames and Field and Field != "#":
        if printBool:
            arc_print("Using size field to create output geometries.", True)
        return abs(row[get_f_index(fNames, Field)])
    else:
        if printBool:
            arc_print("Using size input value to create same sized output geometries.", True)
        return abs(constantLen)


def get_fields(featureClass, excludedTolkens=["OID", "Geometry"], excludedFields=["shape_area", "shape_length"]):
    """Get all field names from an incoming feature class defaulting to excluding tolkens and shape area & length.
    Inputs: Feature class, excluding tokens list, excluded fields list.
    Outputs: List of field names from input feature class. """
    try:
        try:  # If  A feature Class split to game name
            fcName = os.path.split(featureClass)[1]
        except:  # If a Feature Layer, just print the Layer Name
            fcName = featureClass
        field_list = [f.name for f in arcpy.ListFields(featureClass) if f.type not in excludedTolkens
                      and f.name.lower() not in excludedFields]
        arc_print("The field list for {0} is:{1}".format(str(fcName), str(field_list)), True)
        return field_list
    except:
        arc_print(
            "Could not get fields for the following input {0}, returned an empty list.".format(
                str(featureClass)),
            True)
        arcpy.AddWarning(
            "Could not get fields for the following input {0}, returned an empty list.".format(
                str(featureClass)))
        field_list = []
        return field_list


def get_f_index(field_names, field_name):
    """Will get the index for a  arcpy da.cursor based on a list of field names as an input.
    Assumes string will match if all the field names are made lower case."""
    try:
        return [str(i).lower() for i in field_names].index(str(field_name).lower())
    except:
        print("Couldn't retrieve index for {0}, check arguments.".format(str(field_name)))
        return None

@arc_tool_report
def get_azimuth(angle):
    """Converts headings represented by angles in degrees  180 to -180to Azimuth Angles.
    Will also normalize any number to 0-360 """
    if angle<=180 and angle>90:
        azimuth_angles= 360.0-(angle-90)
    else:
        azimuth_angles= abs(angle-90)
    if abs(azimuth_angles)>360:
        azimuth_angles%360
    return azimuth_angles

@arc_tool_report
def get_line_heading(polyline_obj,in_azimuth=False):
    """Takes in an ArcPolyline Object, and returns its heading based on its start and end point positions. """
    first_point = polyline_obj.firstPoint
    last_point = polyline_obj.lastPoint
    first_x = first_point.X
    first_y = first_point.Y
    last_x = last_point.X
    last_y = last_point.Y
    dx = last_x - first_x
    dy = last_y - first_y
    rads = math.atan2(dy, dx)
    angle = math.degrees(rads)
    if in_azimuth:
        angle = get_azimuth(angle)
    return angle

@arc_tool_report
def get_angle_difference(angle,difference=90):
    """Given an azimuth angle (0-360), it will return the two azimuth angles (0-360) as a tuple that are perpendicular to it."""
    angle_lower,angle_higher=(angle+difference)%360,(angle-difference)%360

    return (angle_lower,angle_higher)

@arc_tool_report
def translate_point(point,angle,radius,is_degree=True):
    """Passed a point object (arcpy) this funciton will translate it and
     return a modified clone based on a given angle out a set radius."""
    if is_degree:
        angle=math.radians(angle)

    new_x= math.cos(angle)*radius+point.X
    new_y= math.sin(angle)*radius+point.Y
    new_point= arcpy.Point(new_x,new_y)
    return new_point

@arc_tool_report
def sample_line_from_center(polyline,length_to_sample):
    """Takes a polyline and samples it a target length using the segmentAlongLine method."""
    line_length = float(polyline.length)
    half_way_point= float(polyline.length)/2
    start_point= half_way_point-length_to_sample/2
    end_point = half_way_point+length_to_sample/2
    if line_length <= length_to_sample/2:
        start_point=0
        end_point=line_length
    segment_returned = polyline.segmentAlongLine(start_point,end_point)
    return segment_returned

@arc_tool_report
def generate_whisker_from_polyline(linegeometry, whisker_width):
    """This function will take an ArcPolyline and a target whisker width,and it will create a new line from the
    lines centroid (or label point) that is perpendicular to the bearing of the current polyline. """
    segment_returned = None
    center = linegeometry.centroid
    sr=linegeometry.spatialReference
    line_heading=get_line_heading(linegeometry,True)
    perpendicular_angle_start,perpendicular_angle_end=get_angle_difference(line_heading)
    point_start=translate_point(center,perpendicular_angle_start,whisker_width)
    point_end= translate_point(center,perpendicular_angle_end,whisker_width)
    inputs_line = arcpy.Array([point_start,point_end])
    segment_returned = arcpy.Polyline(inputs_line,sr)
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
                                            has_m="SAME_AS_TEMPLATE",has_z="SAME_AS_TEMPLATE")
        preFields = get_fields(in_fc)
        fields = ["SHAPE@"] + preFields
        cursor = arcpy.da.SearchCursor(in_fc, fields)
        with arcpy.da.InsertCursor(Out_FC, fields) as insertCursor:
            arc_print("Established insert cursor for " + str(FileName) + ".", True)
            lineCounter = 0
            for singleline in cursor:
                try:
                    segment_rows = []
                    lineCounter += 1
                    linegeo = singleline[get_f_index(fields, "SHAPE@")]
                    # Function splits linegeometry based on method and split value
                    if sample_length:
                        linegeo = sample_line_from_center(linegeo, sample_length)
                    split_segment_geometry = generate_whisker_from_polyline(linegeo,
                                                                            line_length(singleline, out_whisker_field,
                                                                                        out_whisker_width,
                                                                                        fields))
                    segID = 0
                    try:
                        segID += 1
                        segmentedRow = copy_altered_row(singleline, fields, {"SHAPE@": split_segment_geometry})
                        segment_rows.append(segmentedRow)
                    except:
                        arc_print("Could not iterate through line segment " + str(segID) + ".")
                        break

                    for row in segment_rows:
                        insertCursor.insertRow(row)
                    if lineCounter % 500 == 0:
                        arc_print("Iterated and generated whiskers for feature " + str(lineCounter) + ".", True)
                except Exception as e:
                    arc_print("Failed to iterate through and generated whiskers for feature " + str(lineCounter) + ".", True)
                    arc_print(e.args[0])
            del cursor, insertCursor, fields, preFields, OutWorkspace, lineCounter
            arc_print("Script Completed Successfully.", True)
    except arcpy.ExecuteError:
        arc_print(arcpy.GetMessages(2))
    except Exception as e:
        arc_print(e.args[0])

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
    feature_line_whisker(FeatureClass, float(Desired_Whisker_Width),Feature_Whisker_Field,float(Line_Sample_Length),
                      OutFeatureClass)
