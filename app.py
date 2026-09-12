# ============================================================
# EQUITY FACTOR & MOMENTUM DASHBOARD
# Modular Streamlit application
# ============================================================

import streamlit as st
from datetime import datetime

from config import tickers
from data import download_price_data, get_fundamental_data, calculate_performance
from styles import apply_global_css
from features.heatmap import show_heatmap
from features.equity_table import show_equity_table
from features.return_volatility import show_return_volatility


st.set_page_config(
    page_title="Equity Factor Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

apply_global_css()

# Sidebar
st.sidebar.title("📊 Equity Dashboard")
st.sidebar.write(f"**{len(tickers)} unique tickers**")
st.sidebar.divider()

# Header
st.title("📊 Equity Factor & Momentum Dashboard")
st.caption(
    "Returns • Realised Volatility • Market Capitalisation • Forward Analyst Estimates"
)

# Data loading
with st.spinner("Downloading market data..."):
    price_data = download_price_data(tuple(tickers))

if not price_data:
    st.error("No price data was returned by Yahoo Finance.")
    st.stop()

performance_df = calculate_performance(price_data)
if performance_df.empty:
    st.error("No performance data could be calculated.")
    st.stop()

with st.spinner("Loading market capitalisation and analyst estimates..."):
    fundamental_df = get_fundamental_data(tuple(tickers))

# Top metrics
# ============================================================
# TOP METRICS
# ============================================================

# Tickers missing price data
missing_price_tickers = [
    ticker for ticker in tickers
    if ticker not in price_data
]

# Tickers missing market cap
missing_market_cap_tickers = []

if (
    fundamental_df is not None
    and not fundamental_df.empty
    and "Market Cap" in fundamental_df.columns
):
    market_cap_count = fundamental_df["Market Cap"].notna().sum()

    missing_market_cap_tickers = (
        fundamental_df.loc[
            fundamental_df["Market Cap"].isna(),
            "Ticker"
        ]
        .tolist()
    )
else:
    market_cap_count = 0
    missing_market_cap_tickers = tickers.copy()


col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Universe",
        len(tickers)
    )

with col2:
    st.metric(
        "Price Data",
        f"{len(price_data)} / {len(tickers)}"
    )

    if missing_price_tickers:
        st.caption(
            "Missing: "
            + ", ".join(missing_price_tickers)
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
            + ", ".join(missing_market_cap_tickers)
        )


with col4:
    st.metric(
        "Updated",
        datetime.now().strftime("%d %b %Y")
    )

# Feature modules
show_heatmap(performance_df, fundamental_df)
show_equity_table(performance_df, fundamental_df)
show_return_volatility(performance_df, fundamental_df)
