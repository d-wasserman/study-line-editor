# Name: FeatureLineCorridorAssembly.py
# Purpose: This tool normalizes center line networks by assembling them into continuous parallel corridors and
# attaching a corridor ID that can be used with a dissolve to the input network.
# Author: David Wasserman
# Last Modified: 1/1/2020
# Copyright: David Wasserman
# Python Version:  2.7/3.6
# --------------------------------
# Copyright 2020 David J. Wasserman
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
import pandas as pd
import numpy as np
import os
import linelibrary as ll


def assemble_corridors_from_network(input_network, output_network, connected_range="0.5 Feet", parallel_threshold=15,
                                    near_table=None):
    """This tool normalizes center line networks by assembling them into continuous parallel corridors and
    attaching a corridor ID that can be used with a dissolve to the input network.
    Parameters
    -------------------
    input_network - input network to attach corridor ids to.
    output_network - output network with attached corridor ids.
    connected_range - the distance between lines that is considered for a connected relationship.
    parallel_threshold - threshold of angles in degrees between parallel lines and non-parallel lines.
    temp_near_table - temporary near table used to compute line relationships.  """
    near_table = os.path.join("in_memory", "Near_Table")
    bearing_field = "Azimuth"
    if near_table is None:
        near_table = os.path.join("in_memory", "Temp_Near_Table")
    arcpy.env.overwriteOutput = True
    ll.arc_print("Creating network copy...")
    if arcpy.Exists(output_network):
        arcpy.DeleteFeatures_management(output_network)
    arcpy.CopyFeatures_management(input_network, output_network)
    ll.calculate_line_bearing(output_network, bearing_field, True)
    ll.arc_print("Bearing field added...")
    desc = arcpy.Describe(output_network)
    oid = desc.OIDFieldName
    line_bearing_df = ll.arcgis_table_to_df(output_network, [bearing_field])
    line_bearing_df[bearing_field]
    ll.arc_print("Generating near table for parallel analysis...")
    arcpy.GenerateNearTable_analysis(output_network, output_network, near_table, search_radius=connected_range,
                                     closest=False)
    near_df = ll.arcgis_table_to_df(near_table)
    near_df = near_df.merge(line_bearing_df, how="left", left_on="IN_FID", right_index=True)
    near_df = near_df.rename(columns={bearing_field: "IN_" + str(bearing_field)})
    near_df = near_df.merge(line_bearing_df, how="left", left_on="NEAR_FID", right_index=True)
    near_df = near_df.rename(columns={bearing_field: "NEAR_" + str(bearing_field)})
    ll.arc_print("Determining smallest angle between two potential line directions...")
    near_df_w_angle = ll.find_smallest_angle_column(near_df, "IN_Azimuth", "NEAR_Azimuth")
    near_df["Parallel_Lines"] = np.where(near_df["Smallest_Angle"] <= parallel_threshold, 1, 0)
    near_df["Smallest_Angle"] = np.where(near_df["Parallel_Lines"] == 1, np.NaN, near_df["Smallest_Angle"])
    # The links spatial relations are all encoded in this table.
    # Anything with close to zero for an angle is considered parallel.
    # We want to flat all parallel lines, and then drop them from the table for final summary statistics.
    angle_groups = near_df_w_angle.groupby("IN_FID")
    agg_dict = {"NEAR_FID": "count", "Smallest_Angle": ["min", "max", "mean"], "Parallel_Lines": "first"}
    angle_results = angle_groups.agg(agg_dict)
    angle_results.columns = ["Link_Cnt", "Min_Link_Angle", "Max_Link_Angle", "Mean_Link_Angle", "Parallel_Present"]
    angle_results = angle_results.reset_index()
    # # Create Corridor IDs
    # Pick a seed line and assemble all parallel connecting lines into a set of unique ids for each
    # "corridor set". The threshold determines whether an item is parallel or not.
    unique_fids = near_df_w_angle["IN_FID"].unique()
    corridor_ids = {}
    unvisited_fids = []
    visited_fids = set()
    counter = 0
    current_corridor_id = 1
    ll.arc_print("Using relationship table to construct corridors...")
    for fid in unique_fids:
        if fid in visited_fids:
            continue
        current_set = corridor_ids.setdefault(current_corridor_id, set([fid]))
        fid_df = near_df_w_angle[near_df_w_angle["IN_FID"] == fid]
        parallel_df = fid_df[fid_df["Parallel_Lines"] == 1]
        current_set.add(fid)
        visited_fids.add(fid)
        if parallel_df.size > 0:
            unvisited_fids.extend(parallel_df["NEAR_FID"].tolist())
            while unvisited_fids:
                visited_fid = unvisited_fids.pop()
                fid_df = near_df_w_angle[near_df_w_angle["IN_FID"] == visited_fid]
                parallel_df = fid_df[fid_df["Parallel_Lines"] == 1]
                visited_fids.add(visited_fid)
                current_set.add(visited_fid)
                more_ids_to_visit = [i for i in parallel_df["NEAR_FID"].tolist() if i not in visited_fids]
                unvisited_fids.extend(more_ids_to_visit)
            current_corridor_id += 1
        else:
            pass
        counter += 1
    corridor_container = []
    for corridor_id in corridor_ids:
        unique_ids = list(corridor_ids[corridor_id])
        corridor_data = [(corridor_id, fid) for fid in unique_ids]
        corridor_container.extend(corridor_data)
    corridor_df = pd.DataFrame(corridor_container, columns=["Corridor_ID", "FID"])
    corridor_df = corridor_df.set_index("FID")
    angle_results = angle_results.merge(corridor_df, how="left", left_on="IN_FID", right_index=True)
    angle_rec = angle_results.to_records()
    ll.arc_print("Joining Bearing & Corridor Fields...")
    arcpy.da.ExtendTable(output_network, oid, angle_rec, "IN_FID", False)
    ll.arc_print("Script Complete...")


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    # Define Inputs
    FeatureClass = arcpy.GetParameterAsText(0)
    OutFeatureClass = arcpy.GetParameterAsText(1)
    ConnectedRange = arcpy.GetParameterAsText(2)
    ParallelThreshold = int(arcpy.GetParameterAsText(3))
    NearTable = None
    assemble_corridors_from_network(FeatureClass, OutFeatureClass, ConnectedRange, ParallelThreshold, NearTable)
