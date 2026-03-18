"""MENA Rising Pipeline — AI Brief Generation

Reads data_payload.json (raw collected data), sends to Claude to produce
the complete brief JSON, validates, and writes latest_brief.json.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import anthropic

from config import ANTHROPIC_API_KEY, COUNTRIES, DATA_PAYLOAD_FILE, LOGS_DIR, OUTPUT_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ── Issue Metadata ───────────────────────────────────────────────────────────

def compute_issue_metadata() -> dict:
    """Compute issue number and weekOf date.

    weekOf = upcoming Monday. Number auto-incremented from existing output.
    """
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    if today.weekday() == 0:
        next_monday = today
    else:
        next_monday = today + timedelta(days=days_until_monday)

    week_of = next_monday.strftime("%B %d, %Y")
    parts = week_of.split(" ")
    parts[1] = str(int(parts[1].rstrip(","))) + ","
    week_of = " ".join(parts)

    number = "001"
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text())
            prev = int(existing.get("issue", {}).get("number", "0"))
            number = f"{prev + 1:03d}"

            # Ensure new weekOf is at least 7 days after previous
            prev_week_of = existing.get("issue", {}).get("weekOf", "")
            if prev_week_of:
                prev_dt = datetime.strptime(prev_week_of, "%B %d, %Y")
                if next_monday.replace(hour=0, minute=0, second=0, microsecond=0) <= prev_dt:
                    next_monday = prev_dt + timedelta(days=7)
                    week_of = next_monday.strftime("%B %d, %Y")
                    parts = week_of.split(" ")
                    parts[1] = str(int(parts[1].rstrip(","))) + ","
                    week_of = " ".join(parts)
        except Exception:
            pass

    return {"number": number, "weekOf": week_of}


# ── Prompts ──────────────────────────────────────────────────────────────────

def build_system_prompt() -> str:
    return f"""You are a senior MENA economic analyst producing a weekly intelligence briefing.
Your tone matches the Financial Times and The Economist — authoritative, concise, data-driven.
Today's date: {datetime.now().strftime("%B %d, %Y")}.

You will receive raw economic data from multiple sources. Your job is to produce the COMPLETE
weekly brief as a single JSON object matching the exact schema specified.

You MUST respond with valid JSON only. No markdown, no commentary, no code fences."""


def build_user_prompt(data_payload: dict, issue_metadata: dict) -> str:
    # Format macro data
    macro = data_payload.get("macro", {})
    macro_lines = []
    for indicator, countries_data in macro.items():
        macro_lines.append(f"\n  {indicator.upper()}:")
        if isinstance(countries_data, dict):
            for iso2, vals in countries_data.items():
                if isinstance(vals, dict) and vals.get("value") is not None:
                    macro_lines.append(f"    {iso2}: {vals['value']} (year: {vals.get('year', 'N/A')})")

    # Format commodities
    commodities = data_payload.get("commodities", {})
    comm_lines = []
    for name, vals in commodities.items():
        if isinstance(vals, dict) and vals.get("value") is not None:
            comm_lines.append(f"  {name}: ${vals['value']} (change: {vals.get('change_pct', 'N/A')}%)")

    # Format FX
    fx = data_payload.get("fx", {})
    fx_lines = []
    for pair, vals in fx.items():
        if isinstance(vals, dict) and vals.get("rate") is not None:
            fx_lines.append(f"  {pair}: {vals['rate']} (change: {vals.get('change_pct', 'N/A')}%)")

    # Format news headlines
    news = data_payload.get("news_headlines", [])
    news_lines = []
    for n in news[:10]:
        news_lines.append(f"  - {n.get('title', '')} ({n.get('source', '')})")

    # Format labor data
    labor = data_payload.get("labor", {})
    labor_lines = []
    for indicator, countries_data in labor.items():
        labor_lines.append(f"\n  {indicator.upper()}:")
        if isinstance(countries_data, dict):
            for iso2, vals in countries_data.items():
                if isinstance(vals, dict) and vals.get("value") is not None:
                    labor_lines.append(f"    {iso2}: {vals['value']}% (year: {vals.get('year', 'N/A')})")

    # Format risk events
    risk_events = data_payload.get("risk_events", [])
    risk_lines = []
    for r in risk_events[:15]:
        risk_lines.append(f"  - {r.get('title', '')} [{', '.join(r.get('countries', []))}]")

    # Country name/ISO mapping for reference
    country_map = {info["iso2"]: name for name, info in COUNTRIES.items()}
    country_flags = {name: info["flag"] for name, info in COUNTRIES.items()}

    return f"""Here is raw economic data collected from multiple sources. Use it to produce the complete weekly brief.

