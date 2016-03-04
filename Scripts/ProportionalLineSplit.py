# Name: ProportionalLineSplit.py
# Purpose: Take a feature class and proportionally split each unique feature line into equal length segments. Similar
# to editing tools done manually.This version of the tool will join the original fields of the old feature class.
# Author: David Wasserman
# Last Modified: 2/13/2016
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
from functools import wraps
# Define Inputs
FeatureClass = arcpy.GetParameterAsText(0)
Desired_Feature_Count = arcpy.GetParameter(1)
Feature_Count_Field = arcpy.GetParameterAsText(2)
OutFeatureClass = arcpy.GetParameterAsText(3)


# Function Definitions
def funcReport(function=None,reportBool=False):
    """This decorator function is designed to be used as a wrapper with other functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""
    def funcReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if reportBool:
                    print("Function:{0}".format(str(function.__name__)))
                    print("     Input(s):{0}".format(str(args)))
                    print("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                print("{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])
        return funcWrapper
    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return funcReport_Decorator(function)
        return waiting_for_function
    else:
        return funcReport_Decorator(function)


def arcToolReport(function=None, arcToolMessageBool=False, arcProgressorBool=False):
    """This decorator function is designed to be used as a wrapper with other GIS functions to enable basic try and except
     reporting (if function fails it will report the name of the function that failed and its arguments. If a report
      boolean is true the function will report inputs and outputs of a function.-David Wasserman"""
    def arcToolReport_Decorator(function):
        def funcWrapper(*args, **kwargs):
            try:
                funcResult = function(*args, **kwargs)
                if arcToolMessageBool:
                    arcpy.AddMessage("Function:{0}".format(str(function.__name__)))
                    arcpy.AddMessage("     Input(s):{0}".format(str(args)))
                    arcpy.AddMessage("     Ouput(s):{0}".format(str(funcResult)))
                if arcProgressorBool:
                    arcpy.SetProgressorLabel("Function:{0}".format(str(function.__name__)))
                    arcpy.SetProgressorLabel("     Input(s):{0}".format(str(args)))
                    arcpy.SetProgressorLabel("     Ouput(s):{0}".format(str(funcResult)))
                return funcResult
            except Exception as e:
                arcpy.AddMessage(
                    "{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print("{0} - function failed -|- Function arguments were:{1}.".format(str(function.__name__), str(args)))
                print(e.args[0])
        return funcWrapper
    if not function:  # User passed in a bool argument
        def waiting_for_function(function):
            return  arcToolReport_Decorator(function)
        return waiting_for_function
    else:
        return arcToolReport_Decorator(function)

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

def copyAlteredRow(row, fieldList, replacementDict):
    try:
        newRow = []
        keyList = replacementDict.keys()
        for field in fieldList:
            try:
                if field in keyList:
                    newRow.append(replacementDict[field])
                else:
                    newRow.append(row[getFIndex(fieldList, field)])
            except:
                arcPrint("Could not replace field {0} with its accepted value. Check field names for match.".format(
                        str(field)), True)
                newRow.append(None)  # Append a null value where it cannot find a value to the list.
        return newRow
    except:
        arcPrint("Could not get row fields for the following input {0}, returned an empty list.".format(str(row)),
                 True)
        arcpy.AddWarning(
                "Could not get row fields for the following input {0}, returned an empty list.".format(str(row)))
        newRow = []
        return newRow

@arcToolReport
def lineLength(row, Field, constantLen, fNames):
    # returns the appropriate value type  based on the options selected: retrieved form field or uses a constant
    if Field and Field != "#":
        arcPrint("Using size field to create output geometries.", True)
        return abs(row[getFIndex(fNames, Field)])
    else:
        arcPrint("Using size input value to create same sized output geometries.", True)
        return abs(constantLen)


def getFields(featureClass, excludedTolkens=["OID", "Geometry"], excludedFields=["shape_area", "shape_length"]):
    try:
        fcName = os.path.split(featureClass)[1]
        field_list = [f.name for f in arcpy.ListFields(featureClass) if f.type not in excludedTolkens
                      and f.name.lower() not in excludedFields]
        arcPrint("The field list for {0} is:{1}".format(str(fcName), str(field_list)), True)
        return field_list
    except:
        arcPrint(
                "Could not get fields for the following input {0}, returned an empty list.".format(
                        str(featureClass)),
                True)
        arcpy.AddWarning(
                "Could not get fields for the following input {0}, returned an empty list.".format(
                        str(featureClass)))
        field_list = []
        return field_list


def getFIndex(field_names, field_name):
    try:  # Assumes string will match if all the field names are made lower case.
        return [str(i).lower() for i in field_names].index(str(field_name).lower())
    # Make iter items lower case to get right time field index.
    except:
        print("Couldn't retrieve index for {0}, check arguments.".format(str(field_name)))
        return None


def do_analysis(in_fc, out_count_value, out_count_field, Out_FC):
    # This function will split each feature in a feature class into a desired number of equal length segments
    # based on an out count value or field.
    try:
        arcpy.env.overwriteOutput = True
        OutWorkspace = os.path.split(Out_FC)[0]
        FileName = os.path.split(Out_FC)[1]
        arcpy.CreateFeatureclass_management(OutWorkspace, FileName, "POLYLINE", in_fc, spatial_reference=in_fc)
        preFields = getFields(in_fc)
        fields = ["SHAPE@"] + preFields
        cursor = arcpy.da.SearchCursor(in_fc, fields)
        with arcpy.da.InsertCursor(Out_FC, fields) as insertCursor:
            arcPrint("Established insert cursor for " + str(FileName) + ".", True)
            lineCounter = 0
            for singleline in cursor:
                try:
                    segmentList = []
                    lineCounter += 1
                    linegeo = singleline[getFIndex(fields, "SHAPE@")]
                    # Incoming num is rounded, a minimum of 1 is chosen, and then it is inted to prep for range/seg
                    out_count = int(
                            round(max([1, lineLength(singleline, out_count_field, out_count_value, fields)])))
                    arcPrint(
                            "On feature iteration {0}, the desired number of segments is {1}.".format(
                                    str(lineCounter),
                                    str(out_count)),
                            True)
                    for elinesegindex in range(0, out_count):
                        try:
                            seg = linegeo.segmentAlongLine((elinesegindex / float(out_count)),
                                                           ((elinesegindex + 1) / float(out_count)), True)
                            segID = elinesegindex + 1
                            segmentedRow = copyAlteredRow(singleline, fields, {"SHAPE@": seg})
                            segmentList.append(segmentedRow)
                        except:
                            arcPrint("Could not iterate through line segment " + str(segID) + ".")
                            break
                    if len(segmentList) == out_count:  # Unload by feature so partial segments are not made.
                        for row in segmentList:
                            insertCursor.insertRow(row)
                    pass
                    arcPrint("Iterated through and split feature " + str(lineCounter) + ".", True)
                except:
                    arcPrint("Failed to iterate through feature " + str(lineCounter) + ".", True)
            del cursor, insertCursor, fields, preFields, OutWorkspace, lineCounter
            arcPrint("Script Completed Successfully.", True)

    except arcpy.ExecuteError:
        arcpy.GetMessages(2)
    except Exception as e:
        print e.args[0]

    # End do_analysis function

# This test allows the script to be used from the operating
# system command prompt (stand-alone), in a Python IDE,
# as a geoprocessing script tool, or as a module imported in
# another script
if __name__ == '__main__':
    do_analysis(FeatureClass, Desired_Feature_Count, Feature_Count_Field, OutFeatureClass)
