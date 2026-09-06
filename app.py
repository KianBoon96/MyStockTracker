# ============================================================
# EQUITY FACTOR DASHBOARD
# Streamlit + yfinance
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Equity Factor Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    .main {
        background-color: #0e1117;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        color: #f5f5f5;
    }

    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }

    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 10px;
        border-radius: 8px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# TICKER UNIVERSE
# ============================================================

tickers = [

    # --------------------------------------------------------
    # SEMICONDUCTORS
    # --------------------------------------------------------
    "ALAB", "AMBA", "AMD", "AVGO", "CRDO",
    "DRAM", "FORM", "INTC", "MRVL", "MU",
    "NVDA", "SKHY", "STM", "TSM",

    # --------------------------------------------------------
    # SEMICONDUCTOR EQUIPMENT
    # --------------------------------------------------------
    "ASML", "ICHR", "KLIC", "KLAC", "TER",

    # --------------------------------------------------------
    # DATA CENTER / NETWORKING / OPTICAL
    # --------------------------------------------------------
    "AAOI", "ANET", "CIEN", "COHR", "CSCO",
    "DELL", "GLW", "LITE", "NOK", "SNDK",
    "TTMI",

    # --------------------------------------------------------
    # SOFTWARE / CYBERSECURITY
    # --------------------------------------------------------
    "ADBE", "APP", "CRM", "CRWD", "DDOG",
    "INTU", "NET", "NOW", "PANW", "PATH",
    "PLTR", "RBRK", "RNG", "SNOW", "SNPS",
    "TEAM", "VEEV", "ZS",

    # --------------------------------------------------------
    # AI / CLOUD / INTERNET
    # --------------------------------------------------------
    "AMZN", "CRWV", "GOOG", "META",
    "MSFT", "NBIS", "NFLX", "UBER",

    # --------------------------------------------------------
    # CONSUMER TECHNOLOGY
    # --------------------------------------------------------
    "AAPL", "TSLA",

    # --------------------------------------------------------
    # FINANCIAL / PAYMENTS / FINTECH / CRYPTO
    # --------------------------------------------------------
    "AXP", "COIN", "CRCL", "FISV",
    "FOUR", "HOOD", "MA", "V",

    # --------------------------------------------------------
    # HEALTHCARE
    # --------------------------------------------------------
    "BSX", "ISRG",

    # --------------------------------------------------------
    # AEROSPACE / DEFENSE / SPACE / AUTONOMOUS
    # --------------------------------------------------------
    "ASTS", "AVAV", "BA", "LMT",
    "ONDS", "RKLB", "SPCX", "XAR",

    # --------------------------------------------------------
    # POWER / UTILITIES
    # --------------------------------------------------------
    "BE", "CEG", "VST",

    # --------------------------------------------------------
    # DATA CENTER / POWER INFRASTRUCTURE
    # --------------------------------------------------------
    "APLD", "CORZ", "IREN", "VRT",

    # --------------------------------------------------------
    # INDUSTRIALS
    # --------------------------------------------------------
    "AGX", "CAT", "GE",

    # --------------------------------------------------------
    # MATERIALS / MINING / PRECIOUS METALS
    # --------------------------------------------------------
    "AA", "FCX", "GLD", "NEM", "SCCO", "SLV",

    # --------------------------------------------------------
    # CONSUMER / RETAIL / RESTAURANTS / APPAREL
    # --------------------------------------------------------
    "AEO", "ANF", "BBY", "CAVA", "COST",
    "DPZ", "KO", "LEVI", "MNST", "RL",
    "SHAK", "TGT", "TOST", "VSXY", "WMT",

    # --------------------------------------------------------
    # STATE STREET / SPDR SECTOR ETFs
    # --------------------------------------------------------
    "XLB", "XLC", "XLE", "XLF", "XLI",
    "XLK", "XLP", "XLRE", "XLU", "XLV",
    "XLY",

    # --------------------------------------------------------
    # BOND
    # --------------------------------------------------------
    "TLT",
]

tickers = list(dict.fromkeys(tickers))


# ============================================================
# CATEGORY MAP
# ============================================================

category_map = {}

