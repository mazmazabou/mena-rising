"""MENA Rising Pipeline — Claude AI Commentary Generation

Reads the partial brief (with API data), prompts Claude to generate editorial
content and AI-estimated metrics, then merges everything into the final brief.
"""

import json
import logging
import time
from datetime import datetime

import anthropic

from config import ANTHROPIC_API_KEY, OUTPUT_FILE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


def build_system_prompt() -> str:
    return f"""You are a senior MENA economic analyst producing a weekly intelligence briefing.
Your tone matches the Financial Times and The Economist — authoritative, concise, data-driven.
Today's date: {datetime.now().strftime("%B %d, %Y")}.
You MUST respond with valid JSON only. No markdown, no commentary, no code fences."""


def build_user_prompt(partial_brief: dict) -> str:
    # Extract real data for context
    ticker_summary = []
    for t in partial_brief.get("ticker", []):
        ticker_summary.append(f"  {t['label']}: {t['value']}")

    macro_summary = []
    for m in partial_brief.get("macroPulse", []):
        if m["value"] is not None:
            macro_summary.append(f"  {m['country']} {m['metric']}: {m['value']}{m['unit']}")

    youth_summary = []
    for y in partial_brief.get("laborSignals", {}).get("youthUnemployment", []):
        youth_summary.append(f"  {y['country']}: {y['value']}%")

    return f"""Here is the current MENA economic data from API sources:

TICKER:
{chr(10).join(ticker_summary)}

MACRO INDICATORS (from APIs):
{chr(10).join(macro_summary)}

YOUTH UNEMPLOYMENT:
{chr(10).join(youth_summary)}

Generate a JSON object with EXACTLY these fields:

{{
  "bottomLine": "3-4 sentences of BCG-quality macro commentary referencing the real data values above. Connect themes across countries.",

  "notableFlows": [
    "sentence 1 about a capital/trade flow",
    "sentence 2",
    "sentence 3",
    "sentence 4"
  ],

  "dealsToWatch": [
    {{
      "name": "Deal name",
      "parties": "Party1 · Party2 · Party3",
      "value": "$XB",
      "status": "Active"
    }},
    {{
      "name": "Deal name 2",
      "parties": "Party1 · Party2",
      "value": "$XB",
      "status": "In Progress"
    }},
    {{
      "name": "Deal name 3",
      "parties": "Party1 · Party2 · Party3",
      "value": "$XB",
      "status": "MOU Signed"
    }}
  ],

  "risks": [
    {{
      "level": "HIGH",
      "title": "Short risk title",
      "description": "2-3 sentences with specific data points.",
      "countries": ["Country1", "Country2"]
    }},
    {{
      "level": "MEDIUM",
      "title": "Short risk title",
      "description": "2-3 sentences with specific data points.",
      "countries": ["Country1"]
    }},
    {{
      "level": "LOW",
      "title": "Short risk title",
      "description": "2-3 sentences with specific data points.",
      "countries": ["Country1", "Country2", "Country3"]
    }}
  ],

  "aiMacroPulse": [
    {{
      "country": "Saudi Arabia",
      "metric": "Oil Revenue",
      "value": <number in $B>,
      "change": <number>,
      "sparkline": [<6 plausible trend numbers>]
    }},
    {{
      "country": "UAE",
      "metric": "PMI",
      "value": <number, typically 50-58>,
      "change": <number>,
      "sparkline": [<6 numbers>]
    }},
    {{
      "country": "UAE",
      "metric": "FDI Inflows",
      "value": <number in $B>,
      "change": <number>,
      "sparkline": [<6 numbers>]
    }},
    {{
      "country": "Morocco",
      "metric": "Tourism Revenue",
      "value": <number, % YoY growth>,
      "change": <number>,
      "sparkline": [<6 numbers>]
    }},
    {{
      "country": "Qatar",
      "metric": "LNG Exports",
      "value": <number, % YoY growth>,
      "change": <number>,
      "sparkline": [<6 numbers>]
    }},
    {{
      "country": "Qatar",
      "metric": "Budget Surplus",
      "value": <number, % GDP>,
      "change": <number>,
      "sparkline": [<6 numbers>]
    }}
  ],

  "aiAdoption": [
    {{"country": "UAE", "rank": 1, "score": <0-100>}},
    {{"country": "Saudi Arabia", "rank": 2, "score": <0-100>}},
    {{"country": "Qatar", "rank": 3, "score": <0-100>}},
    {{"country": "Egypt", "rank": 4, "score": <0-100>}},
    {{"country": "Morocco", "rank": 5, "score": <0-100>}}
  ],

  "techJobs": {{
    "trend": "up",
    "change": <integer, YoY % growth>,
    "context": "One sentence describing MENA tech job market trends."
  }}
}}

CONSTRAINTS:
- "parties" uses " · " (space-middle dot-space) as separator
- "status" must be one of: "Active", "In Progress", "MOU Signed", "Under Review"
- risks: exactly one HIGH, one MEDIUM, one LOW
- All sparkline arrays must have exactly 6 numbers
- All numeric values should be plausible for current MENA conditions
- Reference actual data values in the bottomLine commentary
- Return ONLY the JSON object, nothing else"""


