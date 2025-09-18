# ruff: noqa: E501

from string import Template

EMAIL_HEADER = """
<html>
<body>
    <div class="wrapper" style="padding: 0.5%; text-align:center; border-radius: 5px; border: 1px solid #efefef">
	<div class="header" style="background: #001d55; text-align: center; padding-top: 15px; padding-bottom: 15px; border-top-left-radius: 5px; border-top-right-radius: 5px;">
        <img src="cid:logo-light.png" height="45"/>
	</div>
	<div>
"""

EMAIL_FOOTER = """
    <p style="border-top: 1px solid #001d55; background-color: #1040A1; padding: 10px; color: white;">© 2025, Diamond Light Source</p></div>
"""

SAMPLE_COLLECTION_LINK = Template("""
<li><a href="$frontend_url/proposals/$proposal/sessions/$session/shipments/$shipment">$shipment_name</a></li>
""")

ALERT_BODY = Template("""
<p>Dear $local_contact,</p>

<p>The user(s) have submitted important information regarding the grids and pre-session data collection parameters for session $proposal-$session in SCAUP.</p>

<p>To view this information, either head to the <a href="$frontend_url/proposals/$proposal/sessions/$session">session samples dashboard</a>, select a sample collection and click “Print contents as table” under the Actions section, or view one of the session sample collections directly:</p>

<ul style="text-align: left;list-style: square;">
$sample_collection_links
</ul>

<p>Before starting an EPU session, please ensure that grids are added to the Cassette positions in the Sample Collection Summary page. This step allows results from the auto-processing pipeline in PATo to be correctly linked to sample conditions in SCAUP.</p>

<p>Note: If you are not the designated Local Contact for this session, kindly forward this email to the appropriate person.</p>

<p>Many thanks,</p>
<p>SCAUP team</p>
""")
