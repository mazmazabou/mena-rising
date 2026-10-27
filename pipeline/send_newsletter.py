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


# Resend swaps this placeholder for each contact's one-click unsubscribe link.
UNSUBSCRIBE_URL = "{{{RESEND_UNSUBSCRIBE_URL}}}"

NAVY = "#0b1628"
PANEL = "#10303f"
GOLD = "#c9a84c"
IVORY = "#eadfcb"
SLATE = "#8b9aaf"
RULE = "#2b3f4c"
RISK_COLORS = {"LOW": "#3dcf8e", "MEDIUM": "#f0c04c", "HIGH": "#c75b2f", "CRITICAL": "#e06666"}
SERIF = "'Cormorant Garamond',Georgia,'Times New Roman',serif"
BODY = "'Crimson Pro',Georgia,'Times New Roman',serif"


def _format_metric(m: dict) -> str:
    value, unit = m.get("value", ""), m.get("unit", "")
    if unit == "$B":
        return f"${value}B"
    if unit in ("%", "% GDP"):
        return f"{value}%"
    return str(value)


def build_html(brief: dict, asset_base: str = SITE_URL) -> str:
    """Build the newsletter HTML from brief data.

    Table layout with inline styles so Outlook renders it. Motion comes from the
    masthead GIF (frame 1 is the finished static design, which is all Outlook
    shows) plus a CSS fade on the lead for clients that support it, behind
    prefers-reduced-motion.
    """
    issue = brief.get("issue", {})
    issue_num = escape(str(issue.get("number", "?")))
    week_of = escape(str(issue.get("weekOf", "")))
    bottom_line = escape(brief.get("bottomLine", ""))
    lead = escape(brief.get("headline", "")) or bottom_line.split(". ")[0]
    drop, rest = (bottom_line[:1], bottom_line[1:]) if bottom_line else ("", "")

    macro_rows = ""
    for m in brief.get("macroPulse", [])[:6]:
        change = m.get("change", 0) or 0
        change_html = ""
        if change:
            color = RISK_COLORS["LOW"] if change > 0 else RISK_COLORS["CRITICAL"]
            arrow = "&#9650;" if change > 0 else "&#9660;"
            change_html = f'<br><span style="color:{color};font-size:12px">{arrow} {abs(change)}%</span>'
        macro_rows += f"""
            <tr>
              <td style="padding:10px 0;border-bottom:1px solid {RULE};font-family:{BODY};font-size:16px;line-height:1.35;color:{IVORY}">
                {escape(str(m.get("country", "")))}<br><span style="color:{SLATE};font-size:14px">{escape(str(m.get("metric", "")))}</span>
              </td>
              <td align="right" style="padding:10px 0;border-bottom:1px solid {RULE};font-family:'JetBrains Mono',Menlo,Consolas,monospace;font-size:17px;color:{IVORY};white-space:nowrap">
                {escape(_format_metric(m))}{change_html}
              </td>
            </tr>"""

    risk_rows = ""
    for r in brief.get("risks", [])[:3]:
        level = str(r.get("level", "MEDIUM"))
        color = RISK_COLORS.get(level, RISK_COLORS["MEDIUM"])
        risk_rows += f"""
            <tr>
              <td style="padding:0 0 18px">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
                  <tr>
                    <td width="3" bgcolor="{color}" style="background:{color};font-size:0;line-height:0">&nbsp;</td>
                    <td bgcolor="{PANEL}" style="background:{PANEL};padding:14px 18px">
                      <p style="margin:0;font-family:{SERIF};font-style:italic;font-weight:600;font-size:15px;color:{color}">{escape(level.capitalize())} risk</p>
                      <p style="margin:4px 0 0;font-family:{SERIF};font-weight:600;font-size:20px;line-height:1.25;color:{IVORY}">{escape(str(r.get("title", "")))}</p>
                      <p style="margin:6px 0 0;font-family:{BODY};font-size:15px;line-height:1.55;color:{SLATE}">{escape(str(r.get("description", "")))}</p>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>"""

    section_head = (
        f'<p style="margin:0 0 6px;font-family:{SERIF};font-style:italic;font-size:24px;font-weight:500;color:{GOLD}">{{}}</p>'
        f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
        f'<td height="1" bgcolor="{GOLD}" style="background:{GOLD};font-size:0;line-height:0;opacity:.5">&nbsp;</td></tr></table>'
    )

    return f"""\
<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<meta name="supported-color-schemes" content="dark">
<title>MENA Rising No. {issue_num}</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&amp;family=Crimson+Pro:wght@400&amp;display=swap" rel="stylesheet">
<style>
  @media (prefers-reduced-motion: no-preference) {{
    .mr-lead {{ animation: mr-rise 1.1s cubic-bezier(.22,1,.36,1) .3s both; }}
    @keyframes mr-rise {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: none; }} }}
  }}
  @media (max-width: 620px) {{
    .mr-pad {{ padding-left: 20px !important; padding-right: 20px !important; }}
    .mr-lead {{ font-size: 30px !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background:{NAVY}" bgcolor="{NAVY}">
<div style="display:none;max-height:0;overflow:hidden">{lead}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{NAVY}" style="background:{NAVY}">
<tr><td align="center" style="padding:24px 8px">
  <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px">

    <!-- Dateline -->
    <tr><td class="mr-pad" style="padding:0 32px">
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
        <td style="font-family:{BODY};font-size:14px;color:{SLATE}">No. {issue_num}</td>
        <td align="right" style="font-family:{BODY};font-size:14px;color:{SLATE}">Week of {week_of}</td>
      </tr></table>
    </td></tr>

    <!-- Ornament band: animated GIF, frame 1 is the finished static design -->
    <tr><td style="padding:10px 0 0">
      <img src="{asset_base}/email/masthead.gif" width="600" height="80" alt="" style="display:block;width:100%;max-width:600px;height:auto;border:0">
    </td></tr>

    <!-- Nameplate -->
    <tr><td align="center" style="padding:6px 32px 4px">
      <h1 style="margin:0;font-family:{SERIF};font-weight:600;font-size:52px;line-height:1;color:{GOLD}">MENA Rising</h1>
      <p style="margin:10px 0 0;font-family:{BODY};font-style:italic;font-size:16px;color:{SLATE}">Economic intelligence for the Middle East &amp; North Africa</p>
    </td></tr>

    <!-- Lead -->
    <tr><td class="mr-pad" style="padding:28px 32px 8px;border-top:1px solid {RULE}">
      <h2 class="mr-lead" style="margin:0;font-family:{SERIF};font-weight:500;font-size:36px;line-height:1.1;color:{IVORY}">{lead}</h2>
    </td></tr>

    <!-- Bottom line, with a drop cap -->
    <tr><td class="mr-pad" style="padding:18px 32px 8px">
      <p style="margin:0;font-family:{BODY};font-size:18px;line-height:1.65;color:{IVORY}"><span style="float:left;font-family:{SERIF};font-weight:600;font-size:62px;line-height:52px;padding:4px 8px 0 0;color:{GOLD}">{drop}</span>{rest}</p>
    </td></tr>

    <!-- Macro pulse -->
    <tr><td class="mr-pad" style="padding:30px 32px 8px">
      {section_head.format("Macro pulse")}
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{macro_rows}
      </table>
    </td></tr>

    <!-- Risk radar -->
    <tr><td class="mr-pad" style="padding:30px 32px 0">
      {section_head.format("Risk radar")}
      <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:16px">{risk_rows}
      </table>
    </td></tr>

    <!-- CTA: bulletproof button -->
    <tr><td align="center" style="padding:16px 32px 36px">
      <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
        <td bgcolor="{GOLD}" style="background:{GOLD};border-radius:2px">
          <a href="{SITE_URL}" style="display:inline-block;padding:14px 34px;font-family:{SERIF};font-weight:600;font-size:18px;color:{NAVY};text-decoration:none">Read the full issue</a>
        </td>
      </tr></table>
    </td></tr>

    <!-- Footer -->
    <tr><td align="center" class="mr-pad" style="padding:20px 32px;border-top:1px solid {RULE}">
      <p style="margin:0;font-family:{BODY};font-size:13px;line-height:1.6;color:{SLATE}">
        You subscribed to MENA Rising at mena-rising.com. It arrives every Monday.<br>
        <a href="{SITE_URL}/archive" style="color:{GOLD}">Past issues</a> &nbsp;&nbsp; <a href="{UNSUBSCRIBE_URL}" style="color:{GOLD}">Unsubscribe</a>
      </p>
    </td></tr>

  </table>
</td></tr>
</table>
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
