"""MENA Rising Pipeline — Data Collection

Fetches raw economic data from 6 sources and writes data_payload.json.
Each fetch function is independent and returns empty data on failure.
"""

import json
import logging
import time
from datetime import datetime, timedelta

import requests
import yfinance as yf

from config import (
    COUNTRIES,
    DATA_PAYLOAD_FILE,
    FRED_API_KEY,
    FRED_SERIES,
    LOGS_DIR,
    NEWS_API_KEY,
    SPARKLINE_POINTS,
    WB_INDICATORS,
    YFINANCE_TICKERS,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


# ── World Bank (macro indicators) ────────────────────────────────────────────

def _fetch_wb_indicator(indicator: str, country_iso2: str, num_years: int = 10) -> list[dict]:
    """Fetch a single World Bank indicator for one country.

    Returns list of {"year": int, "value": float} sorted ascending by year.
    """
    end_year = datetime.now().year
    start_year = end_year - num_years
    url = (
        f"https://api.worldbank.org/v2/country/{country_iso2}/indicator/{indicator}"
        f"?format=json&per_page=100&date={start_year}:{end_year}"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if len(data) < 2 or data[1] is None:
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


def _wb_latest_and_sparkline(records: list[dict]) -> dict:
    """Extract latest value, year, and sparkline from World Bank records."""
    if not records:
        return {"value": None, "year": None, "sparkline": []}
    sparkline_records = records[-SPARKLINE_POINTS:]
    sparkline = [round(r["value"], 1) for r in sparkline_records]
    latest = sparkline_records[-1]
    return {
        "value": round(latest["value"], 1),
        "year": latest["year"],
        "sparkline": sparkline,
    }


def fetch_worldbank() -> dict:
    """Fetch GDP growth, inflation, and current account balance for 8 countries.

    Returns: {"gdp_growth": {"SA": {value, year, sparkline}, ...}, ...}
    """
    indicators = {
        "gdp_growth": WB_INDICATORS["gdp_growth"],
        "inflation": WB_INDICATORS["inflation"],
        "current_account_balance": WB_INDICATORS["current_account_balance"],
    }
    result = {key: {} for key in indicators}

    for country, info in COUNTRIES.items():
        iso2 = info["iso2"]
        for key, code in indicators.items():
            records = _fetch_wb_indicator(code, iso2)
            result[key][iso2] = _wb_latest_and_sparkline(records)
            time.sleep(0.3)

    return result


# ── FRED (oil prices) ────────────────────────────────────────────────────────

def _fetch_fred_series(series_id: str, num_observations: int = 50) -> list[dict]:
    """Fetch FRED time series data."""
    if not FRED_API_KEY:
        log.warning("FRED_API_KEY not set, skipping FRED fetch for %s", series_id)
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


def _oil_from_records(records: list[dict]) -> dict:
    """Convert FRED/yfinance records to {value, change_pct, sparkline}."""
    if not records:
        return {"value": None, "change_pct": None, "sparkline": []}
    recent = records[-SPARKLINE_POINTS:]
    sparkline = [round(r["value"], 2) for r in recent]
    latest = recent[-1]["value"]
    change_pct = None
    if len(recent) >= 2 and recent[-2]["value"] != 0:
        change_pct = round(((latest - recent[-2]["value"]) / recent[-2]["value"]) * 100, 1)
    return {"value": round(latest, 2), "change_pct": change_pct, "sparkline": sparkline}


def fetch_fred() -> dict:
    """Fetch Brent crude and WTI crude from FRED.

    Falls back to yfinance BZ=F / CL=F if FRED fails.
    Returns: {"brent_crude": {value, change_pct, sparkline}, "wti_crude": {...}}
    """
    result = {}

    for name, series_id in FRED_SERIES.items():
        records = _fetch_fred_series(series_id)
        if records:
            result[name] = _oil_from_records(records)
        else:
            # Fallback to yfinance
            yf_ticker = YFINANCE_TICKERS.get("Brent Crude" if name == "brent_crude" else "WTI Crude")
            if yf_ticker:
                log.info("FRED failed for %s, falling back to yfinance %s", name, yf_ticker)
                yf_records = _fetch_yfinance_records(yf_ticker)
                result[name] = _oil_from_records(yf_records)
            else:
                result[name] = {"value": None, "change_pct": None, "sparkline": []}

    return result


# ── yfinance helpers ─────────────────────────────────────────────────────────

def _fetch_yfinance_records(ticker_symbol: str) -> list[dict]:
    """Fetch weekly closing prices from yfinance as [{date, value}]."""
    try:
        df = yf.download(ticker_symbol, period="60d", interval="1wk", progress=False)
        if df.empty:
            return []
        records = []
        for date, row in df.iterrows():
            close_val = row["Close"]
            if hasattr(close_val, "item"):
                close_val = close_val.item()
            elif hasattr(close_val, "iloc"):
                close_val = close_val.iloc[0]
            records.append({"date": str(date.date()), "value": float(close_val)})
        return records
    except Exception as e:
        log.warning("yfinance fetch failed for %s: %s", ticker_symbol, e)
        return []


# ── FX rates (yfinance) ──────────────────────────────────────────────────────

def fetch_finnhub() -> dict:
    """Fetch USD/SAR, USD/AED, USD/EGP exchange rates via yfinance.

    Finnhub's free tier doesn't support /forex/rates (403), so we use
    yfinance directly. The function name is kept for orchestrator compatibility.
    Returns: {"USD_SAR": {rate, change_pct}, "USD_AED": {...}, "USD_EGP": {...}}
    """
    pairs = {
        "USD_SAR": {"yf_ticker": "SARUSD=X", "invert": True},
        "USD_AED": {"yf_ticker": "AEDUSD=X", "invert": True},
        "USD_EGP": {"yf_ticker": "EGPUSD=X", "invert": True},
    }

    result = {}
    for pair_name, cfg in pairs.items():
        records = _fetch_yfinance_records(cfg["yf_ticker"])
        if records:
            latest = records[-1]["value"]
            if cfg["invert"] and latest != 0:
                latest = 1.0 / latest
            prev = None
            if len(records) >= 2:
                prev = records[-2]["value"]
                if cfg["invert"] and prev != 0:
                    prev = 1.0 / prev
            change_pct = None
            if prev and prev != 0:
                change_pct = round(((latest - prev) / prev) * 100, 1)
            result[pair_name] = {"rate": round(latest, 4), "change_pct": change_pct}
        else:
            result[pair_name] = {"rate": None, "change_pct": None}

    return result


# ── News API (headlines) ─────────────────────────────────────────────────────

def fetch_news() -> list[dict]:
    """Fetch top 10 MENA headlines from past 7 days via News API.

    Returns: [{"title", "source", "url", "published_at"}, ...]
    """
    if not NEWS_API_KEY:
        log.warning("NEWS_API_KEY not set, skipping news fetch")
        return []

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    query = "Saudi OR UAE OR Egypt OR Turkey OR MENA OR Gulf OR OPEC"
    url = (
        f"https://newsapi.org/v2/everything"
        f"?q={query}&from={seven_days_ago}&sortBy=relevance"
        f"&pageSize=10&language=en&apiKey={NEWS_API_KEY}"
    )
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])
        return [
            {
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", ""),
                "url": a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
            }
            for a in articles
        ]
    except Exception as e:
        log.warning("News API fetch failed: %s", e)
        return []


