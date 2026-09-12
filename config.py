# Dashboard configuration and ticker universe

import pandas as pd

tickers = [

    # --------------------------------------------------------
    # SEMICONDUCTORS
    # --------------------------------------------------------

    "ALAB",
    "AMBA",
    "AMD",
    "AVGO",
    "CRDO",
    "DRAM",
    "FORM",
    "INTC",
    "MRVL",
    "MU",
    "NVDA",
    "SKHY",
    "STM",
    "TSM",

    # --------------------------------------------------------
    # SEMICONDUCTOR EQUIPMENT
    # --------------------------------------------------------

    "ASML",
    "ICHR",
    "KLIC",
    "KLAC",
    "TER",

    # --------------------------------------------------------
    # DATA CENTER / NETWORKING / OPTICAL
    # --------------------------------------------------------

    "AAOI",
    "ANET",
    "CIEN",
    "COHR",
    "CSCO",
    "DELL",
    "GLW",
    "LITE",
    "NOK",
    "SNDK",
    "TTMI",

    # --------------------------------------------------------
    # SOFTWARE / CYBERSECURITY
    # --------------------------------------------------------

    "ADBE",
    "APP",
    "CRM",
    "CRWD",
    "DDOG",
    "INTU",
    "NET",
    "NOW",
    "PANW",
    "PATH",
    "PLTR",
    "RBRK",
    "RNG",
    "SNOW",
    "SNPS",
    "TEAM",
    "VEEV",
    "ZS",

    # --------------------------------------------------------
    # AI / CLOUD / INTERNET
    # --------------------------------------------------------

    "AMZN",
    "CRWV",
    "GOOG",
    "META",
    "MSFT",
    "NBIS",
    "NFLX",
    "UBER",

    # --------------------------------------------------------
    # CONSUMER TECHNOLOGY
    # --------------------------------------------------------

    "AAPL",
    "TSLA",

    # --------------------------------------------------------
    # FINANCIALS / FINTECH / PAYMENTS / CRYPTO
    # --------------------------------------------------------

    "AXP",
    "COIN",
    "CRCL",
    "FISV",
    "FOUR",
    "HOOD",
    "MA",
    "V",

    # --------------------------------------------------------
    # HEALTHCARE
    # --------------------------------------------------------

    "BSX",
    "ISRG",

    # --------------------------------------------------------
    # AEROSPACE / DEFENSE / SPACE / AUTONOMOUS
    # --------------------------------------------------------

    "ASTS",
    "AVAV",
    "BA",
    "LMT",
    "ONDS",
    "RKLB",
    "SPCX",
    "XAR",

    # --------------------------------------------------------
    # INDUSTRIALS
    # --------------------------------------------------------

    "AGX",
    "CAT",
    "GE",
    "VRT",

    # --------------------------------------------------------
    # POWER / UTILITIES
    # --------------------------------------------------------

    "BE",
    "CEG",
    "VST",

    # --------------------------------------------------------
    # DATA CENTER / POWER INFRASTRUCTURE
    # --------------------------------------------------------

    "APLD",
    "CORZ",
    "IREN",

    # --------------------------------------------------------
    # MATERIALS / MINING / PRECIOUS METALS
    # --------------------------------------------------------

    "AA",
    "FCX",
    "GLD",
    "NEM",
    "SCCO",
    "SLV",

    # --------------------------------------------------------
    # CONSUMER / RETAIL / RESTAURANTS
    # --------------------------------------------------------

    "AEO",
    "ANF",
    "BBY",
    "CAVA",
    "COST",
    "DPZ",
    "KO",
    "LEVI",
    "MNST",
    "RL",
    "SHAK",
    "TGT",
    "TOST",
    "VSXY",
    "WMT",
]


# Remove duplicates
tickers = list(dict.fromkeys(tickers))


# ============================================================
# CATEGORY MAP
# ============================================================

