#!/usr/bin/env python3
"""Send an email alert when the MENA Rising pipeline fails in GitHub Actions."""

import argparse
import os
import sys
from datetime import datetime, timezone

try:
    import resend
except ImportError:
    print("Installing resend SDK...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "resend", "-q"])
    import resend


def main():
    parser = argparse.ArgumentParser(description="Send pipeline failure alert")
    parser.add_argument("--run-url", required=True, help="GitHub Actions run URL")
    args = parser.parse_args()

    api_key = os.environ.get("RESEND_API_KEY")
    if not api_key:
        print("ERROR: RESEND_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    resend.api_key = api_key
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html_body = f"""\
<div style="font-family: Georgia, 'Times New Roman', serif; max-width: 560px; margin: 0 auto; color: #1a1a2e;">
  <h1 style="font-size: 22px; color: #c0392b; margin-bottom: 16px;">Pipeline Failure Alert</h1>
  <p style="font-size: 15px; line-height: 1.6;">
    The MENA Rising weekly pipeline failed at <strong>{timestamp}</strong>.
  </p>
  <p style="font-size: 15px; line-height: 1.6;">
    <a href="{args.run_url}" style="color: #c9a84c;">View the GitHub Actions run</a>
    to inspect logs and identify the failure.
  </p>
  <p style="font-size: 13px; color: #666; margin-top: 32px;">
    This is an automated ops alert from MENA Rising.
  </p>
</div>"""

    try:
        resend.Emails.send({
            "from": "MENA Rising Alerts <brief@mena-rising.com>",
            "to": ["abouelelamazen@gmail.com"],
            "subject": f"Warning: MENA Rising Pipeline Failed \u2014 {timestamp}",
            "html": html_body,
        })
        print(f"Failure alert sent to abouelelamazen@gmail.com")
    except Exception as e:
        print(f"ERROR sending alert: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
