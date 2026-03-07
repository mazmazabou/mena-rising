"""MENA Rising Pipeline — API Data Fetching

Fetches economic data from World Bank, yfinance, and FRED APIs.
Produces a partial JSON brief with API-populated fields and nulls for AI-generated fields.
"""

import json
import logging
import time
from datetime import datetime, timedelta

import requests
import yfinance as yf

from config import (
    COUNTRIES,
    FRED_API_KEY,
    FRED_SERIES,
    INVERT_TICKERS,
    MACRO_PULSE_METRICS,
    OUTPUT_FILE,
    SPARKLINE_POINTS,
    WB_INDICATORS,
    YFINANCE_TICKERS,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ── World Bank ─────────────────────────────────────────────────────────────────

def fetch_world_bank(indicator: str, country_iso2: str, num_years: int = 10) -> list[dict]:
    """Fetch World Bank indicator data for a country.

    Returns list of {"year": int, "value": float} sorted ascending by year.
    """
    end_year = datetime.now().year
    start_year = end_year - num_years
    url = (
        f"https://api.worldbank.org/v2/country/{country_iso2}/indicator/{indicator}"
        f"?format=json&per_page=50&date={start_year}:{end_year}"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if len(data) < 2 or data[1] is None:
            log.warning("World Bank returned no data for %s/%s", indicator, country_iso2)
            return []
        records = [
            {"year": int(entry["date"]), "value": entry["value"]}
            for entry in data[1]
            if entry["value"] is not None
        ]
        records.sort(key=lambda r: r["year"])
        return records
    except Exception as e:
        log.warning("World Bank fetch failed for %s/%s: %s", indicator, country_iso2, e)
        return []


def get_wb_latest_and_sparkline(indicator: str, country_iso2: str) -> dict:
    """Get latest value, year-over-year change, and sparkline from World Bank data."""
    records = fetch_world_bank(indicator, country_iso2)
    if not records:
        return {"value": None, "change": None, "sparkline": []}

    sparkline_records = records[-SPARKLINE_POINTS:]
    sparkline = [round(r["value"], 1) for r in sparkline_records]
    latest = sparkline_records[-1]["value"]

    change = None
    if len(sparkline_records) >= 2:
        prev = sparkline_records[-2]["value"]
        change = round(latest - prev, 1)

    return {"value": round(latest, 1), "change": change, "sparkline": sparkline}


# ── yfinance ───────────────────────────────────────────────────────────────────

def fetch_yfinance_weekly(ticker_symbol: str, weeks: int = 8) -> list[dict]:
    """Fetch weekly closing prices from yfinance.

    Returns list of {"date": str, "close": float} sorted ascending.
    """
    try:
        df = yf.download(ticker_symbol, period="60d", interval="1wk", progress=False)
        if df.empty:
            log.warning("yfinance returned no data for %s", ticker_symbol)
            return []
        records = []
        for date, row in df.iterrows():
            close_val = row["Close"]
            # Handle both scalar and Series (multi-level columns)
            if hasattr(close_val, "item"):
                close_val = close_val.item()
            elif hasattr(close_val, "iloc"):
                close_val = close_val.iloc[0]
            records.append({"date": str(date.date()), "close": float(close_val)})
        return records
    except Exception as e:
        log.warning("yfinance fetch failed for %s: %s", ticker_symbol, e)
        return []


def get_yf_latest_and_sparkline(ticker_symbol: str, invert: bool = False) -> dict:
    """Get latest value, week-over-week % change, and sparkline from yfinance.

    If invert=True, values are inverted (1/x) — used for currency pairs where
    yfinance returns USD-per-X but we need X-per-USD.
    """
    records = fetch_yfinance_weekly(ticker_symbol)
    if not records:
        return {"value": None, "change": None, "sparkline": []}

    sparkline_records = records[-SPARKLINE_POINTS:]

    if invert:
        sparkline = [round(1.0 / r["close"], 2) for r in sparkline_records if r["close"] != 0]
        latest = 1.0 / sparkline_records[-1]["close"] if sparkline_records[-1]["close"] != 0 else None
    else:
        sparkline = [round(r["close"], 2) for r in sparkline_records]
        latest = sparkline_records[-1]["close"]

    change = None
    if latest is not None and len(sparkline_records) >= 2:
        if invert:
            prev = 1.0 / sparkline_records[-2]["close"] if sparkline_records[-2]["close"] != 0 else None
        else:
            prev = sparkline_records[-2]["close"]
        if prev and prev != 0:
            change = round(((latest - prev) / prev) * 100, 1)

    return {"value": round(latest, 2) if latest else None, "change": change, "sparkline": sparkline}


# ── FRED (fallback for oil) ───────────────────────────────────────────────────

def fetch_fred_series(series_id: str, num_observations: int = 50) -> list[dict]:
    """Fetch FRED time series data. Used as fallback for Brent Crude."""
    if not FRED_API_KEY:
        log.warning("FRED_API_KEY not set, skipping FRED fetch")
        return []
    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}&api_key={FRED_API_KEY}&file_type=json"
        f"&sort_order=desc&limit={num_observations}"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        records = [
            {"date": obs["date"], "value": float(obs["value"])}
            for obs in data.get("observations", [])
            if obs["value"] != "."
        ]
        records.sort(key=lambda r: r["date"])
        return records
    except Exception as e:
        log.warning("FRED fetch failed for %s: %s", series_id, e)
        return []


# ── Ticker Strip ──────────────────────────────────────────────────────────────

def build_ticker() -> list[dict]:
    """Build the 6-item ticker strip matching the frontend schema.

    - Currency pairs & oil: string-formatted value, weekly % change
    - Annual indicators: value with % suffix, change=null
    """
    ticker = []

    # 1. EGP/USD (inverted: yfinance gives USD/EGP, we want EGP/USD)
    egp = get_yf_latest_and_sparkline(YFINANCE_TICKERS["EGP/USD"], invert=True)
    ticker.append({
        "label": "EGP/USD",
        "value": f"{egp['value']:.2f}" if egp["value"] else "N/A",
        "change": egp["change"],
    })

    # 2. Brent Crude (yfinance primary, FRED fallback)
    brent = get_yf_latest_and_sparkline(YFINANCE_TICKERS["Brent Crude"])
    if brent["value"] is None:
        log.info("Brent Crude yfinance failed, trying FRED fallback")
        fred_data = fetch_fred_series(FRED_SERIES["brent_crude"])
        if fred_data:
            recent = fred_data[-SPARKLINE_POINTS:]
            brent = {
                "value": round(recent[-1]["value"], 2),
                "change": round(((recent[-1]["value"] - recent[-2]["value"]) / recent[-2]["value"]) * 100, 1) if len(recent) >= 2 else None,
                "sparkline": [round(r["value"], 2) for r in recent],
            }
    ticker.append({
        "label": "Brent Crude",
        "value": f"${brent['value']:.2f}" if brent["value"] else "N/A",
        "change": brent["change"],
    })

    # 3. SAR/USD (inverted + pegged — change should be 0)
    sar = get_yf_latest_and_sparkline(YFINANCE_TICKERS["SAR/USD"], invert=True)
    ticker.append({
        "label": "SAR/USD",
        "value": f"{sar['value']:.2f}" if sar["value"] else "3.75",
        "change": 0,  # Pegged currency — show dash, not hide
    })

    # 4. Egypt Inflation (annual — change=null to hide indicator)
    egypt_inf = get_wb_latest_and_sparkline(WB_INDICATORS["inflation"], COUNTRIES["Egypt"]["iso2"])
    time.sleep(0.5)
    ticker.append({
        "label": "Egypt Inflation",
        "value": f"{egypt_inf['value']}%" if egypt_inf["value"] else "N/A",
        "change": None,  # null hides the change indicator
    })

    # 5. UAE GDP Growth (annual — change=null)
    uae_gdp = get_wb_latest_and_sparkline(WB_INDICATORS["gdp_growth"], COUNTRIES["UAE"]["iso2"])
    time.sleep(0.5)
    ticker.append({
        "label": "UAE GDP Growth",
        "value": f"{uae_gdp['value']}%" if uae_gdp["value"] else "N/A",
        "change": None,
    })

    # 6. Morocco CPI (annual — change=null)
    morocco_inf = get_wb_latest_and_sparkline(WB_INDICATORS["inflation"], COUNTRIES["Morocco"]["iso2"])
    ticker.append({
        "label": "Morocco CPI",
        "value": f"{morocco_inf['value']}%" if morocco_inf["value"] else "N/A",
        "change": None,
    })

    return ticker


# ── Macro Pulse ───────────────────────────────────────────────────────────────


def build_macro_pulse_api_data() -> list[dict]:
    """Build the 12-item macro pulse array.

    API-fetchable entries are fully populated. AI-generated entries have null values.
    """
    results = []
    for m in MACRO_PULSE_METRICS:
        country = m["country"]
        flag = COUNTRIES[country]["flag"]
        iso2 = COUNTRIES[country]["iso2"]
        source = m["source"]

        if source == "ai_generated":
            data = {"value": None, "change": None, "sparkline": []}
        elif source.startswith("wb_"):
            indicator_key = source.removeprefix("wb_")
            indicator_code = WB_INDICATORS.get(indicator_key)
            if indicator_code:
                data = get_wb_latest_and_sparkline(indicator_code, iso2)
                time.sleep(0.5)
            else:
                data = {"value": None, "change": None, "sparkline": []}
        elif source.startswith("yf_"):
            ticker_label = source.removeprefix("yf_")
            ticker_symbol = YFINANCE_TICKERS.get(ticker_label)
            if ticker_symbol:
                invert = ticker_label in INVERT_TICKERS
                data = get_yf_latest_and_sparkline(ticker_symbol, invert=invert)
            else:
                data = {"value": None, "change": None, "sparkline": []}
        else:
            data = {"value": None, "change": None, "sparkline": []}

        results.append({
            "country": country,
            "flag": flag,
            "metric": m["metric"],
            "value": data["value"],
            "unit": m["unit"],
            "change": data["change"],
            "sparkline": data["sparkline"],
        })

    return results


# ── Youth Unemployment ────────────────────────────────────────────────────────

def build_youth_unemployment() -> list[dict]:
    """Build youth unemployment data sorted descending by value."""
    indicator = WB_INDICATORS["youth_unemployment"]
    results = []
    for country, info in COUNTRIES.items():
        if country == "Turkey":
            continue  # Not in the frontend schema for youth unemployment
        wb = get_wb_latest_and_sparkline(indicator, info["iso2"])
        time.sleep(0.5)
        if wb["value"] is not None:
            results.append({"country": country, "value": wb["value"]})
        else:
            results.append({"country": country, "value": 0})

    results.sort(key=lambda r: r["value"], reverse=True)
    return results


# ── Issue Metadata ────────────────────────────────────────────────────────────

def compute_issue_metadata() -> dict:
    """Compute issue number and weekOf date.

    weekOf = upcoming Monday. Number auto-incremented from existing output.
    """
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7  # Next Monday, not today
    if today.weekday() == 0:
        next_monday = today  # Today is Monday
    else:
        next_monday = today + timedelta(days=days_until_monday)

    week_of = next_monday.strftime("%B %d, %Y")
    # Remove leading zero from day: "March 07" → "March 7"
    parts = week_of.split(" ")
    parts[1] = str(int(parts[1].rstrip(","))) + ","
    week_of = " ".join(parts)

    # Auto-increment issue number from existing output
    number = "001"
    if OUTPUT_FILE.exists():
        try:
            existing = json.loads(OUTPUT_FILE.read_text())
            prev = int(existing.get("issue", {}).get("number", "0"))
            number = f"{prev + 1:03d}"
        except Exception:
            pass

    return {"number": number, "weekOf": week_of}


# ── Main Assembly ─────────────────────────────────────────────────────────────

def fetch_all() -> dict:
    """Fetch all API data and assemble the partial brief JSON.

    AI-generated fields are set to None. Returns the dict and writes to OUTPUT_FILE.
    """
    log.info("Starting data fetch...")

    log.info("Computing issue metadata")
    issue = compute_issue_metadata()

    log.info("Building ticker strip")
    ticker = build_ticker()

    log.info("Building macro pulse data")
    macro_pulse = build_macro_pulse_api_data()

    log.info("Building youth unemployment data")
    youth_unemployment = build_youth_unemployment()

    brief = {
        "issue": issue,
        "ticker": ticker,
        "bottomLine": None,  # AI-generated
        "macroPulse": macro_pulse,
        "notableFlows": None,  # AI-generated
        "dealsToWatch": None,  # AI-generated
        "laborSignals": {
            "youthUnemployment": youth_unemployment,
            "aiAdoption": None,  # AI-generated
            "techJobs": None,  # AI-generated
        },
        "risks": None,  # AI-generated
        "_metadata": {
            "generated_at": datetime.now().isoformat(),
            "api_sources_used": ["world_bank", "yfinance"],
            "ai_fields_pending": [
                "bottomLine",
                "notableFlows",
                "dealsToWatch",
                "risks",
                "laborSignals.aiAdoption",
                "laborSignals.techJobs",
                "macroPulse[Saudi Arabia/Oil Revenue]",
                "macroPulse[UAE/PMI]",
                "macroPulse[UAE/FDI Inflows]",
                "macroPulse[Morocco/Tourism Revenue]",
                "macroPulse[Qatar/LNG Exports]",
                "macroPulse[Qatar/Budget Surplus]",
            ],
        },
    }

    # Write output
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(json.dumps(brief, indent=2, ensure_ascii=False))
    log.info("Partial brief written to %s", OUTPUT_FILE)

    return brief


if __name__ == "__main__":
    fetch_all()