groups = {

    "Semiconductors": [
        "ALAB",
        "AMBA",
        "AMD",
        "AVGO",
        "CRDO",
        "DRAM",
        "FORM",
        "INTC",
        "MRVL",
        "MU",
        "NVDA",
        "SKHY",
        "STM",
        "TSM",
    ],

    "Semiconductor Equipment": [
        "ASML",
        "ICHR",
        "KLIC",
        "KLAC",
        "TER",
    ],

    "Data Center / Networking / Optical": [
        "AAOI",
        "ANET",
        "CIEN",
        "COHR",
        "CSCO",
        "DELL",
        "GLW",
        "LITE",
        "NOK",
        "SNDK",
        "TTMI",
    ],

    "Software / Cybersecurity": [
        "ADBE",
        "APP",
        "CRM",
        "CRWD",
        "DDOG",
        "INTU",
        "NET",
        "NOW",
        "PANW",
        "PATH",
        "PLTR",
        "RBRK",
        "RNG",
        "SNOW",
        "SNPS",
        "TEAM",
        "VEEV",
        "ZS",
    ],

    "AI / Cloud / Internet": [
        "AMZN",
        "CRWV",
        "GOOG",
        "META",
        "MSFT",
        "NBIS",
        "NFLX",
        "UBER",
    ],

    "Consumer Technology": [
        "AAPL",
        "TSLA",
    ],

    "Financials / Fintech / Payments": [
        "AXP",
        "COIN",
        "CRCL",
        "FISV",
        "FOUR",
        "HOOD",
        "MA",
        "V",
    ],

    "Healthcare": [
        "BSX",
        "ISRG",
    ],

    "Aerospace / Defense / Space / Autonomous": [
        "ASTS",
        "AVAV",
        "BA",
        "LMT",
        "ONDS",
        "RKLB",
        "SPCX",
        "XAR",
    ],

    "Industrials": [
        "AGX",
        "CAT",
        "GE",
        "VRT",
    ],

    "Power / Utilities": [
        "BE",
        "CEG",
        "VST",
    ],

    "Data Center / Power Infrastructure": [
        "APLD",
        "CORZ",
        "IREN",
    ],

    "Materials / Mining / Precious Metals": [
        "AA",
        "FCX",
        "GLD",
        "NEM",
        "SCCO",
        "SLV",
    ],

    "Consumer / Retail / Restaurants": [
        "AEO",
        "ANF",
        "BBY",
        "CAVA",
        "COST",
        "DPZ",
        "KO",
        "LEVI",
        "MNST",
        "RL",
        "SHAK",
        "TGT",
        "TOST",
        "VSXY",
        "WMT",
    ],
}


category_map = {}

for category, symbols in groups.items():

    for symbol in symbols:

        category_map[symbol] = category


# ============================================================
# YAHOO FINANCE SYMBOL HANDLING
# ============================================================

# All tickers in the current universe use their current
# Yahoo Finance symbols directly.
YF_ALIASES = {}


def yf_symbol(ticker):
    """
    Return the Yahoo Finance symbol for a dashboard ticker.

    If an alias is added in the future, it will be used.
    Otherwise, the original ticker is returned unchanged.
    """
    return YF_ALIASES.get(ticker, ticker)

# ============================================================
# TIME WINDOWS
# ============================================================

RETURN_WINDOWS = {

    "Daily": 1,

    "Weekly": 5,

    "Monthly": 21,

    "Semi-Annual": 126,

    "Annual": 252,
}


VOL_WINDOWS = {

    "Monthly": 21,

    "Semi-Annual": 126,

    "Annual": 252,
}


# Formatting helpers shared across features
def format_market_cap(value):

    if pd.isna(value):

        return "N/A"

    return f"{value / 1e9:,.1f} B"


def format_billions(value):

    if pd.isna(value):

        return "N/A"

    return f"{value / 1e9:,.1f} B"


def format_percent(value):

    if pd.isna(value):

        return "N/A"

    return f"{value:+.2%}"


def format_number(value):

    if pd.isna(value):

        return "N/A"

    return f"{value:.2f}"
