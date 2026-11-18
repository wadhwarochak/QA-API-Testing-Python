
import os
import html
import xml.etree.ElementTree as ET
from pathlib import Path

XML_FILE = Path("reports/junit.xml")
HTML_FILE = Path("reports/email_report.html")

pytest_outcome = os.getenv("PYTEST_OUTCOME", "unknown").upper()

repo = os.getenv("GITHUB_REPOSITORY", "N/A")
branch = os.getenv("GITHUB_REF_NAME", "N/A")
trigger = os.getenv("GITHUB_EVENT_NAME", "N/A")
run_id = os.getenv("GITHUB_RUN_ID", "")
server = os.getenv("GITHUB_SERVER_URL", "https://github.com")

test_rows = []
total = passed = failed = skipped = 0
duration = 0.0

if XML_FILE.exists():
    root = ET.parse(XML_FILE).getroot()

    for case in root.iter("testcase"):
        total += 1
        duration += float(case.get("time", 0))

        failure = case.find("failure")
        error = case.find("error")
        skip = case.find("skipped")

        if failure is not None:
            status = "FAILED"
            failed += 1
            details = failure.get("message", failure.text or "")
        elif error is not None:
            status = "ERROR"
            failed += 1
            details = error.get("message", error.text or "")
        elif skip is not None:
            status = "SKIPPED"
            skipped += 1
            details = skip.get("message", skip.text or "")
        else:
            status = "PASSED"
            passed += 1
            details = "Test completed successfully"

        test_name = (
            f"{case.get('classname', '')}."
            f"{case.get('name', '')}"
        ).strip(".")

        test_rows.append(
            f"""
            <tr>
                <td>{html.escape(test_name)}</td>
                <td><b>{status}</b></td>
                <td>{float(case.get('time', 0)):.2f}s</td>
                <td>{html.escape(str(details)[:500])}</td>
            </tr>
            """
        )

if failed:
    overall_status = "FAILED"
elif total == 0:
    overall_status = "REPORT NOT AVAILABLE"
elif skipped == total:
    overall_status = "SKIPPED"
else:
    overall_status = "PASSED"

if not test_rows:
    test_rows.append(
        """
        <tr>
            <td colspan="4">No test results available. Check workflow logs.</td>
        </tr>
        """
    )

run_url = f"{server}/{repo}/actions/runs/{run_id}"

report = f"""
<html>
<body style="font-family:Arial,sans-serif;color:#333;">

<h2>Python API Automation Report</h2>

<table border="1" cellpadding="8"
       cellspacing="0" width="100%"
       style="border-collapse:collapse;">

<tr><th>Execution Summary</th><th>Value</th></tr>
<tr><td>Overall Status</td><td><b>{overall_status}</b></td></tr>
<tr><td>Total Tests</td><td>{total}</td></tr>
<tr><td>Passed</td><td>{passed}</td></tr>
<tr><td>Failed / Errors</td><td>{failed}</td></tr>
<tr><td>Skipped</td><td>{skipped}</td></tr>
<tr><td>Duration</td><td>{duration:.2f} seconds</td></tr>

</table>

<br>

<h3>Individual Test Results</h3>

<table border="1" cellpadding="8"
       cellspacing="0" width="100%"
       style="border-collapse:collapse;">

<tr>
    <th>Test Case</th>
    <th>Status</th>
    <th>Duration</th>
    <th>Details</th>
</tr>

{''.join(test_rows)}

</table>

<br>

<h3>Execution Information</h3>

<table border="1" cellpadding="8"
       cellspacing="0" width="100%"
       style="border-collapse:collapse;">

<tr><td>Repository</td><td>{html.escape(repo)}</td></tr>
<tr><td>Branch</td><td>{html.escape(branch)}</td></tr>
<tr><td>Trigger</td><td>{html.escape(trigger)}</td></tr>
<tr><td>Python Version</td><td>3.12</td></tr>
<tr><td>Framework</td><td>Pytest</td></tr>

</table>

<br>

<p>
<a href="{html.escape(run_url)}">
View GitHub Actions Execution Logs
</a>
</p>

<p>Regards,<br>Pytest API Automation Framework</p>

</body>
</html>
"""

HTML_FILE.parent.mkdir(parents=True, exist_ok=True)
HTML_FILE.write_text(report, encoding="utf-8")

print(f"Email report generated: {HTML_FILE}")