# ── ILO / World Bank (labor indicators) ──────────────────────────────────────

def fetch_ilo_worldbank() -> dict:
    """Fetch youth unemployment and labor force participation for 8 countries.

    Uses World Bank WDI (same API as fetch_worldbank).
    Returns: {"youth_unemployment": {"SA": {value, year}, ...}, "labor_force_participation": {...}}
    """
    indicators = {
        "youth_unemployment": WB_INDICATORS["youth_unemployment"],
        "labor_force_participation": WB_INDICATORS["labor_force_participation"],
    }
    result = {key: {} for key in indicators}

    for country, info in COUNTRIES.items():
        iso2 = info["iso2"]
        for key, code in indicators.items():
            records = _fetch_wb_indicator(code, iso2)
            if records:
                latest = records[-1]
                result[key][iso2] = {
                    "value": round(latest["value"], 1),
                    "year": latest["year"],
                }
            else:
                result[key][iso2] = {"value": None, "year": None}
            time.sleep(0.3)

    return result


# ── GDELT (risk events) ─────────────────────────────────────────────────────

def _gdelt_request(query: str, maxrecords: int, timespan: str) -> list[dict]:
    """Make a single GDELT DOC API request and parse articles."""
    url = (
        f"https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query={query}&mode=artlist&maxrecords={maxrecords}"
        f"&format=json&timespan={timespan}"
    )
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    articles = data.get("articles", [])
    results = []
    for a in articles:
        title = a.get("title", "")
        mentioned = [
            name for name in COUNTRIES.keys()
            if name.lower() in title.lower()
        ]
        results.append({
            "title": title,
            "source_url": a.get("url", ""),
            "event_type": "CONFLICT",
            "countries": mentioned,
            "date": a.get("seendate", ""),
        })
    return results


