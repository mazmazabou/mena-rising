"""MENA Rising Pipeline — Newsletter Sender

Reads latest_brief.json, generates an HTML email summary,
and sends it as a Resend broadcast to the newsletter audience.
"""

import json
import logging
import sys
from html import escape

import resend

from config import OUTPUT_FILE, RESEND_API_KEY, RESEND_AUDIENCE_ID

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

SITE_URL = "https://mena-rising.com"
FROM_ADDRESS = "MENA Rising <brief@mena-rising.com>"


def load_brief() -> dict:
    """Load latest_brief.json from the public data directory."""
    if not OUTPUT_FILE.exists():
        log.error("latest_brief.json not found at %s", OUTPUT_FILE)
        sys.exit(1)
    return json.loads(OUTPUT_FILE.read_text(encoding="utf-8"))


def build_html(brief: dict) -> str:
    """Build a clean HTML email from brief data."""
    issue = brief.get("issue", {})
    issue_num = escape(str(issue.get("number", "?")))
    week_of = escape(str(issue.get("weekOf", "")))
    bottom_line = escape(brief.get("bottomLine", ""))

    # Macro highlights — pick top 6 metrics
    macro_rows = ""
    for m in brief.get("macroPulse", [])[:6]:
        country = escape(str(m.get("country", "")))
        metric = escape(str(m.get("metric", "")))
        value = m.get("value", "")
        unit = m.get("unit", "")
        change = m.get("change", 0)

        if unit == "$B":
            formatted = f"${value}B"
        elif unit in ("%", "% GDP"):
            formatted = f"{value}%"
        else:
            formatted = str(value)

        if change and change != 0:
            arrow = "&#9650;" if change > 0 else "&#9660;"
            color = "#22c55e" if change > 0 else "#ef4444"
            change_html = f' <span style="color:{color}">{arrow}{abs(change)}%</span>'
        else:
            change_html = ""

        macro_rows += f"""
        <tr>
          <td style="padding:6px 12px;border-bottom:1px solid #2a3a4a;color:#c8b88a;font-size:13px">{country}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #2a3a4a;color:#94a3b8;font-size:13px">{metric}</td>
          <td style="padding:6px 12px;border-bottom:1px solid #2a3a4a;color:#f1f5f9;font-family:monospace;font-size:13px">{formatted}{change_html}</td>
        </tr>"""

    # Risk highlights
    risk_items = ""
    for r in brief.get("risks", [])[:3]:
        level = escape(str(r.get("level", "MEDIUM")))
        title = escape(str(r.get("title", "")))
        desc = escape(str(r.get("description", "")))
        level_colors = {
            "LOW": "#22c55e",
            "MEDIUM": "#f59e0b",
            "HIGH": "#f97316",
            "CRITICAL": "#ef4444",
        }
        color = level_colors.get(level, "#f59e0b")
        risk_items += f"""
        <div style="margin-bottom:16px;padding:12px 16px;background:#0f1a2e;border-radius:6px;border-left:3px solid {color}">
          <span style="color:{color};font-size:11px;font-weight:700;letter-spacing:1px">{level}</span>
          <div style="color:#f1f5f9;font-size:15px;font-weight:600;margin-top:4px">{title}</div>
          <div style="color:#94a3b8;font-size:13px;margin-top:4px;line-height:1.5">{desc}</div>
        </div>"""

    return f"""\
<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#0a0f1a;font-family:Georgia,'Times New Roman',serif">
<div style="max-width:600px;margin:0 auto;background:#111827;border:1px solid #1e293b">

  <!-- Header -->
  <div style="padding:32px 24px;text-align:center;border-bottom:2px solid #c8b88a">
    <h1 style="margin:0;color:#c8b88a;font-size:28px;letter-spacing:4px;font-weight:700">MENA RISING</h1>
    <p style="margin:8px 0 0;color:#94a3b8;font-size:14px">Economic Intelligence for the Middle East &amp; North Africa</p>
    <p style="margin:8px 0 0;color:#c8b88a;font-size:12px;letter-spacing:2px;font-family:monospace">Issue #{issue_num} &middot; Week of {week_of}</p>
  </div>

  <!-- Bottom Line -->
  <div style="padding:24px;border-bottom:1px solid #1e293b">
    <p style="margin:0 0 8px;color:#c8b88a;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:600">This Week's Analysis</p>
    <p style="margin:0;color:#e2e8f0;font-size:15px;line-height:1.6;font-style:italic">{bottom_line}</p>
  </div>

  <!-- Macro Pulse -->
  <div style="padding:24px;border-bottom:1px solid #1e293b">
    <p style="margin:0 0 12px;color:#c8b88a;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:600">Macro Pulse</p>
    <table style="width:100%;border-collapse:collapse">
      {macro_rows}
    </table>
  </div>

  <!-- Risk Radar -->
  <div style="padding:24px;border-bottom:1px solid #1e293b">
    <p style="margin:0 0 12px;color:#c8b88a;font-size:11px;letter-spacing:3px;text-transform:uppercase;font-weight:600">Risk Radar</p>
    {risk_items}
  </div>

  <!-- CTA -->
  <div style="padding:32px 24px;text-align:center">
    <a href="{SITE_URL}" style="display:inline-block;background:#c8b88a;color:#0a0f1a;padding:12px 32px;border-radius:4px;text-decoration:none;font-size:14px;font-weight:700;letter-spacing:1px">Read the Full Brief</a>
  </div>

  <!-- Footer -->
  <div style="padding:16px 24px;text-align:center;border-top:1px solid #1e293b">
    <p style="margin:0;color:#64748b;font-size:11px">MENA Rising &middot; Weekly Economic Intelligence</p>
  </div>

</div>
</body>
</html>"""


def send_newsletter():
    """Load brief, build HTML, and broadcast via Resend."""
    if not RESEND_API_KEY:
        log.error("RESEND_API_KEY not set")
        sys.exit(1)
    if not RESEND_AUDIENCE_ID:
        log.error("RESEND_AUDIENCE_ID not set")
        sys.exit(1)

    resend.api_key = RESEND_API_KEY

    brief = load_brief()
    issue_num = brief.get("issue", {}).get("number", "?")
    week_of = brief.get("issue", {}).get("weekOf", "")
    html = build_html(brief)

    subject = f"MENA Rising #{issue_num} — Week of {week_of}"

    log.info("Sending newsletter: %s", subject)

    result = resend.Broadcasts.create({
        "audience_id": RESEND_AUDIENCE_ID,
        "from": FROM_ADDRESS,
        "subject": subject,
        "html": html,
    })

    broadcast_id = result.get("id") if isinstance(result, dict) else getattr(result, "id", None)
    log.info("Broadcast created: %s", broadcast_id)

    if broadcast_id:
        send_params: resend.Broadcasts.SendParams = {"broadcast_id": broadcast_id}
        send_result = resend.Broadcasts.send(send_params)
        log.info("Broadcast sent: %s", send_result)
    else:
        log.error("Failed to create broadcast: %s", result)
        sys.exit(1)

    log.info("Newsletter sent successfully")


if __name__ == "__main__":
    send_newsletter()
