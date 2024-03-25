# Toolbox Summary
This repository holds a collection of easy to use ArcGIS Geoprocessing scripts (10.3+ and Pro) intended to provide automated line editing routines to help create useful study geometries. The tools are described below. 

* Feature Line Split - create a new feature class that has input lines split into an arbitrary number of segments. 

* Feature Line Pull - create a new feature class that has input lines split pulled back a target length. 

* Feature Line Whiskers - create a new feature class that perpendicular lines generated based on the sampled headings of the input polylines. 

* Feature Line Corridor Assembly - will add corridor ids to an output line network for all lines that are parallel within a tolerance and spatially connected/contiguous. 

* Feature Line Roll - Will extend a polyline based on the sampling of the line near its end points. 

* Feature Line Relative Angle - Will find relative angles to tag reference networks as parallel to target corridors. 

* Feature Line Gap Closure - Will find end points of lines with gaps between them and create new lines to close them.

# Citations 

If you use the tool in academic research or as part of professional reports, please cite the tool as the following:

Wasserman, D. Study Line Editor. (2019) GitHub repository, GitHub https://github.com/d-wasserman/study-line-editor. 

It is polite to cite. 

In depth descriptions, are provided below. 

# Feature Line Split

<b>Summary</b>
 
This scripting tool will take an input feature line, and split its line features into the number of target segments or target distance specified by the target specified by the input integer or input field. Each line feature will be split into the number of segments specified. This version of the script will carry over any of the fields of the original feature class using cursors, it will only split the geometry into equal length segments for a number of segments for each line equal to the target count. 

<b>Usage</b>
 
The goal of this script was to split target line features into (such as routes or paths) for all the line features in a feature layer, into segments of a target length or split equally into a target segment count similar to many of the proportional editing tools. The intended uses for this are: 

* Aid in the creation of study segments to summarize data on for linear networks. 

* Aid in the creation of animations for routes by allowing the creation equal length converging line segments whose ends can be converted to points. 

* Provide a tool for batch editing and segmentation of polylines. 

Works in ArcGIS Pro (2to3 compatible)

<b>Parameters</b>

<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the input feature class whose individual geometry features will be broken into the number of desired target segments and put into a new feature class. The input can only be a polyline for this tool, because it uses Polyline specific methods. </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This tool depends on the segmentAlongLine method in ArcGIS 10.3.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Segmentation_Number</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is either the target number of segments for the output lines or the target length in the units of the current projection of the segments for the output lines depending on the split method. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Segmentation_Field (Optional) </td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is a field that denotes the target number of segments for the output lines or the target length in the units of the current projection of the segments for the output lines depending on the split method. If a field is chosen it will override the segmentation number parameter. </SPAN></P><P><SPAN /></P></DIV></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Field</td>
</tr>
<tr>
<td class="info">Split_Method</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This parameter denotes how the input lines will be split. Length will use the current projection's linear units and the chosen segmentation field or value to split the input lines into segments of the chosen length (or close to the chosen length if Best Fit is True). Segment Count will break the lines into segments of equal length based on the segment count. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">String</td>
</tr>
<tr>
<td class="info">Best_Fit_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>If True and Length is the split method, the lines will be split into segments of length closest to the target determined by the value or field while not creating short end segments. It will result in lines closest to the target length but maintain lines of equal length in the output. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Boolean</td>
</tr>
 <tr>
<td class="info">Overlap Percentage</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>A target percentage to overlap split lines by. If set to 50% for example, lines split will overlap by 50% of their length across other split lines. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Boolean</td>
</tr>
<tr>
<td class="info">Output_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the output polyline feature class that will be created by this tool. It should have the fields of the original feature class derived by an insert cursor. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Uses insert cursors to get the desired "copy" of the segmented feature class. </SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Feature Class</td>
</tr>
</tbody>
</table>

# Feature Line Pull

<b>Summary</b>
 
This scripting tool will take an input feature line, and remove a target amount of length from the ends of the lines (pulling them back).  Each line feature will be copied once. This version of the script will carry over any of the fields of the original feature class using cursors, it will only return pulled back geometries in the new feature class. 

