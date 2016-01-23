Hi All,
 
I got inspired by tasks at work and a recent arcpy cafe post to develop a tiny scripting tool that takes an existing polyline feature layer and proportionally splits into  a desired number of segments of equal length. This scripting tool will enable you to do batch editing based on either an input field or just split all the lines into segments of equal length. This tool WILL attempt to copy the fields from the original feature class.
 
Summary
 
 
This scripting tool will take an input feature line, and split its line features into the number of target segments specified by the target specified by the input integer or input field. Each line feature will be split into the number of segments specified, each of equal length. This version of the script will carry over any of the fields of the original feature class using cursors, it will only split the geometry into equal length segments for a number of segments for each line equal to the target count. Keep in mind that this tool creates a new feature class using the input as  a template and then inserts the field values using insert cursors. They are not directly "copies" of the feature class.
 
 
Usage
 
 
The goal of this script was to split target line features into (such as routes or paths) for all the line features in a feature layer, into segments of equal length similar to many of the proportional editing tools. The intended uses for this are:
Aid in the creation of study segments to summarize data on for networks.
Aid in the creation of animations for routes by allowing the creation equal length converging line segments whose ends can be converted to points.
Provide a tool for batch editing and segmentation of polylines.