groups = {

    "Semiconductors": [
        "ALAB", "AMBA", "AMD", "AVGO", "CRDO", "DRAM",
        "FORM", "INTC", "MRVL", "MU", "NVDA", "SKHY",
        "STM", "TSM"
    ],

    "Semiconductor Equipment": [
        "ASML", "ICHR", "KLIC", "KLAC", "TER"
    ],

    "Data Center / Networking": [
        "AAOI", "ANET", "CIEN", "COHR", "CSCO",
        "DELL", "GLW", "LITE", "NOK", "SNDK", "TTMI"
    ],

    "Software / Cybersecurity": [
        "ADBE", "APP", "CRM", "CRWD", "DDOG", "INTU",
        "NET", "NOW", "PANW", "PATH", "PLTR", "RBRK",
        "RNG", "SNOW", "SNPS", "TEAM", "VEEV", "ZS"
    ],

    "AI / Cloud / Internet": [
        "AMZN", "CRWV", "GOOG", "META",
        "MSFT", "NBIS", "NFLX", "UBER"
    ],

    "Consumer Technology": [
        "AAPL", "TSLA"
    ],

    "Financials / Fintech": [
        "AXP", "COIN", "CRCL", "FISV",
        "FOUR", "HOOD", "MA", "V"
    ],

    "Healthcare": [
        "BSX", "ISRG"
    ],

    "Aerospace / Defense / Space": [
        "ASTS", "AVAV", "BA", "LMT",
        "ONDS", "RKLB", "SPCX", "XAR"
    ],

    "Power / Utilities": [
        "BE", "CEG", "VST"
    ],

    "Data Center / Power Infrastructure": [
        "APLD", "CORZ", "IREN", "VRT"
    ],

    "Industrials": [
        "AGX", "CAT", "GE"
    ],

    "Materials / Mining / Precious Metals": [
        "AA", "FCX", "GLD", "NEM", "SCCO", "SLV"
    ],

    "Consumer / Retail / Restaurants": [
        "AEO", "ANF", "BBY", "CAVA", "COST",
        "DPZ", "KO", "LEVI", "MNST", "RL",
        "SHAK", "TGT", "TOST", "VSXY", "WMT"
    ],

    "Sector ETFs": [
        "XLB", "XLC", "XLE", "XLF", "XLI",
        "XLK", "XLP", "XLRE", "XLU", "XLV", "XLY"
    ],

    "Bonds": [
        "TLT"
    ]
}

for category, names in groups.items():
    for ticker in names:
        category_map[ticker] = category


# ============================================================
# YAHOO FINANCE TICKER ALIASES
# ============================================================
#
# These allow your displayed ticker to remain unchanged while
# using the Yahoo Finance symbol where necessary.
#
# SK hynix trades in Korea.
# Victoria's Secret is VSCO on Yahoo Finance.
#
# Other symbols that Yahoo cannot resolve will simply be
# marked unavailable rather than crashing the application.
# ============================================================

yf_aliases = {
    "SKHY": "000660.KS",
    "VSXY": "VSCO",
}


def yf_symbol(ticker):
    return yf_aliases.get(ticker, ticker)


# ============================================================
# TIMEFRAME DEFINITIONS
# ============================================================

TIMEFRAMES = {
    "Daily": 1,
    "Weekly": 5,
    "Monthly": 21,
    "Semi-Annual": 126,
    "Annual": 252
}

ANNUALIZATION = 252


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def format_market_cap(value):

    if pd.isna(value):
        return "N/A"

    if value >= 1e12:
        return f"${value / 1e12:.2f}T"

    if value >= 1e9:
        return f"${value / 1e9:.2f}B"

    if value >= 1e6:
        return f"${value / 1e6:.2f}M"

    return f"${value:,.0f}"


def get_return(prices, days):

    if prices is None or len(prices) < days + 1:
        return np.nan

    try:
        return prices.iloc[-1] / prices.iloc[-days - 1] - 1
    except Exception:
        return np.nan


def get_realized_volatility(returns, days):

    if returns is None or len(returns) < days:
        return np.nan

    window = returns.iloc[-days:]

    if len(window) < 2:
        return np.nan

    # Annualised realized volatility
    return window.std() * np.sqrt(ANNUALIZATION)