<b>Usage</b>
 
The goal of this script was to split target line features into (such as routes or paths) for all the line features in a feature layer, into segments that are pulled back a target amount. The intended uses for this are:

* Aid in the creation of study segments to summarize data on for networks.

* Allow proximity analysis for point features that do not include intersections/target nodes.

* Provide a tool for batch editing and segmentation of polylines. 

Works in ArcGIS Pro (2to3 compatible)

<b>Parameters</b>

<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the input feature class whose individual geometry features will be pulled back and put into a new feature class. The input can only be a polyline for this tool, because it uses Polyline specific methods. </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This tool depends on the segmentAlongLine method in ArcGIS 10.3.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Pull_Amount</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The distance in units of the current projection, that you wish your line features to be pulled back.</SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Pull_Field (Optional) </td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>A Field using a distance in units of the current projection, that specifies the amount you wish your line features to be pulled back. </SPAN></P><P><SPAN /></P></DIV></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Field</td>
</tr>
<tr>
<td class="info">Start_Point_Pull</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Determines whether the line has a distance starting at the line start point is pulled back. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">String</td>
</tr>
<tr>
<td class="info">End_Point_Pull</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Determines whether the line has a distance ending at the line end point is pulled back. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Boolean</td>
</tr>
<tr>
<td class="info">Output_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the output polyline feature class that will be created by this tool. It should have the fields of the original feature class derived by an insert cursor. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Uses insert cursors to get the desired "copy" of the segmented feature class. </SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Feature Class</td>
</tr>
</tbody>
</table>

# Feature Line Whiskers

<b>Summary</b>

This scripting tool is intended to assist with tasks related to createing intelligence related to  right of way widths from vector polygons such as building footprints (distance to frontage), road bed polygons, or sidewalk trace polygons found by remote sensing/computer vision/deep learning techniques. This tools main purpose is to create whiskers that are perpendicular to the line being used to create them. Once these whiskers are made, they can be trimmed by arbitrary polygons (feature to line), and then used to determine the widths of various features. This is a tool that is intended to generalize to many transportation/urban planning workflows.

<b>Usage</b>
 
The goal of this script was to create whiskers (like cat whiskers), that can be used to create lines that are perpendicular to an input sample line. The intended uses for this are:

* Aid in determining right of way widths from roadbed polygons/sidewalk polygons. 

* Determine the distance of a road from features perpendicular to their centroids. 

Works in ArcGIS Pro (2to3 compatible)

<b>Parameters</b>

<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the input feature class whose individual geometry features will be pulled back and put into a new feature class. The input can only be a polyline for this tool, because it uses Polyline specific methods. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This tool depends on the segmentAlongLine method in ArcGIS 10.3.</SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Whisker_Width</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the target width of the whisker that will be generated from the input polyline. If a field is chosen, this attribute is ignored. </SPAN></P></DIV></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Whisker_Field (Optional) </td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Allows you to choose a field that determines the width of the whisker generated on the target polylines. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Field</td>
</tr>
<tr>
<td class="info">Sample_Length</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is likely the most complex attribute to explain. If this is not set, or is zero, the heading from the line is determined by by the start and end points of the line. This attribute allows you to create a  new line that is near the center of the line that has a much smaller size. The sample line will not be seen, but this attribute determines the length sampled from the center of the line to determine heading. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Double</td>
</tr>
<tr>
<td class="info">Output_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This is the output polyline feature class that will be created by this tool. It should have the fields of the original feature class derived by an insert cursor. </SPAN></P></DIV></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>Whiskers should be perpendicular to the input line.</SPAN></P></DIV></DIV></DIV></td>
<td class="info" align="left">Feature Class</td>
</tr>
</tbody>
</table>

# Feature Line Corridor Assembly

<b>Summary</b>
 
This tool will construct a near table to construct a relationship table between lines. It will using the bearing of lines and their corresponding relationships to generate corridor ids consisting of all parallel line features within the threshold that are connected to each other. 

<b>Usage</b>
 