def fetch_gdelt() -> list[dict]:
    """Fetch conflict/risk events from GDELT DOC API (free, no key).

    Retries once with backoff on 429. Falls back to a narrower query
    (fewer countries, shorter timespan) if the broad query keeps failing.
    Returns: [{"title", "source_url", "event_type", "countries", "date"}, ...]
    """
    # Attempt 1: broad query — all 8 countries, risk keywords, 7-day window
    broad_query = (
        "(Saudi OR UAE OR Egypt OR Qatar OR Morocco"
        " OR Jordan OR Bahrain OR Oman OR Turkey)"
        " (conflict OR crisis OR sanctions OR protest OR military)"
    )
    try:
        return _gdelt_request(broad_query, maxrecords=20, timespan="7d")
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 429:
            log.warning("GDELT rate-limited (429), retrying in 5s with narrower query...")
        else:
            log.warning("GDELT broad query failed (%s), retrying with narrower query...", e)
    except Exception as e:
        log.warning("GDELT broad query failed (%s), retrying with narrower query...", e)

    # Wait before retry
    time.sleep(5)

    # Attempt 2: narrow query — fewer countries, shorter timespan, fewer records
    narrow_query = "(Saudi OR Egypt OR UAE) (conflict OR crisis)"
    try:
        return _gdelt_request(narrow_query, maxrecords=10, timespan="3d")
    except Exception as e:
        log.warning("GDELT narrow query also failed: %s", e)
        return []


# ── Orchestrator ─────────────────────────────────────────────────────────────

def collect_all() -> dict:
    """Orchestrate all fetchers. Writes data_payload.json and returns payload."""
    log.info("Starting data collection from 6 sources...")

    sources_succeeded = []
    sources_failed = []

    def _run(name: str, fn):
        try:
            result = fn()
            sources_succeeded.append(name)
            return result
        except Exception as e:
            log.error("Source '%s' failed: %s", name, e)
            sources_failed.append(name)
            return {} if name not in ("news", "gdelt") else []

    macro = _run("worldbank", fetch_worldbank)
    commodities = _run("fred", fetch_fred)
    fx = _run("finnhub", fetch_finnhub)
    news_headlines = _run("news", fetch_news)
    labor = _run("ilo_worldbank", fetch_ilo_worldbank)
    risk_events = _run("gdelt", fetch_gdelt)

    payload = {
        "metadata": {
            "collected_at": datetime.now().isoformat(),
            "sources_succeeded": sources_succeeded,
            "sources_failed": sources_failed,
        },
        "macro": macro,
        "commodities": commodities,
        "fx": fx,
        "news_headlines": news_headlines,
        "labor": labor,
        "risk_events": risk_events,
    }

    # Write data_payload.json
    DATA_PAYLOAD_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_PAYLOAD_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    log.info("Data payload written to %s", DATA_PAYLOAD_FILE)

    # Also write a copy to logs/ for debugging
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"{timestamp}_data_payload.json"
    log_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    log.info("Payload log written to %s", log_file)

    log.info(
        "Collection complete: %d succeeded, %d failed",
        len(sources_succeeded),
        len(sources_failed),
    )
    return payload


if __name__ == "__main__":
    collect_all()
