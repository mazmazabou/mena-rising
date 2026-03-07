"""MENA Rising Pipeline — Master Orchestrator

Usage:
    python run_pipeline.py                # Full pipeline
    python run_pipeline.py --fetch-only   # Only collect data (Phase 1)
    python run_pipeline.py --generate-only # Only run AI generation (Phase 2)
    python run_pipeline.py --dry-run      # Full pipeline but don't write final output
    python run_pipeline.py --archive-only # Only archive current brief
"""

import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

import config  # config.py loads .env automatically
import collect_data
import generate_brief

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def archive_current():
    """Archive the current latest_brief.json before generating a new one."""
    if not config.OUTPUT_FILE.exists():
        log.info("No existing brief to archive — skipping")
        return

    brief = json.loads(config.OUTPUT_FILE.read_text())
    issue = brief.get("issue", {})
    number = issue.get("number", "000")
    week_of = issue.get("weekOf", "")

    # Extract headline — use dedicated field or fall back to first sentence of bottomLine
    headline = brief.get("headline", "")
    if not headline:
        bottom = brief.get("bottomLine", "")
        headline = bottom.split(". ")[0] if bottom else f"Issue #{number}"

    # Parse weekOf (e.g. "March 9, 2026") to YYYY-MM-DD
    try:
        dt = datetime.strptime(week_of, "%B %d, %Y")
        date_str = dt.strftime("%Y-%m-%d")
    except ValueError:
        date_str = ""
        log.warning("Could not parse weekOf '%s' — date will be empty", week_of)

    filename = f"issue-{number}.json"

    # Ensure archive directory exists
    config.ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    # Read existing manifest or start fresh
    if config.MANIFEST_FILE.exists():
        manifest = json.loads(config.MANIFEST_FILE.read_text())
    else:
        manifest = []

    # Skip if this issue is already archived
    issue_num = int(number)
    if any(entry.get("issue") == issue_num for entry in manifest):
        log.info("Issue #%s already archived — skipping", number)
        return

    # Copy brief to archive
    shutil.copy2(config.OUTPUT_FILE, config.ARCHIVE_DIR / filename)

    # Prepend entry to manifest (newest first)
    manifest.insert(0, {
        "issue": issue_num,
        "date": date_str,
        "headline": headline,
        "filename": filename,
    })
    config.MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    log.info("Archived Issue #%s → %s", number, config.ARCHIVE_DIR / filename)


def validate_env(will_generate: bool) -> bool:
    """Validate required environment variables. Warns for optional keys."""
    ok = True

    if will_generate and not config.ANTHROPIC_API_KEY:
        log.error("ANTHROPIC_API_KEY is required for AI generation. Set it in .env or environment.")
        ok = False

    # Optional keys — warn but don't fail
    if not config.FINNHUB_API_KEY:
        log.warning("FINNHUB_API_KEY not set — FX rates will fall back to yfinance")
    if not config.NEWS_API_KEY:
        log.warning("NEWS_API_KEY not set — news headlines will be skipped")

    return ok


def print_summary(brief: dict):
    """Print a success summary with key data points."""
    print("\n" + "=" * 60)
    print("MENA Rising Pipeline — Success")
    print("=" * 60)

    issue = brief.get("issue", {})
    print(f"  Issue:    #{issue.get('number', '?')} — Week of {issue.get('weekOf', '?')}")

    ticker = brief.get("ticker", [])
    for t in ticker[:3]:
        change_str = f" ({t['change']:+.1f}%)" if t.get("change") is not None else ""
        print(f"  {t['label']}: {t['value']}{change_str}")

    macro = brief.get("macroPulse", [])
    populated = sum(1 for m in macro if m.get("value") is not None)
    print(f"  Macro Pulse: {populated}/12 metrics populated")

    if brief.get("bottomLine"):
        print(f"  Bottom Line: {brief['bottomLine'][:80]}...")

    risks = brief.get("risks", [])
    if risks:
        print(f"  Risks: {len(risks)} ({', '.join(r.get('level', '?') for r in risks)})")

    print(f"  Output: {config.OUTPUT_FILE}")
    print("=" * 60 + "\n")


def main():
    parser = argparse.ArgumentParser(description="MENA Rising Data Pipeline")
    parser.add_argument("--fetch-only", action="store_true", help="Only collect data (Phase 1)")
    parser.add_argument("--generate-only", action="store_true", help="Only run AI generation (Phase 2)")
    parser.add_argument("--dry-run", action="store_true", help="Full pipeline, don't write final output")
    parser.add_argument("--archive-only", action="store_true", help="Only archive current brief")
    args = parser.parse_args()

    # Archive-only mode
    if args.archive_only:
        archive_current()
        sys.exit(0)

    will_generate = not args.fetch_only
    if not validate_env(will_generate):
        sys.exit(1)

    # Ensure directories exist
    config.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

    # Archive the current brief before generating a new one
    if not args.generate_only:
        archive_current()

    brief = None
    exit_code = 0

    # Phase 1: Collect raw data
    if not args.generate_only:
        try:
            log.info("=== Phase 1: Collecting Data ===")
            payload = collect_data.collect_all()
            log.info(
                "Data collection complete — %d sources succeeded, %d failed",
                len(payload.get("metadata", {}).get("sources_succeeded", [])),
                len(payload.get("metadata", {}).get("sources_failed", [])),
            )
        except Exception as e:
            log.error("Fatal error during data collection: %s", e)
            sys.exit(1)

    # Phase 2: Generate AI brief
    if not args.fetch_only:
        try:
            log.info("=== Phase 2: Generating AI Brief ===")
            if args.dry_run:
                # Generate but don't write to final output
                brief = generate_brief.generate_brief()
                log.info("Dry run — brief generated but output may be overwritten")
            else:
                brief = generate_brief.generate_brief()
            log.info("AI brief generation complete")
        except Exception as e:
            log.error("AI generation failed: %s", e)
            exit_code = 2  # Partial success

    if brief is None and args.fetch_only:
        # For fetch-only, show payload summary instead
        if config.DATA_PAYLOAD_FILE.exists():
            payload = json.loads(config.DATA_PAYLOAD_FILE.read_text())
            meta = payload.get("metadata", {})
            print("\n" + "=" * 60)
            print("MENA Rising Pipeline — Data Collection Complete")
            print("=" * 60)
            print(f"  Sources succeeded: {meta.get('sources_succeeded', [])}")
            print(f"  Sources failed:    {meta.get('sources_failed', [])}")
            print(f"  Payload:           {config.DATA_PAYLOAD_FILE}")
            print("=" * 60 + "\n")
        sys.exit(exit_code)

    if brief is None:
        log.error("No brief data produced")
        sys.exit(1)

    # Validate
    issues = generate_brief.validate_brief(brief)
    if issues:
        log.warning("Validation issues:")
        for issue in issues:
            log.warning("  - %s", issue)
        if exit_code == 0:
            exit_code = 2

    print_summary(brief)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
