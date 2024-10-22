# Name: FeatureLineRelativeAngle.py
# Purpose: This tool will take in target line file and a reference line file and find the smallest relative angle between all reference lines and the target lines.
# This tool has an optional threshold that can be set to identify all facilities that are parallel (within the threshold) to the target corridors.
# of the old feature class.
# Author: David Wasserman
# Last Modified: 2/19/2024
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
# Import Modules
import math
import os

import arcpy
import numpy as np
import pandas as pd

import linelibrary as fll

# Function Definitions


def feature_line_relative_angle(
    target_lines_fc,
    reference_lines_fc,
    search_radius,
    angle_threshold,
    use_nearest_point=True,
    output_feature_line_fc="in_memory/parallel_facility",
):
    """
    Analyzes two sets of line geometries to find the smallest relative angle between each line in the target
    feature class and all lines in the reference feature class. Optionally, it can apply an angle threshold to
    identify lines that are parallel (within the threshold) to the target lines. The results are output to a
    new feature class.

    Parameters:
    ---------------------
    target_lines_fc (FeatureClass): The input feature class containing the target line geometries for comparison to reference lines.
    reference_lines_fc (FeatureClass): The input feature class containing the reference line geometries to compare against the target lines.
        This is the output feature class with new attributes added including the releative angle to the target, and whether it is parallel.
    search_radius (LinearUnit): The search radius within which the tool will look for reference lines relative to each target line.
    angle_threshold (float): An optional angle threshold (in degrees) to identify lines that are nearly parallel to the target lines.
                             Lines within this threshold angle from the target lines are tagged with a 1 in a Parallel_Target field.
    use_nearest_point (bool): The reference lines use the Near (Analysis) tools to identify the closest lines to the target.
                            By default, this uses the spatial relationship of the reference lines centroids to the target line. This is effectively
                            looking at the nearest spatial relationship relative to the centroid of the reference corridor.

    output_feature_line_fc (FeatureClass): The output feature class of reference lines with relative angles to the target and those
                            deemed parallel to the target. This feature class will include the attributes from the reference_lines_fc,
                            along with the computed smallest relative angle to the reference lines.
    """
    try:
        arcpy.env.overwriteOutput = True
        workspace = r"in_memory"
        bearing_field = "RefAzimuth"
        corr_bearing_field = "TarAzimuth"
        near_fid, near_dist, ftp_oid = "NEAR_FID", "NEAR_DIST", "ORIG_FID"
        temp_points = os.path.join(workspace, "Relative_Angle_Points")
        fll.arc_print("Copying feature classes..")
        arcpy.management.CopyFeatures(reference_lines_fc, output_feature_line_fc)
        fll.arc_print("Output file copied...", True)
        desc = arcpy.Describe(output_feature_line_fc)
        arcpy.AddField_management(output_feature_line_fc, bearing_field, "DOUBLE")
        reference_bearing_dict = fll.calculate_line_bearing(
            output_feature_line_fc, bearing_field, True
        )
        arcpy.AddField_management(target_lines_fc, corr_bearing_field, "DOUBLE")
        target_bearing_dict = fll.calculate_line_bearing(
            target_lines_fc, corr_bearing_field, True
        )
        if use_nearest_point:
            proximity_features = temp_points
            if fll.field_exist(output_feature_line_fc, ftp_oid):
                fll.arc_print("Deleting ORIG_FID field in reference line copy...")
                arcpy.DeleteField_management(output_feature_line_fc, [ftp_oid])
            fll.arc_print("Converting output lines to points for Near Analysis...")
            arcpy.FeatureToPoint_management(
                output_feature_line_fc, temp_points, "INSIDE"
            )
        else:
            fll.arc_print(
                "Considering nearest relationships based on original lines..."
            )
            proximity_features = output_feature_line_fc
        arcpy.Near_analysis(
            proximity_features, target_lines_fc, search_radius=search_radius
        )
        fll.arc_print("Near Analysis complete...", True)
        reference_fields = fll.get_fields(proximity_features)
        reference_df = fll.arcgis_table_to_df(proximity_features, reference_fields)
        target_fields = fll.get_fields(target_lines_fc)
        target_df = fll.arcgis_table_to_df(target_lines_fc, target_fields)
        OIDFieldName = desc.OIDFieldName if not use_nearest_point else ftp_oid
        reference_df[OIDFieldName] = reference_df.index
        corridor_oid = arcpy.Describe(target_lines_fc).OIDFieldName
        reference_df = reference_df.merge(
            target_df,
            how="left",
            right_on=corridor_oid,
            left_on=near_fid,
            suffixes=("_Ref", "_Tar"),
        )
        fll.arc_print("Computing relative angles...")
        angle_diff, reference_azimumth, target_azimuth = (
            "Angle_Diff",
            bearing_field,
            corr_bearing_field,
        )
        angle1, angle2, relative_angle, parallel = (
            "Angle_1",
            "Angle_2",
            "Relative_Angle",
            "Parallel_Target",
        )
        reference_df[angle_diff] = (
            reference_df[reference_azimumth] - reference_df[target_azimuth]
        ) % 360
        reference_df[angle1] = reference_df[angle_diff].apply(
            fll.find_smallest_angle,
            args=(
                0,
                True,
            ),
        )
        reference_df[angle2] = reference_df[angle_diff].apply(
            fll.find_smallest_angle,
            args=(
                180,
                True,
            ),
        )
        reference_df[relative_angle] = reference_df[[angle1, angle2]].min(axis=1)
        reference_df[parallel] = np.where(
            reference_df[relative_angle] < angle_threshold, 1, 0
        )
        joined_fields = [OIDFieldName, angle1, angle2, relative_angle, parallel]
        if use_nearest_point:
            joined_fields.append(near_dist)
        reference_df = reference_df[joined_fields].copy()
        fll.arc_print("Exporing relative angle results as array.")
        finalStandardArray = reference_df.to_records()
        fll.arc_print("Joining new score fields to feature class.")
        OutOIDFieldName = desc.OIDFieldName
        arcpy.da.ExtendTable(
            output_feature_line_fc,
            OutOIDFieldName,
            finalStandardArray,
            OIDFieldName,
            append_only=False,
        )
        fll.arc_print("Join Complete")
        fll.arc_print("Script Completed Successfully.", True)
    except arcpy.ExecuteError:
        arcpy.AddError(str(arcpy.GetMessages(2)))
    except Exception as e:
        arcpy.AddError(str(e.args[0]))

        # End do_analysis function


# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == "__main__":
    # Define Inputs
    Target_Lines = arcpy.GetParameterAsText(0)
    Reference_Lines = arcpy.GetParameterAsText(1)
    Search_Radius = arcpy.GetParameter(2)
    Angle_Threshold = float(arcpy.GetParameter(3))
    Use_Nearest_Point = bool(arcpy.GetParameter(4))
    Output_Feature_Line = arcpy.GetParameterAsText(5)
    feature_line_relative_angle(
        Target_Lines,
        Reference_Lines,
        Search_Radius,
        Angle_Threshold,
        Use_Nearest_Point,
        Output_Feature_Line,
    )