ISSUE METADATA (use exactly as given):
  number: "{issue_metadata['number']}"
  weekOf: "{issue_metadata['weekOf']}"

COUNTRY REFERENCE (ISO2 -> Name -> Flag):
{chr(10).join(f"  {iso2} -> {name} -> {country_flags[name]}" for iso2, name in country_map.items())}

MACRO INDICATORS (World Bank):
{chr(10).join(macro_lines)}

COMMODITIES (FRED / yfinance):
{chr(10).join(comm_lines)}

FX RATES:
{chr(10).join(fx_lines)}

NEWS HEADLINES (past 7 days):
{chr(10).join(news_lines) if news_lines else "  (no headlines available)"}

LABOR INDICATORS (World Bank WDI):
{chr(10).join(labor_lines)}

RISK/CONFLICT EVENTS (GDELT):
{chr(10).join(risk_lines) if risk_lines else "  (no events available)"}

SOURCE METADATA:
  succeeded: {data_payload.get("metadata", {}).get("sources_succeeded", [])}
  failed: {data_payload.get("metadata", {}).get("sources_failed", [])}

---

Generate a JSON object with EXACTLY this structure:

{{
  "issue": {{
    "number": "{issue_metadata['number']}",
    "weekOf": "{issue_metadata['weekOf']}"
  }},

  "headline": "<concise 10-15 word summary of the week's key theme, max 100 characters, no period at end>",

  "ticker": [
    {{"label": "EGP/USD", "value": "<formatted string, e.g. 49.82>", "change": <weekly % change or null>}},
    {{"label": "Brent Crude", "value": "<formatted string with $, e.g. $81.40>", "change": <weekly % change or null>}},
    {{"label": "SAR/USD", "value": "<formatted string, e.g. 3.75>", "change": 0}},
    {{"label": "<annual indicator 1>", "value": "<value with %>", "change": null}},
    {{"label": "<annual indicator 2>", "value": "<value with %>", "change": null}},
    {{"label": "<annual indicator 3>", "value": "<value with %>", "change": null}}
  ],

  "bottomLine": "<3-4 BCG-quality sentences referencing REAL data values from above. Connect themes across countries.>",

  "macroPulse": [
    {{
      "country": "<country name>",
      "flag": "<emoji flag>",
      "metric": "<metric name>",
      "value": <number>,
      "unit": "<%, $B, % GDP, or empty string>",
      "change": <number>,
      "sparkline": [<exactly 6 plausible trend numbers>]
    }}
  ],

  "notableFlows": [
    "<sentence 1 about a capital/trade flow>",
    "<sentence 2>",
    "<sentence 3>",
    "<sentence 4>"
  ],

  "dealsToWatch": [
    {{
      "name": "<deal name>",
      "parties": "<Party1 · Party2 · Party3>",
      "value": "<$XB>",
      "status": "<Active|In Progress|MOU Signed|Under Review>"
    }}
  ],

  "laborSignals": {{
    "youthUnemployment": [
      {{"country": "<country>", "value": <number>}}
    ],
    "aiAdoption": [
      {{"country": "<country>", "rank": <1-5>, "score": <0-100>}}
    ],
    "techJobs": {{
      "trend": "<up|down|flat>",
      "change": <integer YoY % growth>,
      "context": "<one sentence>"
    }}
  }},

  "risks": [
    {{
      "level": "<HIGH|MEDIUM|LOW|CRITICAL>",
      "title": "<short risk title>",
      "description": "<2-3 sentences with specific data points>",
      "countries": ["<Country1>", "<Country2>"]
    }}
  ]
}}

