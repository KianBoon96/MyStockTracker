# ============================================================
# EQUITY FACTOR & MOMENTUM DASHBOARD
# ============================================================

import streamlit as st
from datetime import datetime

from config import tickers

from data import (
    download_price_data,
    get_fundamental_data,
    calculate_performance,
)

from styles import apply_global_css

from features.heatmap import show_heatmap
from features.equity_table import show_equity_table
from features.stock_detail import show_stock_detail
from features.return_volatility import show_return_volatility


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Equity Factor Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# GLOBAL CSS
# ============================================================

apply_global_css()


# ============================================================
# SIDEBAR
# ============================================================

if st.sidebar.button(
    "🔄 Refresh data"
):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title(
    "📊 Equity Factor & Momentum Dashboard"
)

st.caption(
    "Returns • Realised Volatility • "
    "Valuation • Analyst Estimates • "
    "Individual Stock Analysis"
)


# ============================================================
# DOWNLOAD PRICE DATA
# ============================================================

with st.spinner(
    "Downloading market data..."
):

    price_data = download_price_data(
        tuple(tickers)
    )


if not price_data:

    st.error(
        "No price data was returned by Yahoo Finance."
    )

    st.stop()


# ============================================================
# CALCULATE PERFORMANCE
# ============================================================

performance_df = calculate_performance(
    price_data
)


if performance_df.empty:

    st.error(
        "No performance data could be calculated."
    )

    st.stop()


# ============================================================
# DOWNLOAD FUNDAMENTAL DATA
# ============================================================

with st.spinner(
    "Loading valuation and analyst estimates..."
):

    fundamental_df = get_fundamental_data(
        tuple(tickers)
    )


# ============================================================
# TOP METRICS
# ============================================================

missing_price_tickers = [
    ticker
    for ticker in tickers
    if ticker not in price_data
]


price_data_count = (
    len(tickers)
    - len(missing_price_tickers)
)


# ============================================================
# MARKET CAP COVERAGE
# ============================================================

if (
    fundamental_df is not None
    and not fundamental_df.empty
    and "Market Cap" in fundamental_df.columns
):

    market_cap_count = (
        fundamental_df[
            "Market Cap"
        ]
        .notna()
        .sum()
    )


    missing_market_cap_tickers = (
        fundamental_df.loc[
            fundamental_df[
                "Market Cap"
            ].isna(),
            "Ticker"
        ]
        .tolist()
    )


    fundamentals_tickers = set(
        fundamental_df[
            "Ticker"
        ]
    )


    missing_market_cap_tickers += [
        ticker
        for ticker in tickers
        if ticker not in fundamentals_tickers
    ]


    missing_market_cap_tickers = sorted(
        set(
            missing_market_cap_tickers
        )
    )

else:

    market_cap_count = 0

    missing_market_cap_tickers = (
        list(tickers)
    )


# ============================================================
# DISPLAY TOP METRICS
# ============================================================

col1, col2 = st.columns(2)


with col1:

    st.metric(
        "Universe",
        len(tickers)
    )


with col2:

    st.metric(
        "Price Data",
        f"{price_data_count} / {len(tickers)}"
    )

    if missing_price_tickers:

        st.caption(
            "Missing: "
            + ", ".join(
                missing_price_tickers
            )
        )


col3, col4 = st.columns(2)


with col3:

    st.metric(
        "Market Caps",
        f"{market_cap_count} / {len(tickers)}"
    )

    if missing_market_cap_tickers:

        st.caption(
            "Missing: "
            + ", ".join(
                missing_market_cap_tickers
            )
        )


with col4:

    st.metric(
        "Updated",
        datetime.now().strftime(
            "%d %b %Y"
        )
    )


# ============================================================
# SECTION 1
# MARKET HEATMAP
# ============================================================

show_heatmap(
    performance_df,
    fundamental_df
)


# ============================================================
# SECTION 2
# EQUITY VALUATION & PERFORMANCE
# ============================================================

show_equity_table(
    performance_df,
    fundamental_df
)


# ============================================================
# SECTION 3
# INDIVIDUAL STOCK ANALYSIS
# ============================================================

show_stock_detail(
    tickers
)


# ============================================================
# SECTION 4
# RETURN VS REALISED VOLATILITY
# ============================================================

show_return_volatility(
    performance_df,
    fundamental_df
)
