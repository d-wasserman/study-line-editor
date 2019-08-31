# Name: FeatureLinePull.py
# Purpose: Take a feature class and pull back a line equal to a target distance from either a start or end point
# position. This version of the tool will join the original fields.
# of the old feature class.
# Author: David Wasserman
# Last Modified: 6/7/2017
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
def pull_line_geometry(linegeometry, pull_value, end_point_bool=True, start_point_bool=True):
    """This function will take an ArcPolyline, a pull value, and a start and end point boolean. The function returns
    a a line geometry whose length are pulled back based on the input parameters.
    Line Geometry- arc polyline/pull_value- the length or desired number of segments, /pull_value- the distance the
    line will be pulled back from either the start or end point/ end_point_pull- if true, the end point of the line will
    be pulled back the target distance, start_point_bool- if true, the start point of the line will be pulled back the
    target distance. """
    segment_returned = None
    line_length = float(linegeometry.length)
    end_point_start_position = line_length
    start_point_start_position = 0
    try:
        if end_point_bool:
            end_point_start_position = line_length - pull_value
        if start_point_bool:
            start_point_start_position = 0 + pull_value
        segment_returned = linegeometry.segmentAlongLine(start_point_start_position, end_point_start_position)
    except:  # This function fails if the line is shorter than the pull value, in this case no geometry is returned.
        return None
    return segment_returned


def feature_line_pull(in_fc, out_pull_value, out_pull_field, start_point_bool, end_point_bool, Out_FC):
    """Take a feature class and pull back a line equal to a target distance from either a start or end point position.
     This version of the tool will join the original fields."""
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(Out_FC)[0]
        FileName = os.path.split(Out_FC)[1]
        arcpy.CreateFeatureclass_management(OutWorkspace, FileName, "POLYLINE", in_fc, spatial_reference=in_fc,
                                            has_m="SAME_AS_TEMPLATE", has_z="SAME_AS_TEMPLATE")
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
                    split_segment_geometry = pull_line_geometry(linegeo,
                                                                line_length(singleline, out_pull_field, out_pull_value,
                                                                            fields), start_point_bool, end_point_bool)
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
                        arc_print("Iterated through and split feature " + str(lineCounter) + ".", True)
                except Exception as e:
                    arc_print("Failed to iterate through and a split feature " + str(lineCounter) + ".", True)
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
    Desired_Feature_Pull = arcpy.GetParameter(1)
    Feature_Pull_Field = arcpy.GetParameterAsText(2)
    Start_Point_Bool = arcpy.GetParameter(3)
    End_Point_Bool = arcpy.GetParameter(4)
    OutFeatureClass = arcpy.GetParameterAsText(5)
    feature_line_pull(FeatureClass, Desired_Feature_Pull, Feature_Pull_Field, Start_Point_Bool, End_Point_Bool,
                      OutFeatureClass)
