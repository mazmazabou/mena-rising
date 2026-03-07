"""MENA Rising Pipeline — Master Orchestrator

Usage:
    python run_pipeline.py                # Full pipeline
    python run_pipeline.py --fetch-only   # Only collect data (Phase 1)
    python run_pipeline.py --generate-only # Only run AI generation (Phase 2)
    python run_pipeline.py --dry-run      # Full pipeline but don't write final output
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import config  # config.py loads .env automatically
import collect_data
import generate_brief

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


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
    args = parser.parse_args()

    will_generate = not args.fetch_only
    if not validate_env(will_generate):
        sys.exit(1)

    # Ensure directories exist
    config.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)

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