This tool will construct a near table to construct a relationship table between lines. It will using the bearing of lines and their corresponding relationships to generate corridor ids consisting of all parallel line features within the threshold that are connected to each other. The intended uses for this are: 

* Aid in the creation of study segments to summarize data on for linear networks. 

* Provide a tool to generate corridors for study and data summarization that does not depend on arbitrary street names or functional class attributes. 

* Provide a tool for batch editing and segmentation of polylines.

Works in ArcGIS Pro (2to3 compatible). This tool requires the pandas library to work. 

<b>Parameters</b>

<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the input feature class whose individual geometry will be used to assemble corridors from parallel connected lines. 
 </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This tool depends on the pandas Python Library.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Output_Feature_Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This output line feature class of the tool is a copy of the input network with line statistics and corridor attributes added. The fields added include: "Azimuth", "Link_Cnt", "Min_Link_Angle", "Max_Link_Angle", "Mean_Link_Angle", "Parallel_Present", "Corridor_ID"
</SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">Connected_Range</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>This represents the distance between connected line segments. If lines are directly connected this should be a very small number. 
 </SPAN></P><P><SPAN /></P></DIV></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Field</td>
</tr>
<tr>
<td class="info">Parallel_Threshold</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The threshold of angles in degrees between parallel lines and non-parallel lines. </SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">String</td>
</tr>
<tr>
</tbody>
</table>


# Feature Line Roll

<b>Summary</b>
                                                         
This tool will take an input feature line and extend its end points based on the angle implied by a sample of its start and end points. This enables the output line features to maintain the original attributes, but be extended in both directions to enable rolling linear statistics. 

<b>Usage</b>
 
The goal of this script  is to enable linear rolling windows through the extensions of segments in a line feature class. The intended uses for this are: 

* Aid in the creation of rolling window segments for linear rolling stats.

* Allow proximity analysis for point features that blend intersections. 

* Provide a tool to assist with Vision Zero and related safety analysis. 

Works in ArcGIS Pro. This tool requires the pandas library to work. 

<b>Parameters</b>

<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input Feature Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The input feature class whose extends will be extended based on some determined distance in the current projection.
 </SPAN></P></DIV></DIV><div class="noContent" style="text-align:center; margin-top: -1em">___________________</div><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This tool depends on the pandas Python Library.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Extension Distance</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The extension distance in the units of the current projection to extend the line.
</SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Long</td>
</tr>
<tr>
<td class="info">End Sampling Percentage</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><DIV><P><SPAN>The percentage of the ends of the polyline to use for bearing calculations informing the extension. Expressed as a ratio. 
 </SPAN></P><P><SPAN /></P></DIV></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">Float</td>
</tr>
<tr>
<td class="info">Output Feature Line</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>This is the output polyline feature class that will be created by this tool with extended lines. It should have the fields of the original feature class derived by an insert cursor. 
</SPAN></P></DIV></DIV><p><span class="noContent">There is no python reference for this parameter.</span></p></td>
<td class="info" align="left">String</td>
</tr>
<tr>
</tbody>
</table>

# Feature Line Relative Angle

<b>Summary</b>

This tool analyzes two sets of line geometries to identify the smallest relative angle between each line in the target feature class and all lines in the reference feature class. Optionally, it applies an angle threshold to highlight lines that are nearly parallel to the target lines. The results, including the relative angles and parallel status, are output to a new feature class.

<b>Usage</b>

The primary purpose of this script is to facilitate the analysis of linear geometries by comparing their orientations. This can be particularly useful in:

* Determining the alignment of roads or paths in relation to a given target corridor, aiding in urban planning and design.
* Identifying parallel infrastructures within a specified radius, which can be crucial for spatial analysis and decision-making processes.

<b>Parameters</b>