# ============================================================
# DOWNLOAD PRICE DATA
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def download_price_data(ticker_list):

    result = {}

    def download_one(ticker):

        symbol = yf_symbol(ticker)

        try:

            data = yf.download(
                symbol,
                period="2y",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False
            )

            if data is None or data.empty:
                return ticker, None

            if isinstance(data.columns, pd.MultiIndex):
                close = data["Close"].iloc[:, 0]
            else:
                close = data["Close"]

            close = close.dropna()

            if len(close) < 10:
                return ticker, None

            return ticker, close

        except Exception:
            return ticker, None

    with ThreadPoolExecutor(max_workers=8) as executor:

        futures = {
            executor.submit(download_one, ticker): ticker
            for ticker in ticker_list
        }

        for future in as_completed(futures):

            ticker, prices = future.result()

            if prices is not None:
                result[ticker] = prices

    return result


# ============================================================
# FUNDAMENTAL DATA
# ============================================================

@st.cache_data(ttl=21600, show_spinner=False)
def get_fundamental_data(ticker_list):

    rows = []

    def get_one(ticker):

        symbol = yf_symbol(ticker)

        result = {
            "Ticker": ticker,
            "Category": category_map.get(ticker, "Other"),
            "Market Cap": np.nan,
            "EPS Next Year": np.nan,
            "EPS Following Year": np.nan,
            "Revenue Next Year": np.nan,
            "Revenue Following Year": np.nan,
            "EPS Growth Next Year": np.nan,
            "EPS Growth Following Year": np.nan,
            "Revenue Growth Next Year": np.nan,
            "Revenue Growth Following Year": np.nan,
        }

        try:

            tk = yf.Ticker(symbol)

            # --------------------------------------------
            # INFO
            # --------------------------------------------

            try:
                info = tk.info

                market_cap = info.get("marketCap")

                if market_cap is not None:
                    result["Market Cap"] = market_cap

            except Exception:
                info = {}

            # --------------------------------------------
            # ANALYST ESTIMATES
            # --------------------------------------------

            try:

                estimates = tk.get_earnings_estimate()

                if estimates is not None and not estimates.empty:

                    # Yahoo normally provides:
                    #
                    # 0q
                    # +1q
                    # 0y
                    # +1y
                    # +2y

                    if "+1y" in estimates.index:
                        result["EPS Next Year"] = estimates.loc["+1y"].get(
                            "avg", np.nan
                        )

                    if "+2y" in estimates.index:
                        result["EPS Following Year"] = estimates.loc["+2y"].get(
                            "avg", np.nan
                        )

                    if "+1y" in estimates.index:
                        result["EPS Growth Next Year"] = estimates.loc["+1y"].get(
                            "growth", np.nan
                        )

                    if "+2y" in estimates.index:
                        result["EPS Growth Following Year"] = estimates.loc["+2y"].get(
                            "growth", np.nan
                        )

            except Exception:
                pass

            # --------------------------------------------
            # REVENUE ESTIMATES
            # --------------------------------------------

            try:

                revenue = tk.get_revenue_estimate()

                if revenue is not None and not revenue.empty:

                    if "+1y" in revenue.index:

                        result["Revenue Next Year"] = revenue.loc["+1y"].get(
                            "avg", np.nan
                        )

                        result["Revenue Growth Next Year"] = revenue.loc["+1y"].get(
                            "growth", np.nan
                        )

                    if "+2y" in revenue.index:

                        result["Revenue Following Year"] = revenue.loc["+2y"].get(
                            "avg", np.nan
                        )

                        result["Revenue Growth Following Year"] = revenue.loc["+2y"].get(
                            "growth", np.nan
                        )

            except Exception:
                pass

        except Exception:
            pass

        return result

    with ThreadPoolExecutor(max_workers=6) as executor:

        futures = {
            executor.submit(get_one, ticker): ticker
            for ticker in ticker_list
        }

        for future in as_completed(futures):

            try:
                rows.append(future.result())
            except Exception:
                pass

    return pd.DataFrame(rows)


# ============================================================
# CALCULATE PERFORMANCE
# ============================================================

