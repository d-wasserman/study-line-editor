# --------------------------------
# Name: featurelinelib.py
# Purpose: This file serves as a function library for the Feature line Toolboxes. Import as fll.
# Current Owner: David Wasserman
# Last Modified: 8/31/2019
# Copyright:   David Wasserman
# ArcGIS Version:   ArcGIS Pro/10.4
# Python Version:   3.5/2.7
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
import arcpy
import os, re


# Function Definitions
def func_report(function=None, reportBool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def func_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if reportBool:
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


def arc_tool_report(function=None, arcToolMessageBool=False, arcProgressorBool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""

    def arc_tool_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if arcToolMessageBool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(func_result)))
                if arcProgressorBool:
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


@arc_tool_report
def field_exist(featureclass, fieldname):
    """ArcFunction
     Check if a field in a feature class field exists and return true it does, false if not.- David Wasserman"""
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (fieldCount >= 1) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False


@arc_tool_report
def add_new_field(in_table, field_name, field_type, field_precision="#", field_scale="#", field_length="#",
                  field_alias="#", field_is_nullable="#", field_is_required="#", field_domain="#"):
    """ArcFunction
    Add a new field if it currently does not exist. Add field alone is slower than checking first.- David Wasserman"""
    if field_exist(in_table, field_name):
        print(field_name + " Exists")
        arcpy.AddMessage(field_name + " Exists")
    else:
        print("Adding " + field_name)
        arcpy.AddMessage("Adding " + field_name)
        arcpy.AddField_management(in_table, field_name, field_type, field_precision, field_scale,
                                  field_length,
                                  field_alias,
                                  field_is_nullable, field_is_required, field_domain)


@arc_tool_report
def validate_df_names(dataframe, output_feature_class_workspace):
    """Returns pandas dataframe with all col names renamed to be valid arcgis table names."""
    new_name_list = []
    old_names = dataframe.columns.names
    for name in old_names:
        new_name = arcpy.ValidateFieldName(name, output_feature_class_workspace)
        new_name_list.append(new_name)
    rename_dict = {i: j for i, j in zip(old_names, new_name_list)}
    dataframe.rename(index=str, columns=rename_dict)
    return dataframe


@arc_tool_report
def arcgis_table_to_dataframe(in_fc, input_fields, query="", skip_nulls=False, null_values=None):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields."""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    final_fields = [OIDFieldName] + input_fields
    np_array = arcpy.da.TableToNumPyArray(in_fc, final_fields, query, skip_nulls, null_values)
    object_id_index = np_array[OIDFieldName]
    fc_dataframe = pd.DataFrame(np_array, index=object_id_index, columns=input_fields)
    return fc_dataframe


@arc_tool_report
def arcgis_table_to_df(in_fc, input_fields, query=""):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
        input fields. Uses a da search cursor."""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    final_fields = [OIDFieldName] + input_fields
    record_list = [row for row in arcpy.da.SearchCursor(in_fc, final_fields, query)]
    oid_collection = [row[0] for row in record_list]
    fc_dataframe = pd.DataFrame(record_list, index=oid_collection, columns=final_fields)
    return fc_dataframe


@arc_tool_report
def arc_unique_values(table, field, filter_falsy=False):
    """This function will return a list of unique values from a passed field. If the optional bool is true,
    this function will scrub out null/falsy values. """
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        if filter_falsy:
            return sorted({row[0] for row in cursor if row[0]})
        else:
            return sorted({row[0] for row in cursor})


def copy_altered_row(row, field_list, field_dict, replacement_dict):
    """This utility function copy a row with the listed fields, but if there is a key in the replacement dictionary
    the item in that dictionary will replace the item that was originally in that row. Useful for cursor short hand.
    :param - row - row of an input cursor
    :param - field_list - list of field names
    :param - field_dict - dictionary of fields and their indexes as values
    :param - replacement_dict - the dictionary with values to replace the row values with"""
    try:
        new_row = []
        keyList = replacement_dict.keys()
        for field in field_list:
            try:
                if field in keyList:
                    new_row.append(replacement_dict[field])
                else:
                    new_row.append(row[field_dict[field]])
            except:
                arc_print("Could not replace field {0} with its accepted value. Check field names for match.".format(
                    str(field)), True)
                new_row.append(None)  # Append a null value where it cannot find a value to the list.
        return new_row
    except:
        arc_print("Could not get row fields for the following input {0}, returned an empty list.".format(str(row)),
                  True)
        arcpy.AddWarning(
            "Could not get row fields for the following input {0}, returned an empty list.".format(str(row)))
        new_row = []
        return new_row


@arc_tool_report
def line_length(row, field, constant_len, f_dict, print_bool=False):
    """Returns the appropriate value type  based on the options selected: retrieved form field or uses a constant
    :param - row - cursor row as a list
    :param - field - field with geometry
    :param - constant_len - len choice if constant
    :param - f_dict - field dictionary of field name index pairs
    :param - print_bool - print boolean
    :return - int"""
    if f_dict.get(field, None) and field and field != "#":
        if print_bool:
            arc_print("Using size field to create output geometries.", True)
        return abs(row[f_dict[field]])
    else:
        if print_bool:
            arc_print("Using size input value to create same sized output geometries.", True)
        return abs(constant_len)


def get_fields(feature_class, excluded_tolkens=["OID", "Geometry"], excluded_fields=["shape_area", "shape_length"]):
    """Get all field names from an incoming feature class defaulting to excluding tolkens and shape area & length.
    :param - feature_class - Feature class
    :param - excluded_tolkens - list excluding tokens list,
    :param - excluded_fields -  excluded fields list.
    :return - List of field names from input feature class. """
    try:
        try:  # If  A feature Class split to game name
            fcName = os.path.split(feature_class)[1]
        except:  # If a Feature Layer, just print the Layer Name
            fcName = feature_class
        field_list = [f.name for f in arcpy.ListFields(feature_class) if f.type not in excluded_tolkens
                      and f.name.lower() not in excluded_fields]
        arc_print("The field list for {0} is:{1}".format(str(fcName), str(field_list)), True)
        return field_list
    except:
        arc_print(
            "Could not get fields for the following input {0}, returned an empty list.".format(
                str(feature_class)),
            True)
        arcpy.AddWarning(
            "Could not get fields for the following input {0}, returned an empty list.".format(
                str(feature_class)))
        field_list = []
        return field_list


def construct_index_dict(field_names, index_start=0):
    """This function will construct a dictionary used to retrieve indexes for cursors.
    :param - field_names - list of strings (field names) to load as keys into a dictionary
    :param - index_start - an int indicating the beginning index to start from (default 0).
    :return - dictionary in the form of {field:index,...}"""
    dict = {}
    for index, field in enumerate(field_names, start=index_start):
        dict.setdefault(field, index)
    return dict


# End do_analysis function

# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Define input parameters
    print("Function library: ArcNumericalLib.py")