<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Target_Lines_FC</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The input feature class containing the target line geometries for comparison.</SPAN></P></DIV></DIV><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Specifies the target lines for angle comparison.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Reference_Lines_FC</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The input feature class containing reference line geometries for comparison against target lines.</SPAN></P></DIV></DIV><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Defines the reference lines for determining relative angles.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Layer</td>
</tr>
<tr>
<td class="info">Search_Radius</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The radius within which to search for reference lines relative to each target line.</SPAN></P></DIV></DIV><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Limit of search area for finding relevant reference lines.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Linear Unit</td>
</tr>
<tr>
<td class="info">Angle_Threshold</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>An optional threshold for identifying lines nearly parallel to target lines.</SPAN></P></DIV></DIV><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Determines the criteria for parallelism between target and reference lines.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Float</td>
</tr>
<tr>
<td class="info">Use_Nearest_Point</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The reference lines use the Near (Analysis) tools to identify the closest lines to the target.
                            By default, this uses the spatial relationship of the reference lines centroids to the target line. This is effectively 
                            looking at the nearest spatial relationship relative to the centroid of the reference corridor. </SPAN></P></DIV></DIV><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Conversion to centroid has overhead in the form of OID tracking.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Float</td>
</tr>
<tr>
<td class="info">Output_Feature_Line_FC</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>The feature class to output reference lines with relative angles and parallel status to target lines.</SPAN></P></DIV></DIV><br />
<span style="font-weight: bold">Python Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P><SPAN>Hosts the results of the analysis, including angles and parallelism indicators.</SPAN></P></DIV></DIV></td>
<td class="info" align="left">Feature Class</td>
</tr>
</tbody>
</table>


# Feature Line Gap Closure

<b>Summary</b>

This script is designed to enhance network connectivity by identifying and filling gaps between line feature end points within a specified search radius. By analyzing spatial relationships, it creates new lines in an output feature class, thereby improving integration within the network. This process ensures that spatial data representations are more accurate and connected, facilitating better analysis and decision-making in various applications such as urban planning, transportation networks, and utility management.

<b>Usage</b>

The primary function of this tool is to detect and close gaps between line features, which might otherwise disrupt network connectivity. It achieves this by:

* Identifying line feature end points that are within a specified search radius but not directly connected or part of the same line.
* Generating new line features that bridge these gaps, based on the proximity of the end points.
* Adding the FIDs (Feature IDs) of the connected line end points as start and end attributes in the output feature class.
* Including a field for the near distance, which quantifies the gap between the end points.

This tool is invaluable for creating a feature class of lines that effectively closes gaps, enhancing the integrity and usability of spatial datasets.

<b>Parameters</b>

<table width="100%" border="0" cellpadding="5">
<tbody>
<tr>
<th width="30%">
<b>Parameter</b>
</th>
<th width="50%">
<b>Explanation</b>
</th>
<th width="20%">
<b>Data Type</b>
</th>
</tr>
<tr>
<td class="info">Input_Feature_Class</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P>The input line features to analyze for identifying potential gap closures. This parameter is crucial for determining where new connecting lines can be introduced.</P></DIV></DIV></td>
<td class="info" align="left">Feature Class</td>
</tr>
<tr>
<tr>
<td class="info">Transfer_Fields</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P>The fields to transfer as A-B fields to the output feature class from the linear input.</P></DIV></DIV></td>
<td class="info" align="left">Feature Class</td>
</tr>
<tr>
<td class="info">Output_Feature_Class</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P>The output feature class where new lines, designed to fill identified gaps, will be stored. This feature class becomes a comprehensive dataset representing both original and newly created line features.</P></DIV></DIV></td>
<td class="info" align="left">Feature Class</td>
</tr>
<tr>
<td class="info">Search_Radius</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P>The search radius within which to identify the closest end points for gap filling. This parameter defines the scope of the tool's analysis for potential connections.</P></DIV></DIV></td>
<td class="info" align="left">Linear Unit</td>
</tr>
<tr>
<td class="info">Connection_Count</td>
<td class="info" align="left">
<span style="font-weight: bold">Dialog Reference</span><br /><DIV STYLE="text-align:Left;"><DIV><P>The number of connections to create between end points in order of proximity. This parameter helps prioritize which gaps to close first, based on spatial relationships.</P></DIV></DIV></td>
<td class="info" align="left">Long</td>
</tr>
</tbody>
</table>
