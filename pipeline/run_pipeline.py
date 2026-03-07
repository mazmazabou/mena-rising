"""MENA Rising Pipeline — Master Orchestrator

Usage:
    python run_pipeline.py                # Full pipeline
    python run_pipeline.py --fetch-only   # Only fetch API data
    python run_pipeline.py --generate-only # Only run AI generation
    python run_pipeline.py --dry-run      # Full pipeline but don't write output
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from dotenv import load_dotenv

# Load .env BEFORE importing config, so os.environ is populated
# when config.py reads ANTHROPIC_API_KEY / FRED_API_KEY at module level.
load_dotenv(Path(__file__).resolve().parent / ".env")

import config
import fetch_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def validate_env(generate: bool) -> bool:
    """Validate required environment variables."""
    if generate and not config.ANTHROPIC_API_KEY:
        log.error("ANTHROPIC_API_KEY is required for AI generation. Set it in .env or environment.")
        return False
    return True


def validate_output(brief: dict) -> list[str]:
    """Validate the output JSON against expected schema."""
    from generate_commentary import validate_brief
    return validate_brief(brief)


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
    parser.add_argument("--fetch-only", action="store_true", help="Only fetch API data")
    parser.add_argument("--generate-only", action="store_true", help="Only run AI generation")
    parser.add_argument("--dry-run", action="store_true", help="Full pipeline, don't write output")
    args = parser.parse_args()

    will_generate = not args.fetch_only
    if not validate_env(will_generate):
        sys.exit(1)

    # Ensure output directory exists
    config.OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    brief = None
    exit_code = 0

    # Step 1: Fetch API data
    if not args.generate_only:
        try:
            log.info("=== Phase 1: Fetching API Data ===")
            brief = fetch_data.fetch_all()
            log.info("API data fetch complete")
        except Exception as e:
            log.error("Fatal error during data fetch: %s", e)
            sys.exit(1)

    # Step 2: Generate AI commentary
    if not args.fetch_only:
        try:
            log.info("=== Phase 2: Generating AI Commentary ===")
            import generate_commentary

            if args.dry_run and brief:
                # Write temporary file for AI generation, then clean up
                import tempfile
                tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)
                json.dump(brief, tmp, indent=2, ensure_ascii=False)
                tmp.close()
                brief = generate_commentary.generate_commentary(tmp.name)
                Path(tmp.name).unlink()
            else:
                brief = generate_commentary.generate_commentary()
            log.info("AI commentary generation complete")
        except Exception as e:
            log.error("AI generation failed: %s", e)
            exit_code = 2  # Partial success

    if brief is None:
        log.error("No brief data produced")
        sys.exit(1)

    # Step 3: Validate
    issues = validate_output(brief)
    if issues:
        log.warning("Validation issues:")
        for issue in issues:
            log.warning("  - %s", issue)
        if exit_code == 0:
            exit_code = 2  # Partial success

    # Step 4: Write output (unless dry-run)
    if args.dry_run:
        log.info("Dry run — output not written")
    elif not args.fetch_only and not args.generate_only:
        # Already written by generate_commentary
        pass

    print_summary(brief)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
