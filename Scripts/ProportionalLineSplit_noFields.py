# Name: ProportionalLineSplit_noFields.py
# Purpose: Take a feature class and proportionally split each unique feature line into equal length segments. Similar
# to editing tools done manually.This version of the tool will not keep the original fields of the old feature class.
# Author: David Wasserman
# Last Modified: 12/23/2015
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
import os, arcpy

# Define Inputs
FeatureClass = arcpy.GetParameterAsText(0)
Desired_Feature_Count = arcpy.GetParameter(1)
OutFeatureClass = arcpy.GetParameterAsText(2)


# Function Definitions

def arcPrint(string, progressor_Bool=False):
    try:
        if progressor_Bool:
            arcpy.SetProgressorLabel(string)
            arcpy.AddMessage(string)
            print(string)
        else:
            arcpy.AddMessage(string)
            print(string)
    except arcpy.ExecuteError:
        arcpy.GetMessages(2)
        pass
    except:
        arcpy.AddMessage("Could not create message, bad arguments.")
        pass


def do_analysis(in_fc, out_count, Out_FC):
    """TODO: Add documentation about this function here"""
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(in_fc)[0]
        FileName = os.path.split(in_fc)[1]
        fields = ["SHAPE@" if f.type == "Geometry" else f.name for f in arcpy.ListFields(in_fc)]
        cursor = arcpy.da.SearchCursor(in_fc, fields)
        desc = arcpy.Describe(in_fc)
        spatialRef = desc.spatialReference
        arcPrint("Established cursor for " + str(FileName) + ".", True)
        lineCounter = 0
        allSegmentsList = []
        for singleline in cursor:
            try:
                segmentList = []
                lineCounter += 1
                linegeo = singleline[fields.index("SHAPE@", )]
                for elinesegindex in range(0, out_count):
                    try:
                        seg = linegeo.segmentAlongLine((elinesegindex / float(out_count)),
                                                       ((elinesegindex + 1) / float(out_count)), True)
                        segID = elinesegindex + 1
                        segmentList.append(seg)
                    except:
                        arcPrint("Could not iterate through line segment " + str(segID) + ".")
                        break
                if len(segmentList) == out_count:
                    allSegmentsList.extend(segmentList)
                pass
                arcPrint("Iterated through feature " + str(lineCounter) + ".", True)
            except:
                arcPrint("Failed to Iterate through feature " + str(lineCounter) + ".", True)
        try:
            arcpy.CopyFeatures_management(allSegmentsList, Out_FC)
            arcPrint("Copied features to output location.")
        except:
            arcPrint("Could not copy features.")
        try:
            LineFName = "Line_Number"
            SegFName = "Seg_Number"
            arcpy.AddField_management(Out_FC, LineFName, "LONG", field_alias="Est. Orig Line Number")
            arcpy.AddField_management(Out_FC, SegFName, "LONG", field_alias="Est. Seg ID")
            arcpy.CalculateField_management(Out_FC, LineFName, "((!OBJECTID!-1)/" + str(out_count) + ")+1",
                                            "PYTHON_9.3")
            segCodeBlock = """def SegNumCalc(ObID,Num):
              if ObID%Num==0:
                return Num
              else:
                return ObID%Num"""

            arcpy.CalculateField_management(Out_FC, SegFName, "SegNumCalc(!OBJECTID!," + str(out_count) + ")",
                                            "PYTHON_9.3", segCodeBlock)
            arcPrint("Succeeded in adding estimated ID Fields.", True)
        except:
            arcPrint("Could not add and calculate estimated ID Fields")
            pass

        del cursor
        print ("Script Completed Successfully.")

    except arcpy.ExecuteError:
        arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]


# End do_analysis function


# Main Script
do_analysis(FeatureClass, Desired_Feature_Count, OutFeatureClass)
