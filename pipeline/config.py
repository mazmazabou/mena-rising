"""MENA Rising Pipeline — Configuration & Constants"""

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PIPELINE_DIR.parent
OUTPUT_FILE = PROJECT_ROOT / "public" / "data" / "latest_brief.json"

# ── API Keys ───────────────────────────────────────────────────────────────────
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# ── Country Map ────────────────────────────────────────────────────────────────
COUNTRIES = {
    "Egypt":        {"iso2": "EG", "flag": "\U0001f1ea\U0001f1ec"},
    "Saudi Arabia": {"iso2": "SA", "flag": "\U0001f1f8\U0001f1e6"},
    "UAE":          {"iso2": "AE", "flag": "\U0001f1e6\U0001f1ea"},
    "Morocco":      {"iso2": "MA", "flag": "\U0001f1f2\U0001f1e6"},
    "Turkey":       {"iso2": "TR", "flag": "\U0001f1f9\U0001f1f7"},
    "Qatar":        {"iso2": "QA", "flag": "\U0001f1f6\U0001f1e6"},
}

# ── yfinance Tickers ──────────────────────────────────────────────────────────
# EGPUSD=X returns USD-per-EGP (~0.02). Frontend expects EGP-per-USD (~50).
# Tickers in INVERT_TICKERS will have their values inverted (1/value).
YFINANCE_TICKERS = {
    "EGP/USD":     "EGPUSD=X",
    "SAR/USD":     "SARUSD=X",
    "TRY/USD":     "TRYUSD=X",
    "AED/USD":     "AEDUSD=X",
    "Brent Crude": "BZ=F",
}
INVERT_TICKERS = {"EGP/USD", "SAR/USD", "TRY/USD", "AED/USD"}

# ── World Bank Indicators ─────────────────────────────────────────────────────
WB_INDICATORS = {
    "inflation":          "FP.CPI.TOTL.ZG",
    "gdp_growth":         "NY.GDP.MKTP.KD.ZG",
    "youth_unemployment": "SL.UEM.1524.ZS",
}

# ── FRED Series (fallback for oil) ────────────────────────────────────────────
FRED_SERIES = {
    "brent_crude": "DCOILBRENTEU",
}

# ── Sparkline Configuration ───────────────────────────────────────────────────
SPARKLINE_POINTS = 6

# ── Macro Pulse Metric Definitions ────────────────────────────────────────────
# source: "wb_inflation", "wb_gdp_growth", "yf_EGP/USD", "yf_TRY/USD", or "ai_generated"
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
