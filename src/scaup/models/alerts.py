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

ALERT_BODY = Template("""
<p>Dear $local_contact,</p>

<p>The user(s) have submitted important information regarding the grids and pre-session data collection parameters for session $proposal-$session in SCAUP.</p>

<p>To view this information, please <a href="$frontend_url/proposals/$proposal/sessions/$session">go to the Session Samples Dashboard page for the session</a>, select a shipment, and select “Print contents as table” under the Actions section</p>

<p>Before starting an EPU session, please ensure that grids are added to the Cassette positions in the Sample Collection Summary page. This step allows results from the auto-processing pipeline in PATo to be correctly linked to sample conditions in SCAUP.</p>

<p>Note: If you are not the designated Local Contact for this session, kindly forward this email to the appropriate person.</p>

<p>Many thanks,</p>
<p>SCAUP team</p>
""")