CONSTRAINTS:
1. "ticker": exactly 6 items. Use REAL data from FX/commodities above for first 3 items. Last 3 are annual indicators from macro data.
2. "macroPulse": exactly 12 items — 2 per displayed country (pick 6 countries from the 8). Use real WDI/macro data where available. For metrics without API data (Oil Revenue, PMI, FDI Inflows, Tourism Revenue, LNG Exports, Budget Surplus), provide AI-estimated plausible values.
3. "bottomLine": Reference actual data values from above.
4. "notableFlows": exactly 4 items.
5. "dealsToWatch": exactly 3 items. "parties" uses " · " (space-middle dot-space) as separator.
6. "risks": 3 items preferred — include a mix of severity levels (HIGH, MEDIUM, LOW, CRITICAL) based on actual risk assessment. Fewer is acceptable if warranted by the data.
7. "laborSignals.youthUnemployment": Use REAL WDI data. Include all countries that have data, sorted descending by value.
8. "laborSignals.aiAdoption": 5 entries with AI-estimated scores (0-100).
9. "laborSignals.techJobs": AI-estimated.
10. All sparkline arrays must have exactly 6 numbers.
11. "headline": a single sentence, max 100 characters, no period at the end. Captures the week's dominant theme.
12. Return ONLY the JSON object, nothing else."""


# ── Validation ───────────────────────────────────────────────────────────────

def validate_brief(brief: dict) -> tuple[list[str], list[str]]:
    """Validate the completed brief against expected schema.

    Returns (errors, warnings):
      - errors: structural failures that break the frontend (exit code 2)
      - warnings: content variation that doesn't break the frontend (logged, exit code 0)
    """
    errors = []
    warnings = []

    for field in ["issue", "headline", "ticker", "bottomLine", "macroPulse", "notableFlows", "dealsToWatch", "laborSignals", "risks"]:
        if field not in brief:
            errors.append(f"Missing top-level field: {field}")

    if not isinstance(brief.get("headline"), str) or not brief.get("headline", "").strip():
        errors.append("headline must be a non-empty string")

    if isinstance(brief.get("ticker"), list):
        if len(brief["ticker"]) != 6:
            errors.append(f"ticker has {len(brief['ticker'])} items, expected 6")

    if isinstance(brief.get("macroPulse"), list):
        if len(brief["macroPulse"]) != 12:
            errors.append(f"macroPulse has {len(brief['macroPulse'])} items, expected 12")
        for i, m in enumerate(brief["macroPulse"]):
            if m.get("value") is None:
                errors.append(f"macroPulse[{i}] ({m.get('country')}/{m.get('metric')}) has null value")
            if not isinstance(m.get("sparkline"), list) or len(m.get("sparkline", [])) != 6:
                errors.append(f"macroPulse[{i}] sparkline should have 6 points")

    if isinstance(brief.get("notableFlows"), list):
        if len(brief["notableFlows"]) != 4:
            warnings.append(f"notableFlows has {len(brief['notableFlows'])} items, expected 4")

    if isinstance(brief.get("dealsToWatch"), list):
        if len(brief["dealsToWatch"]) != 3:
            warnings.append(f"dealsToWatch has {len(brief['dealsToWatch'])} items, expected 3")

    if isinstance(brief.get("risks"), list):
        if len(brief["risks"]) != 3:
            warnings.append(f"risks has {len(brief['risks'])} items, expected 3")
        levels = {r.get("level") for r in brief.get("risks", [])}
        for expected in ["HIGH", "MEDIUM", "LOW"]:
            if expected not in levels:
                warnings.append(f"risks missing level: {expected}")
    else:
        if "risks" in brief:
            errors.append("risks must be a list")

    ls = brief.get("laborSignals", {})
    if not isinstance(ls.get("youthUnemployment"), list) or len(ls.get("youthUnemployment", [])) < 4:
        errors.append("laborSignals.youthUnemployment should have at least 4 entries")
    if not isinstance(ls.get("aiAdoption"), list) or len(ls.get("aiAdoption", [])) != 5:
        errors.append("laborSignals.aiAdoption should have 5 entries")
    if not isinstance(ls.get("techJobs"), dict):
        errors.append("laborSignals.techJobs should be an object")

    return errors, warnings


# ── Claude API ───────────────────────────────────────────────────────────────

def call_claude_with_retry(system_prompt: str, user_prompt: str) -> dict:
    """Call Claude API, validate response, retry once with error feedback if validation fails."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def _call(messages: list[dict]) -> tuple[str, dict]:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8192,
            temperature=0.7,
            system=system_prompt,
            messages=messages,
        )
        text = response.content[0].text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)

        return text, json.loads(text)

    # First attempt
    try:
        log.info("Calling Claude (attempt 1/2)...")
        messages = [{"role": "user", "content": user_prompt}]
        raw_text, result = _call(messages)

        # Log raw response
        _log_claude_response(raw_text, attempt=1)

        # Validate
        errors, warnings = validate_brief(result)
        if not errors:
            if warnings:
                log.warning("Validation warnings (non-blocking): %s", warnings)
            log.info("Claude response validated successfully on first attempt")
            return result

        # Retry with validation feedback (only errors, not warnings)
        log.warning("Validation errors on first attempt: %s", errors)
        log.info("Calling Claude (attempt 2/2 with validation feedback)...")

        feedback = (
            "Your previous response had these validation errors:\n"
            + "\n".join(f"- {issue}" for issue in errors)
            + "\n\nPlease fix these issues and return the corrected JSON."
        )
        messages.append({"role": "assistant", "content": raw_text})
        messages.append({"role": "user", "content": feedback})

        raw_text_2, result_2 = _call(messages)
        _log_claude_response(raw_text_2, attempt=2)

        errors_2, warnings_2 = validate_brief(result_2)
        if errors_2:
            log.warning("Validation errors remain after retry: %s", errors_2)
        if warnings_2:
            log.warning("Validation warnings (non-blocking): %s", warnings_2)
        if not errors_2:
            log.info("Claude response validated successfully on retry")

        return result_2

    except json.JSONDecodeError as e:
        log.error("Failed to parse Claude response as JSON: %s", e)
        raise RuntimeError(f"Claude returned invalid JSON: {e}")
    except anthropic.APIError as e:
        log.error("Claude API error: %s", e)
        raise RuntimeError(f"Claude API error: {e}")