def call_claude(system_prompt: str, user_prompt: str) -> dict:
    """Call Claude API and parse JSON response. Retries up to 3 times."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    for attempt in range(3):
        try:
            log.info("Calling Claude (attempt %d/3)...", attempt + 1)
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = response.content[0].text.strip()

            # Strip markdown code fences if present
            if text.startswith("```"):
                lines = text.split("\n")
                # Remove first line (```json or ```) and last line (```)
                lines = [l for l in lines if not l.strip().startswith("```")]
                text = "\n".join(lines)

            result = json.loads(text)
            log.info("Claude response parsed successfully")
            return result

        except json.JSONDecodeError as e:
            log.warning("Failed to parse Claude response as JSON (attempt %d): %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))
        except anthropic.APIError as e:
            log.warning("Claude API error (attempt %d): %s", attempt + 1, e)
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))

    raise RuntimeError("Failed to get valid response from Claude after 3 attempts")


def merge_ai_into_brief(partial_brief: dict, ai_output: dict) -> dict:
    """Merge AI-generated fields into the partial brief."""
    brief = partial_brief.copy()

    # Top-level AI fields
    brief["bottomLine"] = ai_output["bottomLine"]
    brief["notableFlows"] = ai_output["notableFlows"]
    brief["dealsToWatch"] = ai_output["dealsToWatch"]
    brief["risks"] = ai_output["risks"]

    # Labor signals
    brief["laborSignals"]["aiAdoption"] = ai_output["aiAdoption"]
    brief["laborSignals"]["techJobs"] = ai_output["techJobs"]

    # Merge AI macro pulse metrics into the existing array
    ai_macro_by_key = {}
    for m in ai_output.get("aiMacroPulse", []):
        key = f"{m['country']}/{m['metric']}"
        ai_macro_by_key[key] = m

    for i, existing in enumerate(brief["macroPulse"]):
        key = f"{existing['country']}/{existing['metric']}"
        if existing["value"] is None and key in ai_macro_by_key:
            ai_m = ai_macro_by_key[key]
            brief["macroPulse"][i]["value"] = ai_m["value"]
            brief["macroPulse"][i]["change"] = ai_m["change"]
            brief["macroPulse"][i]["sparkline"] = ai_m["sparkline"]

    # Remove internal metadata
    brief.pop("_metadata", None)

    return brief


def validate_brief(brief: dict) -> list[str]:
    """Validate the completed brief against expected schema. Returns list of issues."""
    issues = []

    # Top-level fields
    for field in ["issue", "ticker", "bottomLine", "macroPulse", "notableFlows", "dealsToWatch", "laborSignals", "risks"]:
        if field not in brief:
            issues.append(f"Missing top-level field: {field}")

    # Ticker
    if isinstance(brief.get("ticker"), list):
        if len(brief["ticker"]) != 6:
            issues.append(f"ticker has {len(brief['ticker'])} items, expected 6")

    # MacroPulse
    if isinstance(brief.get("macroPulse"), list):
        if len(brief["macroPulse"]) != 12:
            issues.append(f"macroPulse has {len(brief['macroPulse'])} items, expected 12")
        for i, m in enumerate(brief["macroPulse"]):
            if m.get("value") is None:
                issues.append(f"macroPulse[{i}] ({m.get('country')}/{m.get('metric')}) has null value")
            if not isinstance(m.get("sparkline"), list) or len(m.get("sparkline", [])) != 6:
                issues.append(f"macroPulse[{i}] sparkline should have 6 points")

    # Notable flows
    if isinstance(brief.get("notableFlows"), list):
        if len(brief["notableFlows"]) != 4:
            issues.append(f"notableFlows has {len(brief['notableFlows'])} items, expected 4")

    # Deals
    if isinstance(brief.get("dealsToWatch"), list):
        if len(brief["dealsToWatch"]) != 3:
            issues.append(f"dealsToWatch has {len(brief['dealsToWatch'])} items, expected 3")

    # Risks
    if isinstance(brief.get("risks"), list):
        if len(brief["risks"]) != 3:
            issues.append(f"risks has {len(brief['risks'])} items, expected 3")
        levels = {r.get("level") for r in brief.get("risks", [])}
        for expected in ["HIGH", "MEDIUM", "LOW"]:
            if expected not in levels:
                issues.append(f"risks missing level: {expected}")

    # Labor signals
    ls = brief.get("laborSignals", {})
    if not isinstance(ls.get("youthUnemployment"), list) or len(ls.get("youthUnemployment", [])) < 4:
        issues.append("laborSignals.youthUnemployment should have at least 4 entries")
    if not isinstance(ls.get("aiAdoption"), list) or len(ls.get("aiAdoption", [])) != 5:
        issues.append("laborSignals.aiAdoption should have 5 entries")
    if not isinstance(ls.get("techJobs"), dict):
        issues.append("laborSignals.techJobs should be an object")

    return issues


def generate_commentary(brief_path: str | None = None) -> dict:
    """Main entry: read partial brief → prompt Claude → merge → validate → write."""
    path = brief_path or str(OUTPUT_FILE)
    log.info("Reading partial brief from %s", path)
    partial = json.loads(open(path).read())

    system_prompt = build_system_prompt()
    user_prompt = build_user_prompt(partial)

    ai_output = call_claude(system_prompt, user_prompt)

    brief = merge_ai_into_brief(partial, ai_output)

    issues = validate_brief(brief)
    if issues:
        log.warning("Validation issues found:")
        for issue in issues:
            log.warning("  - %s", issue)
    else:
        log.info("Validation passed")

    OUTPUT_FILE.write_text(json.dumps(brief, indent=2, ensure_ascii=False))
    log.info("Completed brief written to %s", OUTPUT_FILE)

    return brief


if __name__ == "__main__":
    generate_commentary()
