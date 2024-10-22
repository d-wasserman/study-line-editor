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

import itertools
import math
import os

# Import Modules
import arcpy

try:
    import pandas as pd
except:
    arcpy.AddWarning(
        "Some tools require the Pandas installed in the ArcGIS Python Install."
        " Might require installing pre-requisite libraries and software."
    )


# Function Definitions
def func_report(function=None, reportBool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
    reporting (if function fails it will report the name of the function that failed and its arguments. If a report
     boolean is true the function will report inputs and outputs of a function.-David Wasserman
    """

    def func_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if reportBool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Output(s):{0}".format(str(func_result)))
                return func_result
            except Exception as e:
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(
                        str(function.__name__), str(args)
                    )
                )
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
     boolean is true the function will report inputs and outputs of a function.-David Wasserman
    """

    def arc_tool_report_decorator(function):
        def func_wrapper(*args, **kwargs):
            try:
                func_result = function(*args, **kwargs)
                if arcToolMessageBool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Output(s):{0}".format(str(func_result)))
                if arcProgressorBool:
                    arcpy.SetProgressorLabel(
                        "Function:{0}".format(str(function.__name__))
                    )
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel(
                        "     Output(s):{0}".format(str(func_result))
                    )
                return func_result
            except Exception as e:
                arcpy.AddWarning(
                    "{0} - function failed -|- Function arguments were:{1}.".format(
                        str(function.__name__), str(args)
                    )
                )
                print(
                    "{0} - function failed -|- Function arguments were:{1}.".format(
                        str(function.__name__), str(args)
                    )
                )
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
    """This function is used to simplify using arcpy reporting for tool creation,if progressor bool is true it will
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
    Check if a field in a feature class field exists and return true it does, false if not.- David Wasserman
    """
    fieldList = arcpy.ListFields(featureclass, fieldname)
    fieldCount = len(fieldList)
    if (
        fieldCount >= 1
    ) and fieldname.strip():  # If there is one or more of this field return true
        return True
    else:
        return False


@arc_tool_report
def add_new_field(
    in_table,
    field_name,
    field_type,
    field_precision="#",
    field_scale="#",
    field_length="#",
    field_alias="#",
    field_is_nullable="#",
    field_is_required="#",
    field_domain="#",
):
    """ArcFunction
    Add a new field if it currently does not exist. Add field alone is slower than checking first.- David Wasserman
    """
    if field_exist(in_table, field_name):
        print(field_name + " Exists")
        arcpy.AddMessage(field_name + " Exists")
    else:
        print("Adding " + field_name)
        arcpy.AddMessage("Adding " + field_name)
        arcpy.AddField_management(
            in_table,
            field_name,
            field_type,
            field_precision,
            field_scale,
            field_length,
            field_alias,
            field_is_nullable,
            field_is_required,
            field_domain,
        )


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
def arcgis_table_to_dataframe(
    in_fc, input_fields, query="", skip_nulls=False, null_values=None
):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields. Uses TableToNumPyArray to get initial data."""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    if input_fields:
        final_fields = [OIDFieldName] + input_fields
    else:
        final_fields = [field.name for field in arcpy.ListFields(in_fc)]
    np_array = arcpy.da.TableToNumPyArray(
        in_fc, final_fields, query, skip_nulls, null_values
    )
    object_id_index = np_array[OIDFieldName]
    fc_dataframe = pd.DataFrame(np_array, index=object_id_index, columns=input_fields)
    return fc_dataframe


@arc_tool_report
def arcgis_table_to_df(in_fc, input_fields=None, query=""):
    """Function will convert an arcgis table into a pandas dataframe with an object ID index, and the selected
    input fields using an arcpy.da.SearchCursor.
    :param - in_fc - input feature class or table to convert
    :param - input_fields - fields to input to a da search cursor for retrieval
    :param - query - sql query to grab appropriate values
    :returns - pandas.DataFrame"""
    OIDFieldName = arcpy.Describe(in_fc).OIDFieldName
    if input_fields:
        final_fields = [OIDFieldName] + input_fields
    else:
        final_fields = [field.name for field in arcpy.ListFields(in_fc)]
    data = [
        row for row in arcpy.da.SearchCursor(in_fc, final_fields, where_clause=query)
    ]
    fc_dataframe = pd.DataFrame(data, columns=final_fields)
    fc_dataframe = fc_dataframe.set_index(OIDFieldName, drop=True)
    return fc_dataframe


@arc_tool_report
def arc_unique_values(table, field, filter_falsy=False):
    """This function will return a list of unique values from a passed field. If the optional bool is true,
    this function will scrub out null/falsy values."""
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
    :param - replacement_dict - the dictionary with values to replace the row values with
    """
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
                arc_print(
                    "Could not replace field {0} with its accepted value. Check field names for match.".format(
                        str(field)
                    ),
                    True,
                )
                new_row.append(
                    None
                )  # Append a null value where it cannot find a value to the list.
        return new_row
    except:
        arc_print(
            "Could not get row fields for the following input {0}, returned an empty list.".format(
                str(row)
            ),
            True,
        )
        arcpy.AddWarning(
            "Could not get row fields for the following input {0}, returned an empty list.".format(
                str(row)
            )
        )
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
            arc_print(
                "Using size input value to create same sized output geometries.", True
            )
        return abs(constant_len)


def get_fields(
    feature_class,
    excluded_tolkens=["OID", "Geometry"],
    excluded_fields=["shape_area", "shape_length"],
):
    """Get all field names from an incoming feature class defaulting to excluding tolkens and shape area & length.
    :param - feature_class - Feature class
    :param - excluded_tolkens - list excluding tokens list,
    :param - excluded_fields -  excluded fields list.
    :return - List of field names from input feature class."""
    try:
        try:  # If  A feature Class split to game name
            fcName = os.path.split(feature_class)[1]
        except:  # If a Feature Layer, just print the Layer Name
            fcName = feature_class
        field_list = [
            f.name
            for f in arcpy.ListFields(feature_class)
            if f.type not in excluded_tolkens and f.name.lower() not in excluded_fields
        ]
        arc_print(
            "The field list for {0} is:{1}".format(str(fcName), str(field_list)), True
        )
        return field_list
    except:
        arc_print(
            "Could not get fields for the following input {0}, returned an empty list.".format(
                str(feature_class)
            ),
            True,
        )
        arcpy.AddWarning(
            "Could not get fields for the following input {0}, returned an empty list.".format(
                str(feature_class)
            )
        )
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


def find_smallest_angle(angle1, angle2, absolute_value=False):
    """Find the smallest angle between two provided azimuth angles.
    @param: - angle1 - first angle in degrees between 0 and 360 degrees
    @param: - angle2 - first angle in degrees between 0 and 360 degrees
    @param: - absolute_value - if true, return absolute value of result
    """
    diff = angle1 - angle2
    diff = (diff + 180) % 360 - 180
    if absolute_value:
        diff = abs(diff)
    return diff


def convert_to_azimuth(angle):
    """Converts Near 180 to -180 angles to Azimuth Angles. Will also normalize any number to 0-360 .
    @param: angle - angle denoted in terms of 180 to -180 degrees
    @returns angle - angle 0 to 360"""
    if angle <= 180 and angle > 90:
        azimuth_angles = 360.0 - (angle - 90)
    else:
        azimuth_angles = abs(angle - 90)
    if abs(azimuth_angles) > 360:
        azimuth_angles % 360
    return azimuth_angles


def arc_calculate_segment_bearing(shape_obj, method="GEODESIC"):
    """Calculate the bearing from a single shape object and return the angle.
    @param - shape object from arcpy for a polyline. Uses Arc methods.
    returns - angle - float - angle in degrees (not azimuth)"""
    sr = shape_obj.spatialReference
    first_point = arcpy.PointGeometry(shape_obj.firstPoint, sr)
    last_point = arcpy.PointGeometry(shape_obj.lastPoint, sr)
    angle, dist = first_point.angleAndDistanceTo(last_point, method)
    return angle


def calculate_segment_bearing(shape_obj):
    """Calculate the bearing from a single shape object and return the angle. Assumes projected coords.
    @param - shape object from arcpy for a polyline
    returns - angle - float - angle in degrees (not azimuth)"""
    first_point = shape_obj.firstPoint
    last_point = shape_obj.lastPoint
    first_x = first_point.X
    first_y = first_point.Y
    last_x = last_point.X
    last_y = last_point.Y
    dx = last_x - first_x
    dy = last_y - first_y
    rads = math.atan2(dy, dx)  # Relative to North
    angle = math.degrees(rads)
    return angle


def calculate_line_bearing(in_fc, field, convert_azimuth=False):
    """Adds a new field and update it to provide a line bearing in degrees.
    @param - in_fc - input feature class to add bear
    @param - field - new field to add bearing
    @param - convert_azimuth - convert the bearing from 0 to 360 degrees"""
    add_new_field(in_fc, field, "DOUBLE")
    return_oid_bearing_dict = {}
    sr_type = arcpy.Describe(in_fc).spatialReference.type
    with arcpy.da.UpdateCursor(in_fc, ["OID@", "SHAPE@", field]) as cursor:
        for row in cursor:
            ObjectID = row[0]
            shape = row[1]
            if sr_type == "Geographic":
                angle = arc_calculate_segment_bearing(shape)
            else:
                angle = calculate_segment_bearing(
                    shape
                )  # TODO speed test - use planar method vs. this.
            if convert_azimuth:
                angle = convert_to_azimuth(angle)
            row[2] = angle
            return_oid_bearing_dict.update({ObjectID: angle})
            cursor.updateRow(row)
        arc_print("Updated Line Bearing field.")
    del cursor
    return return_oid_bearing_dict


def find_smallest_angle_from_intersecting_lines(
    angle_1, angle_2, angle_1_inverse=None, angle_2_inverse=None
):
    """Given two angles indicating a lines orientation, this function will determine the inverse versions of their angles, and
    test every combination of angle to determine the smallest possible angle between them.
    @:param - angle_1 - first angle of a line bearing of unknown orientation. Assumes azimuth angle 0-360 degrees.
    @:param - angle_2 - second angle of a line bearing of unknown orientation. Assumes azimuth angle 0-360 degrees.
    @:param - angle_1_inverse - inverse angle of angle_1- if not provided, is derived.
    @:param - angle_2_inverse- inverse angle of angle_2- if not provided, is derived."""
    if angle_1_inverse is None:
        angle_1_inverse = (angle_1 + 180) % 360
    if angle_2_inverse is None:
        angle_2_inverse = (angle_2 + 180) % 360
    angle_combinations = itertools.combinations(
        [angle_1, angle_2, angle_1_inverse, angle_2_inverse], 2
    )
    smallest_angle = None
    for angle_1, angle_2 in angle_combinations:
        small_angle = find_smallest_angle(angle_1, angle_2, True)
        if smallest_angle is None:
            smallest_angle = small_angle
        else:
            smallest_angle = min([small_angle, smallest_angle])
    return smallest_angle


def find_smallest_angle_column(
    df,
    bearing_column_1,
    bearing_column_2,
    new_field_prexix="Inverted_",
    new_column="Smallest_Angle",
):
    """Add a column to pandas dataframe that takes a 0 to 360 degree azimuth angle and adds its inverse.
    @:param - df - a pandas dataframe
    @:param - bearing_column_1 - column in dataframe with the angle the line is pointing
    @:param - bearing_column_2 - column in dataframe with the angle the line is pointing
    @:param - new_field_prefix - inverted angle columns added for each angle with this prefix added to them
    @:param - new_column - name of the inverted azimuth angle"""
    inverted_col_1 = str(new_field_prexix) + bearing_column_1
    inverted_col_2 = str(new_field_prexix) + bearing_column_2
    df[inverted_col_1] = (df[bearing_column_1] + 180).mod(360)
    df[inverted_col_2] = (df[bearing_column_2] + 180).mod(360)
    df[new_column] = df.apply(
        lambda x: find_smallest_angle_from_intersecting_lines(
            x[bearing_column_1],
            x[bearing_column_2],
            x[inverted_col_1],
            x[inverted_col_2],
        ),
        axis=1,
    )
    return df


def get_angle_difference(angle, difference=90):
    """Given an azimuth angle (0-360), it will return the two azimuth angles (0-360) as a tuple that are perpendicular to it."""
    angle_lower, angle_higher = (angle + difference) % 360, (angle - difference) % 360
    return (angle_lower, angle_higher)


def translate_point(point, angle, radius, is_degree=True):
    """Passed a point object (arcpy) this funciton will translate it and
    return a modified clone based on a given angle out a set radius."""
    if is_degree:
        angle = math.radians(angle)
    new_x = math.cos(angle) * radius + point.X
    new_y = math.sin(angle) * radius + point.Y
    new_point = arcpy.Point(new_x, new_y)
    return new_point


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


def generate_whisker_from_polyline(linegeometry, whisker_width):
    """This function will take an ArcPolyline and a target whisker width,and it will create a new line from the
    lines centroid (or label point) that is perpendicular to the bearing of the current polyline.
    """
    segment_returned = None
    center = linegeometry.centroid
    sr = linegeometry.spatialReference
    line_heading = arc_calculate_segment_bearing(linegeometry)
    line_heading = convert_to_azimuth(line_heading)
    perpendicular_angle_start, perpendicular_angle_end = get_angle_difference(
        line_heading
    )
    point_start = translate_point(center, perpendicular_angle_start, whisker_width)
    point_end = translate_point(center, perpendicular_angle_end, whisker_width)
    inputs_line = arcpy.Array([point_start, point_end])
    segment_returned = arcpy.Polyline(inputs_line, sr)
    # This function fails if the line is shorter than the pull value, in this case no geometry is returned.
    return segment_returned


def split_segment_by_length(
    linegeometry, split_value, overlap_percentage=0, best_fit_bool=True
):
    """This function will take an ArcPolyline, a split value of a target length for a split segment, and
    boolean that determines if the lines split are the best of fit based on the length.
    Parameters
    ----------------
    linegeometry - arc polyline
    split_value - the length in the current projection
    overlap_percentage - the degree of overlap as a percentage of the line length
    best_fit_bool -  determines if the length is rounded to be segments of equal length.
    Returns
    ----------------
    segment_list - list of split geometries."""
    segment_list = []
    line_length = float(linegeometry.length)
    if not best_fit_bool:
        segment_total = int(math.ceil(line_length / float(split_value)))
        percent_split = False
    else:
        segmentation_value = int(max([1, round(line_length / float(split_value))]))
        segment_total = segmentation_value
        percent_split = True
    for line_seg_index in range(0, segment_total):
        line_seg_index_start = (
            line_seg_index
            if overlap_percentage == 0
            else max([0, float(line_seg_index) - float(overlap_percentage)])
        )
        start_position = (
            (line_seg_index_start * float(split_value))
            if not percent_split
            else (line_seg_index_start / float(segmentation_value))
        )
        line_seg_index_end = (
            line_seg_index
            if overlap_percentage == 0
            else min([segment_total, float(line_seg_index) + float(overlap_percentage)])
        )
        end_position = (
            ((line_seg_index_end + 1) * float(split_value))
            if not percent_split
            else ((line_seg_index_end + 1) / float(segmentation_value))
        )
        seg = linegeometry.segmentAlongLine(start_position, end_position, percent_split)
        segment_list.append(seg)
    return segment_list


def split_segment_by_count(linegeometry, split_count, overlap_percentage=0.0):
    """This function will take an ArcPolyline, a split count for the number of lines to return. The function returns a list of
    line geometries whose length and number are determined by the split value, split method, and best fit settings.
    Parameters
    ----------------
    linegeometry - arc polyline
    split_count - the count of the number of lines to return
    Returns
    ----------------
    segment_list - list of split geometries."""
    segment_list = []
    segmentation_value = int(round(max([1, split_count])))
    for line_seg_index in range(0, segmentation_value):
        line_seg_index_start = (
            line_seg_index
            if overlap_percentage == 0
            else max([0, float(line_seg_index) - float(overlap_percentage)])
        )
        line_seg_index_end = (
            line_seg_index
            if overlap_percentage == 0
            else min(
                [segmentation_value, float(line_seg_index) + float(overlap_percentage)]
            )
        )
        seg = linegeometry.segmentAlongLine(
            (line_seg_index_start / float(segmentation_value)),
            ((line_seg_index_end + 1) / float(segmentation_value)),
            True,
        )
        segment_list.append(seg)
    return segment_list


# End do_analysis function

# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == "__main__":
    # Define input parameters
    print("Function library: linelibrary.py")