def calculate_performance(price_data):

    rows = []

    for ticker, prices in price_data.items():

        returns = prices.pct_change().dropna()

        row = {
            "Ticker": ticker,
            "Category": category_map.get(ticker, "Other"),
        }

        for name, days in TIMEFRAMES.items():

            row[f"{name} Return"] = get_return(prices, days)

            row[f"{name} Volatility"] = get_realized_volatility(
                returns,
                days
            )

        rows.append(row)

    return pd.DataFrame(rows)


# ============================================================
# HEATMAP DATA
# ============================================================

def create_heatmap_dataframe(performance_df, fundamental_df, timeframe):

    return_df = performance_df[
        ["Ticker", f"{timeframe} Return"]
    ].copy()

    if fundamental_df is not None and not fundamental_df.empty:

        return_df = return_df.merge(
            fundamental_df[["Ticker", "Market Cap"]],
            on="Ticker",
            how="left"
        )

    else:

        return_df["Market Cap"] = np.nan

    return_df["Return"] = return_df[f"{timeframe} Return"]

    return return_df[
        ["Ticker", "Return", "Market Cap"]
    ].dropna(subset=["Return"])


# ============================================================
# HEATMAP
# ============================================================

def render_heatmap(performance_df, fundamental_df, timeframe):

    df = create_heatmap_dataframe(
        performance_df,
        fundamental_df,
        timeframe
    )

    if df.empty:
        st.warning("No performance data available.")
        return

    df = df.sort_values("Return", ascending=False)

    # --------------------------------------------------------
    # Grid dimensions
    # --------------------------------------------------------

    n = len(df)

    cols = 8
    rows = int(np.ceil(n / cols))

    heatmap_matrix = np.full((rows, cols), np.nan)
    ticker_matrix = np.full((rows, cols), "", dtype=object)

    cap_matrix = np.full((rows, cols), "", dtype=object)

    for i, (_, row) in enumerate(df.iterrows()):

        r = i // cols
        c = i % cols

        heatmap_matrix[r, c] = row["Return"]
        ticker_matrix[r, c] = row["Ticker"]

        cap_matrix[r, c] = format_market_cap(
            row["Market Cap"]
        )

    fig = go.Figure(
        data=go.Heatmap(
            z=heatmap_matrix,
            x=list(range(cols)),
            y=list(range(rows)),
            colorscale=[
                [0.0, "#8B0000"],
                [0.25, "#C0392B"],
                [0.5, "#2C3E50"],
                [0.75, "#27AE60"],
                [1.0, "#00FF88"]
            ],
            zmid=0,
            text=ticker_matrix,
            customdata=cap_matrix,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Return: %{z:.2%}<br>"
                "Market Cap: %{customdata}"
                "<extra></extra>"
            ),
            colorbar=dict(
                title="Return"
            )
        )
    )

    # --------------------------------------------------------
    # Add ticker + market cap text
    # --------------------------------------------------------

    for r in range(rows):

        for c in range(cols):

            if ticker_matrix[r, c] != "":

                ret = heatmap_matrix[r, c]

                fig.add_annotation(
                    x=c,
                    y=r,
                    text=(
                        f"<b>{ticker_matrix[r,c]}</b>"
                        f"<br>"
                        f"{ret:.1%}"
                        f"<br>"
                        f"<span style='font-size:10px'>"
                        f"{cap_matrix[r,c]}"
                        f"</span>"
                    ),
                    showarrow=False,
                    font=dict(
                        color="white",
                        size=11
                    )
                )

    fig.update_layout(
        title=f"{timeframe} Return — Market Cap shown below return",
        height=max(500, rows * 85),
        xaxis=dict(
            showticklabels=False,
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            autorange="reversed"
        ),
        margin=dict(
            l=10,
            r=10,
            t=60,
            b=10
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# FORMAT TABLE
# ============================================================

def prepare_table(performance_df, fundamental_df):

    df = performance_df.copy()

    if fundamental_df is not None and not fundamental_df.empty:

        df = df.merge(
            fundamental_df,
            on=["Ticker", "Category"],
            how="left"
        )

    # --------------------------------------------------------
    # Column order
    # --------------------------------------------------------

    desired_columns = [

        "Ticker",
        "Category",
        "Market Cap",

        "Daily Return",
        "Weekly Return",
        "Monthly Return",
        "Semi-Annual Return",
        "Annual Return",

        "Daily Volatility",
        "Weekly Volatility",
        "Monthly Volatility",
        "Semi-Annual Volatility",
        "Annual Volatility",

        "EPS Next Year",
        "EPS Following Year",

        "Revenue Next Year",
        "Revenue Following Year",

        "EPS Growth Next Year",
        "EPS Growth Following Year",

        "Revenue Growth Next Year",
        "Revenue Growth Following Year",
    ]

    existing = [
        col for col in desired_columns
        if col in df.columns
    ]

    return df[existing]


# ============================================================
# TABLE FILTERS
# ============================================================

def apply_filters(df):

    st.markdown("### Filters")

    c1, c2, c3 = st.columns([1, 1, 2])

    with c1:

        categories = sorted(
            df["Category"].dropna().unique()
        )

        selected_categories = st.multiselect(
            "Category",
            categories,
            default=categories
        )

    with c2:

        selected_tickers = st.multiselect(
            "Ticker",
            sorted(df["Ticker"].unique()),
            default=[]
        )

    with c3:

        search = st.text_input(
            "Search ticker",
            placeholder="e.g. NVDA, AMD, PLTR..."
        )

    filtered = df.copy()

    if selected_categories:

        filtered = filtered[
            filtered["Category"].isin(selected_categories)
        ]

    if selected_tickers:

        filtered = filtered[
            filtered["Ticker"].isin(selected_tickers)
        ]

    if search:

        filtered = filtered[
            filtered["Ticker"].str.contains(
                search.upper(),
                na=False
            )
        ]

    # --------------------------------------------------------
    # Numeric filters
    # --------------------------------------------------------

    with st.expander("Advanced numeric filters"):

        numeric_columns = [
            "Market Cap",
            "Daily Return",
            "Weekly Return",
            "Monthly Return",
            "Semi-Annual Return",
            "Annual Return",
            "Daily Volatility",
            "Weekly Volatility",
            "Monthly Volatility",
            "Semi-Annual Volatility",
            "Annual Volatility",
        ]

        available_numeric = [
            c for c in numeric_columns
            if c in filtered.columns
        ]

        selected_metric = st.selectbox(
            "Filter metric",
            available_numeric
        )

        series = filtered[selected_metric].dropna()

        if not series.empty:

            minimum = float(series.min())
            maximum = float(series.max())

            if minimum < maximum:

                lower, upper = st.slider(
                    f"{selected_metric} range",
                    min_value=minimum,
                    max_value=maximum,
                    value=(minimum, maximum)
                )

                filtered = filtered[
                    filtered[selected_metric].between(
                        lower,
                        upper
                    )
                ]

    return filtered


# ============================================================
# RETURN / VOLATILITY TABLE
# ============================================================

def render_return_volatility_table(
    performance_df,
    fundamental_df,
    timeframe
):

    return_col = f"{timeframe} Return"
    vol_col = f"{timeframe} Volatility"

    df = performance_df[
        [
            "Ticker",
            "Category",
            return_col,
            vol_col
        ]
    ].copy()

    if fundamental_df is not None and not fundamental_df.empty:

        df = df.merge(
            fundamental_df[
                ["Ticker", "Market Cap"]
            ],
            on="Ticker",
            how="left"
        )

    else:

        df["Market Cap"] = np.nan

    df["Return / Volatility"] = (
        df[return_col] /
        df[vol_col].replace(0, np.nan)
    )

    df = df.sort_values(
        "Return / Volatility",
        ascending=False
    )

    display_df = df.rename(
        columns={
            return_col: "Return",
            vol_col: "Realised Volatility"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={

            "Return": st.column_config.NumberColumn(
                "Return",
                format="%.2%"
            ),

            "Realised Volatility": st.column_config.NumberColumn(
                "Realised Volatility",
                format="%.2%"
            ),

            "Return / Volatility": st.column_config.NumberColumn(
                "Return / Volatility",
                format="%.2f"
            ),

            "Market Cap": st.column_config.NumberColumn(
                "Market Cap",
                format="$%.0f"
            )
        }
    )

    return df


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📊 Equity Dashboard")

st.sidebar.markdown(
    "### Universe"
)

st.sidebar.write(
    f"**{len(tickers)} tickers**"
)

st.sidebar.divider()

st.sidebar.markdown(
    """
### Data

Prices: Yahoo Finance  
Frequency: Daily  
Volatility: Annualised realised volatility  
Returns: Price returns
"""
)

if st.sidebar.button("🔄 Refresh data"):

    st.cache_data.clear()

    st.rerun()


# ============================================================
# HEADER
# ============================================================

st.title("📊 Equity Factor & Momentum Dashboard")

st.caption(
    "Performance • Realised Volatility • Market Capitalisation • "
    "Analyst Estimates"
)


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Downloading market data..."):

    price_data = download_price_data(
        tuple(tickers)
    )


if not price_data:

    st.error(
        "Yahoo Finance did not return any price data. "
        "Please try refreshing."
    )

    st.stop()


# ============================================================
# PERFORMANCE
# ============================================================

performance_df = calculate_performance(
    price_data
)


# ============================================================
# FUNDAMENTALS
# ============================================================

with st.spinner(
    "Loading market capitalisation and analyst estimates..."
):

    fundamental_df = get_fundamental_data(
        tuple(tickers)
    )


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "Universe",
        f"{len(tickers)}"
    )

with col2:

    st.metric(
        "Price Data",
        f"{len(price_data)}"
    )

with col3:

    available_fundamentals = (
        fundamental_df["Market Cap"]
        .notna()
        .sum()
        if not fundamental_df.empty
        else 0
    )

    st.metric(
        "Market Caps",
        f"{available_fundamentals}"
    )

with col4:

    st.metric(
        "Updated",
        datetime.now().strftime("%d %b %Y")
    )


# ============================================================
# SECTION 1 — HEATMAP
# ============================================================

st.divider()

st.header("1. Performance Heat Map")

heatmap_timeframe = st.radio(
    "Select timeframe",
    [
        "Daily",
        "Weekly",
        "Monthly",
        "Semi-Annual",
        "Annual"
    ],
    horizontal=True,
    key="heatmap_timeframe"
)

render_heatmap(
    performance_df,
    fundamental_df,
    heatmap_timeframe
)


# ============================================================
# SECTION 2 — MAIN TABLE
# ============================================================

st.divider()

st.header("2. Equity Returns, Volatility & Fundamentals")

st.caption(
    "Click any column header to sort. Use the filters below "
    "to narrow the universe."
)

main_table = prepare_table(
    performance_df,
    fundamental_df
)

filtered_table = apply_filters(
    main_table
)


# ------------------------------------------------------------
# FORMAT MAIN TABLE
# ------------------------------------------------------------

percent_columns = [

    "Daily Return",
    "Weekly Return",
    "Monthly Return",
    "Semi-Annual Return",
    "Annual Return",

    "Daily Volatility",
    "Weekly Volatility",
    "Monthly Volatility",
    "Semi-Annual Volatility",
    "Annual Volatility",

    "EPS Growth Next Year",
    "EPS Growth Following Year",

    "Revenue Growth Next Year",
    "Revenue Growth Following Year",
]

column_config = {}

for col in percent_columns:

    if col in filtered_table.columns:

        column_config[col] = st.column_config.NumberColumn(
            col,
            format="%.2%"
        )


if "Market Cap" in filtered_table.columns:

    column_config["Market Cap"] = (
        st.column_config.NumberColumn(
            "Market Capitalisation",
            format="$%.0f"
        )
    )


if "EPS Next Year" in filtered_table.columns:

    column_config["EPS Next Year"] = (
        st.column_config.NumberColumn(
            "EPS Next Year",
            format="$%.2f"
        )
    )


if "EPS Following Year" in filtered_table.columns:

    column_config["EPS Following Year"] = (
        st.column_config.NumberColumn(
            "EPS Following Year",
            format="$%.2f"
        )
    )


if "Revenue Next Year" in filtered_table.columns:

    column_config["Revenue Next Year"] = (
        st.column_config.NumberColumn(
            "Revenue Next Year",
            format="$%.0f"
        )
    )


if "Revenue Following Year" in filtered_table.columns:

    column_config["Revenue Following Year"] = (
        st.column_config.NumberColumn(
            "Revenue Following Year",
            format="$%.0f"
        )
    )


st.dataframe(
    filtered_table,
    use_container_width=True,
    hide_index=True,
    height=700,
    column_config=column_config
)


# ============================================================
# SECTION 3 — RETURN VS REALISED VOLATILITY
# ============================================================

st.divider()

st.header("3. Return vs. Realised Volatility")

rv_timeframe = st.radio(
    "Select timeframe",
    [
        "Daily",
        "Weekly",
        "Monthly",
        "Semi-Annual",
        "Annual"
    ],
    horizontal=True,
    key="rv_timeframe"
)


return_col = f"{rv_timeframe} Return"
vol_col = f"{rv_timeframe} Volatility"


rv_df = performance_df[
    [
        "Ticker",
        "Category",
        return_col,
        vol_col
    ]
].copy()


if fundamental_df is not None and not fundamental_df.empty:

    rv_df = rv_df.merge(
        fundamental_df[
            ["Ticker", "Market Cap"]
        ],
        on="Ticker",
        how="left"
    )


rv_df["Return / Volatility"] = (
    rv_df[return_col] /
    rv_df[vol_col].replace(0, np.nan)
)


rv_df = rv_df.dropna(
    subset=[return_col, vol_col]
)


# ============================================================
# SCATTER PLOT
# ============================================================

fig = px.scatter(
    rv_df,
    x=vol_col,
    y=return_col,
    color="Category",
    text="Ticker",
    hover_data=[
        "Ticker",
        "Category",
        "Market Cap"
    ],
    size="Market Cap",
    size_max=30,
    title=f"{rv_timeframe} Return vs Realised Volatility"
)

fig.update_traces(
    textposition="top center",
    textfont=dict(size=9)
)


# ------------------------------------------------------------
# Add zero lines
# ------------------------------------------------------------

fig.add_hline(
    y=0,
    line_dash="dash",
    line_color="gray"
)

fig.add_vline(
    x=rv_df[vol_col].median(),
    line_dash="dash",
    line_color="gray"
)


fig.update_layout(
    height=650,
    xaxis_title="Realised Volatility",
    yaxis_title=f"{rv_timeframe} Return",
    legend_title="Category"
)


fig.update_xaxes(
    tickformat=".0%"
)

fig.update_yaxes(
    tickformat=".0%"
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# RETURN / VOLATILITY RANKING
# ============================================================

st.subheader(
    f"{rv_timeframe} Return / Realised Volatility Ranking"
)

rv_display = rv_df[
    [
        "Ticker",
        "Category",
        "Market Cap",
        return_col,
        vol_col,
        "Return / Volatility"
    ]
].copy()


rv_display = rv_display.sort_values(
    "Return / Volatility",
    ascending=False
)


st.dataframe(
    rv_display,
    use_container_width=True,
    hide_index=True,
    column_config={

        "Market Cap": st.column_config.NumberColumn(
            "Market Cap",
            format="$%.0f"
        ),

        return_col: st.column_config.NumberColumn(
            "Return",
            format="%.2%"
        ),

        vol_col: st.column_config.NumberColumn(
            "Realised Volatility",
            format="%.2%"
        ),

        "Return / Volatility": st.column_config.NumberColumn(
            "Return / Volatility",
            format="%.2f"
        )
    }
)


# ============================================================
# DATA QUALITY
# ============================================================

with st.expander("Data quality / unavailable tickers"):

    unavailable = [
        ticker
        for ticker in tickers
        if ticker not in price_data
    ]

    if unavailable:

        st.warning(
            f"{len(unavailable)} tickers did not return price data:"
        )

        st.write(
            ", ".join(unavailable)
        )

    else:

        st.success(
            "Price data available for all tickers."
        )

    st.caption(
        "Analyst estimates are supplied by Yahoo Finance and "
        "may be unavailable for some securities. "
        "ETF and commodity instruments generally do not have "
        "company-style EPS/revenue estimates."
    )
