"""MENA Rising Pipeline — Configuration & Constants"""

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────────────────
PIPELINE_DIR = Path(__file__).resolve().parent

# Load .env before reading any env vars. override=False means
# already-set env vars (e.g. from CI) are not overwritten.
load_dotenv(PIPELINE_DIR / ".env", override=False)
PROJECT_ROOT = PIPELINE_DIR.parent
OUTPUT_FILE = PROJECT_ROOT / "public" / "data" / "latest_brief.json"
DATA_PAYLOAD_FILE = PIPELINE_DIR / "data_payload.json"
LOGS_DIR = PIPELINE_DIR / "logs"

# ── API Keys ───────────────────────────────────────────────────────────────────
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
FINNHUB_API_KEY = os.environ.get("FINNHUB_API_KEY", "")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID", "")

# ── Country Map ────────────────────────────────────────────────────────────────
COUNTRIES = {
    "Saudi Arabia": {"iso2": "SA", "flag": "\U0001f1f8\U0001f1e6"},
    "UAE":          {"iso2": "AE", "flag": "\U0001f1e6\U0001f1ea"},
    "Egypt":        {"iso2": "EG", "flag": "\U0001f1ea\U0001f1ec"},
    "Qatar":        {"iso2": "QA", "flag": "\U0001f1f6\U0001f1e6"},
    "Morocco":      {"iso2": "MA", "flag": "\U0001f1f2\U0001f1e6"},
    "Jordan":       {"iso2": "JO", "flag": "\U0001f1ef\U0001f1f4"},
    "Bahrain":      {"iso2": "BH", "flag": "\U0001f1e7\U0001f1ed"},
    "Oman":         {"iso2": "OM", "flag": "\U0001f1f4\U0001f1f2"},
    "Turkey":       {"iso2": "TR", "flag": "\U0001f1f9\U0001f1f7"},
}

# ── yfinance Tickers ──────────────────────────────────────────────────────────
# EGPUSD=X returns USD-per-EGP (~0.02). Frontend expects EGP-per-USD (~50).
# Tickers in INVERT_TICKERS will have their values inverted (1/value).
YFINANCE_TICKERS = {
    "EGP/USD":     "EGPUSD=X",
    "SAR/USD":     "SARUSD=X",
    "AED/USD":     "AEDUSD=X",
    "Brent Crude": "BZ=F",
    "WTI Crude":   "CL=F",
    "TRY/USD":     "TRYUSD=X",
}
INVERT_TICKERS = {"EGP/USD", "SAR/USD", "AED/USD", "TRY/USD"}

# ── World Bank Indicators ─────────────────────────────────────────────────────
WB_INDICATORS = {
    "inflation":                "FP.CPI.TOTL.ZG",
    "gdp_growth":               "NY.GDP.MKTP.KD.ZG",
    "youth_unemployment":       "SL.UEM.1524.ZS",
    "current_account_balance":  "BN.CAB.XOKA.GD.ZS",
    "labor_force_participation": "SL.TLF.CACT.ZS",
}

# ── FRED Series ─────────────────────────────────────────────────────────────
FRED_SERIES = {
    "brent_crude": "DCOILBRENTEU",
    "wti_crude":   "DCOILWTICO",
}

# ── Sparkline Configuration ───────────────────────────────────────────────────
SPARKLINE_POINTS = 6

# ── Macro Pulse Metric Definitions ────────────────────────────────────────────
# source: "wb_inflation", "wb_gdp_growth", "yf_EGP/USD", or "ai_generated"
MACRO_PULSE_METRICS = [
    {"country": "Egypt",        "metric": "Inflation Rate", "unit": "%",      "source": "wb_inflation"},
    {"country": "Egypt",        "metric": "EGP/USD",        "unit": "",       "source": "yf_EGP/USD"},
    {"country": "Saudi Arabia", "metric": "GDP Growth",     "unit": "%",      "source": "wb_gdp_growth"},
    {"country": "Saudi Arabia", "metric": "Oil Revenue",    "unit": "$B",     "source": "ai_generated"},
    {"country": "UAE",          "metric": "PMI",            "unit": "",       "source": "ai_generated"},
    {"country": "UAE",          "metric": "FDI Inflows",    "unit": "$B",     "source": "ai_generated"},
    {"country": "Morocco",      "metric": "CPI",            "unit": "%",      "source": "wb_inflation"},
    {"country": "Morocco",      "metric": "Tourism Revenue","unit": "%",      "source": "ai_generated"},
    {"country": "Turkey",       "metric": "Inflation",      "unit": "%",      "source": "wb_inflation"},
    {"country": "Turkey",       "metric": "Lira/USD",       "unit": "",       "source": "yf_TRY/USD"},
    {"country": "Qatar",        "metric": "LNG Exports",    "unit": "%",      "source": "ai_generated"},
    {"country": "Qatar",        "metric": "Budget Surplus",  "unit": "% GDP", "source": "ai_generated"},
]
