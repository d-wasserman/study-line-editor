# Name: FeatureLineSplit.py
# Purpose: Take a feature class and proportionally split each unique feature line into segments of a target count
# or target distance. Similar to editing tools done manually.This version of the tool will join the original fields
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
def split_line_geometry(linegeometry, split_value, split_method="LENGTH", best_fit_bool=True):
    """This function will take an ArcPolyline, a split value, a split method of either 'LENGTH' or 'SEGMENT COUNT', and
    boolean that determines if the lines split are the best of fit based on the length. The function returns a list of
    line geometries whose length and number are determined by the split value, split method, and best fit settings.
    Line Geometry- arc polyline/split value- the length or desired number of segments, /split method- determines if
    split value is treated as a length target or segment count target/ best fit bool determines if the length is rounded
    to be segments of equal length."""
    segment_list = []
    line_length = float(linegeometry.length)
    if str(split_method).upper() == "LENGTH" and not best_fit_bool:
        segment_total = int(math.ceil(line_length / float(split_value)))
        for elinesegindex in range(0, segment_total):
            start_position = (elinesegindex * (int(split_value)))
            end_position = (elinesegindex + 1) * int(split_value)
            seg = linegeometry.segmentAlongLine(start_position, end_position)
            segment_list.append(seg)
    else:
        segmentation_value = int(round(max([1, split_value])))
        if str(split_method).upper() == "LENGTH" and best_fit_bool:
            segmentation_value = int(max([1, round(line_length / float(split_value))]))
        for elinesegindex in range(0, segmentation_value):
            seg = linegeometry.segmentAlongLine((elinesegindex / float(segmentation_value)),
                                                ((elinesegindex + 1) / float(segmentation_value)), True)
            segment_list.append(seg)
    return segment_list


def feature_line_split(in_fc, out_count_value, out_count_field, split_method, best_fit_bool, Out_FC):
    """ This function will split each feature in a feature class into a desired number of equal length segments based
    on a specified distance or target segment count based on an out count value or field."""
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
                    split_segment_list = split_line_geometry(linegeo,
                                                             line_length(singleline, out_count_field, out_count_value,
                                                                         fields), split_method, best_fit_bool)
                    segID = 0
                    for segment in split_segment_list:
                        try:
                            segID += 1
                            segmentedRow = copy_altered_row(singleline, fields, {"SHAPE@": segment})
                            segment_rows.append(segmentedRow)
                        except:
                            arc_print("Could not iterate through line segment " + str(segID) + ".")
                            break
                    if len(segment_rows) == len(
                            split_segment_list):  # Unload by feature so partial segments are not made.
                        for row in segment_rows:
                            insertCursor.insertRow(row)
                    if lineCounter % 500 == 0:
                        arc_print("Iterated through and split feature " + str(lineCounter) + ".", True)
                except Exception as e:
                    arc_print("Failed to iterate through and a split feature " + str(lineCounter) + ".", True)
                    arc_print(e.args[0])
            del cursor, insertCursor, fields, preFields, OutWorkspace, lineCounter, split_segment_list
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
    Desired_Feature_Count = arcpy.GetParameter(1)
    Feature_Count_Field = arcpy.GetParameterAsText(2)
    Split_Method = arcpy.GetParameterAsText(3)
    Best_Fit_Bool = arcpy.GetParameter(4)
    OutFeatureClass = arcpy.GetParameterAsText(5)
    feature_line_split(FeatureClass, Desired_Feature_Count, Feature_Count_Field, Split_Method, Best_Fit_Bool,
                       OutFeatureClass)