def _log_claude_response(raw_text: str, attempt: int):
    """Save Claude's raw response to logs directory."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"{timestamp}_claude_response_attempt{attempt}.json"
    log_file.write_text(raw_text)
    log.info("Claude response logged to %s", log_file)


# ── Main Entry ───────────────────────────────────────────────────────────────

def generate_brief(payload_path: str | None = None) -> dict:
    """Main entry: load data_payload.json -> prompt Claude -> validate -> write."""
    path = Path(payload_path) if payload_path else DATA_PAYLOAD_FILE
    log.info("Reading data payload from %s", path)

    if not path.exists():
        raise FileNotFoundError(f"Data payload not found: {path}")

    data_payload = json.loads(path.read_text())
    issue_metadata = compute_issue_metadata()

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(data_payload, issue_metadata)

    brief = call_claude_with_retry(system_prompt, user_prompt)

    # Ensure issue metadata is deterministic (override AI output)
    brief["issue"] = issue_metadata

    # Final validation
    errors, warnings = validate_brief(brief)
    if errors:
        log.warning("Final validation errors:")
        for e in errors:
            log.warning("  - %s", e)
    if warnings:
        log.warning("Final validation warnings (non-blocking):")
        for w in warnings:
            log.warning("  - %s", w)
    if not errors and not warnings:
        log.info("Final validation passed")

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(brief, indent=2, ensure_ascii=False))
    log.info("Completed brief written to %s", OUTPUT_FILE)

    return brief


if __name__ == "__main__":
    generate_brief()
