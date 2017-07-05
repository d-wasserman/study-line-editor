This repository holds a collection of easy to use ArcGIS Geoprocessing scripts  (10.3+ and Pro) intended for batch line editing. The tools are described below. 

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