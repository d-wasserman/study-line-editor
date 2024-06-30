# Name: FeatureLineGapClosure.py
# Purpose: This script fills gaps between line feature end points within a specified search radius,
# improving connectivity. It analyzes spatial relationships to create new lines in an output
# feature class, enhancing network integration.
# Author: David Wasserman
# AI Disclosure: Partial Code Generation Feb 2024 ChatGPT 4.
# Last Modified: 3/1/2024
# Copyright: David Wasserman
# Python Version:  3.9
# --------------------------------
# Copyright 2024 David J. Wasserman
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
import arcpy
import os
import linelibrary as ll


def create_gap_filling_lines(
    input_line_features,
    transfer_fields,
    output_feature_class,
    search_radius="500 Feet",
    connection_count=1,
):
    """Identifies and fills gaps between line feature end points within a specified search radius.
    Adds the FIDs of the line end points as start and end attributes and includes a field for the near distance.

    Parameters:
    - input_line_features (FeatureClass): The input line features to analyze.
    - transfer_fields(Fields): These are fields from the A-B end points from the original line features that will be added with "A_" or "B_" fields.
    - output_feature_class (FeatureClass): The output feature class for storing new lines that fill the identified gaps.
    - search_radius (LinearUnit): The search radius within which to identify the closest end points for gap filling.
    - connection_count(int): The number of connections to create between end points in the order of proximity.
    """
    # try:
    ll.arc_print("Feature class validation...")
    arcpy.env.overwriteOutput = True
    oid = arcpy.Describe(input_line_features).OIDFieldName
    workspace = "in_memory"
    pt_id, ln_id = "PT_ID", "LINE_ID"
    workspace, output_fc_name = os.path.split(output_feature_class)
    arcpy.AddField_management(input_line_features, ln_id, "LONG")
    arcpy.CalculateField_management(
        input_line_features, ln_id, "!{0}!".format(oid), "PYTHON3"
    )
    ll.arc_print("Explode the line features to their end points...")
    end_points_temp = os.path.join(workspace, "end_points")
    arcpy.FeatureVerticesToPoints_management(
        input_line_features, end_points_temp, "BOTH_ENDS"
    )
    end_pt_field_list = [field.name for field in arcpy.ListFields(end_points_temp)]
    end_pt_field_types = [field.type for field in arcpy.ListFields(end_points_temp)]
    end_pt_field_dict = {i: j for i, j in zip(end_pt_field_list, end_pt_field_types)}
    ll.arc_print(
        "Filtering transfer fields to feature end points fields are: {0}".format(
            end_pt_field_list
        )
    )
    transfer_fields = [
        i for i in transfer_fields if i in end_pt_field_list and i != ln_id
    ]
    transfer_types = [end_pt_field_dict[i] for i in transfer_fields]
    ll.arc_print("Add a unique identifier to each end point...")
    arcpy.AddField_management(end_points_temp, pt_id, "LONG")
    arcpy.CalculateField_management(
        end_points_temp, pt_id, "!{0}!".format(oid), "PYTHON3"
    )
    ll.arc_print(
        "Construct the near table to find closest points within the search radius..."
    )
    near_table_temp = os.path.join(workspace, "end_points_near")
    arcpy.GenerateNearTable_analysis(
        end_points_temp,
        end_points_temp,
        near_table_temp,
        search_radius,
        "NO_LOCATION",
        "NO_ANGLE",
        "ALL",
        closest_count=connection_count,
    )
    ll.arc_print(
        "Filter out points that are from the same line feature or are touching an existing point..."
    )
    # Load data into a DataFrame
    input_fields_df = ["SHAPE@", pt_id, ln_id]
    if transfer_fields:
        input_fields_df = ["SHAPE@", pt_id, ln_id] + transfer_fields
        ll.arc_print("Attempting to transfer fields: {0}".format(input_fields_df))
    df = ll.arcgis_table_to_df(end_points_temp, input_fields=input_fields_df)
    df.set_index(pt_id)
    # Create a dictionary from the columns
    sm_df = df[[ln_id, pt_id]].copy()
    groups = sm_df.groupby(pt_id)
    line_dict = {pt_id: group[ln_id].values[0] for pt_id, group in groups}

    # ll.arc_print(line_dict)
    filtered_near_table = [
        row
        for row in arcpy.da.SearchCursor(
            near_table_temp, ["IN_FID", "NEAR_FID", "NEAR_DIST"]
        )
        if (line_dict[row[0]] != line_dict[row[1]]) or row[2] <= 0
    ]  # Filter out those of the same line or touching now

    ll.arc_print("Create the output feature class...")
    arcpy.CreateFeatureclass_management(
        workspace, output_fc_name, "POLYLINE", spatial_reference=input_line_features
    )
    ll.arc_print("Adding new fields to output...")
    a_nd, b_nd = "A_NODE", "B_NODE"
    arcpy.AddField_management(output_feature_class, a_nd, "LONG")
    arcpy.AddField_management(output_feature_class, b_nd, "LONG")
    for name_f, type_f in zip(transfer_fields, transfer_types):
        a_field, b_field = "A_" + str(name_f), "B_" + str(name_f)
        arcpy.AddField_management(output_feature_class, a_field, type_f)
        arcpy.AddField_management(output_feature_class, b_field, type_f)
    ll.arc_print("Insert new lines into the output feature class...")
    sr = arcpy.Describe(input_line_features).spatialReference
    count_hash = {}
    a_nd_tf = ["A_" + str(i) for i in transfer_fields]
    b_nd_tf = ["B_" + str(i) for i in transfer_fields]
    ab_nd_tdf = [
        sub[item] for item in range(len(b_nd_tf)) for sub in [a_nd_tf, b_nd_tf]
    ]
    # ab_dict = {i:["A_"+str(i),"B_"+str(i)] for i in transfer_fields }
    output_fields = ["SHAPE@", a_nd, b_nd]
    if ab_nd_tdf:
        output_fields = ["SHAPE@", a_nd, b_nd] + ab_nd_tdf
    with arcpy.da.InsertCursor(output_feature_class, output_fields) as insert_cursor:
        for row in filtered_near_table:
            counter = count_hash.setdefault(row[0], 0)
            if counter >= connection_count:
                # Don't create new lines for those beyond
                continue
            start_point = df[df[pt_id] == row[0]]["SHAPE@"].values[0]
            end_point = df[df[pt_id] == row[1]]["SHAPE@"].values[0]
            line = arcpy.Polyline(
                arcpy.Array([start_point.firstPoint, end_point.lastPoint]), sr
            )
            new_row = [line, row[0], row[1]]
            if transfer_fields:
                for field in transfer_fields:
                    start_val = df[df[pt_id] == row[0]][field].values[0]
                    end_val = df[df[pt_id] == row[1]][field].values[0]
                    new_row.append(start_val)
                    new_row.append(end_val)
            insert_cursor.insertRow(new_row)
            count_hash[row[0]] += 1

        ll.arc_print("Gap filling lines created successfully.")

    # except Exception as e:
    #     arcpy.AddError(str(e))


if __name__ == "__main__":
    # Define Inputs
    InputLineFeatures = arcpy.GetParameterAsText(0)
    TransferFields = arcpy.GetParameterAsText(1).split(";")
    OutputFeatureClass = arcpy.GetParameterAsText(2)
    SearchRadius = arcpy.GetParameterAsText(3)
    NumberOfConnections = int(arcpy.GetParameterAsText(4))

    create_gap_filling_lines(
        InputLineFeatures,
        TransferFields,
        OutputFeatureClass,
        SearchRadius,
        NumberOfConnections,
    )
