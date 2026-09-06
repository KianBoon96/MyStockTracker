# ============================================================
# EQUITY FACTOR & MOMENTUM DASHBOARD
# Streamlit + Yahoo Finance
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime


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
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ======================================================
       GLOBAL
       ====================================================== */

    .block-container {
        padding-top: 1.0rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }


    /* ======================================================
       METRIC CARDS
       ====================================================== */

    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 12px;
        border-radius: 8px;
    }


    /* ======================================================
       TABLE
       ====================================================== */

    div[data-testid="stDataFrame"] {
        width: 100% !important;
    }


    /* ======================================================
       PLOTLY
       ====================================================== */

    .js-plotly-plot {
        width: 100% !important;
        max-width: 100% !important;
    }

    .plot-container {
        width: 100% !important;
    }


    /* ======================================================
       MOBILE
       ====================================================== */

    @media (max-width: 768px) {

        .block-container {
            padding-top: 0.6rem !important;
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
        }


        h1 {
            font-size: 1.45rem !important;
            line-height: 1.2 !important;
        }


        h2 {
            font-size: 1.2rem !important;
        }


        h3 {
            font-size: 1rem !important;
        }


        p {
            font-size: 0.85rem !important;
        }


        /* ==================================================
           METRIC CARDS
           ================================================== */

        div[data-testid="stMetric"] {
            padding: 7px !important;
            min-height: 65px !important;
            border-radius: 7px !important;
        }


        div[data-testid="stMetricLabel"] {
            font-size: 0.65rem !important;
        }


        div[data-testid="stMetricValue"] {
            font-size: 1.0rem !important;
        }


        /* ==================================================
           RADIO
           ================================================== */

        div[role="radiogroup"] {
            gap: 0.2rem !important;
            flex-wrap: wrap !important;
        }


        div[role="radiogroup"] label {
            font-size: 0.76rem !important;
        }


        /* ==================================================
           SELECT BOXES
           ================================================== */

        div[data-baseweb="select"] {
            font-size: 0.8rem !important;
        }


        /* ==================================================
           DATAFRAME
           ================================================== */

        div[data-testid="stDataFrame"] {
            overflow-x: auto !important;
        }


        /* ==================================================
           PLOTLY
           ================================================== */

        .js-plotly-plot {
            width: 100% !important;
            max-width: 100% !important;
        }


        /* ==================================================
           BUTTONS
           ================================================== */

        button {
            min-height: 40px !important;
        }


        /* ==================================================
           CAPTIONS
           ================================================== */

        div[data-testid="stCaptionContainer"] {
            font-size: 0.72rem !important;
        }


        /* ==================================================
           EXPANDERS
           ================================================== */

        details summary {
            font-size: 0.84rem !important;
        }
    }


    /* ======================================================
       SMALL PHONES
       ====================================================== */

    @media (max-width: 480px) {

        .block-container {
            padding-left: 0.35rem !important;
            padding-right: 0.35rem !important;
        }


        h1 {
            font-size: 1.3rem !important;
        }


        h2 {
            font-size: 1.1rem !important;
        }


        div[data-testid="stMetric"] {
            padding: 6px !important;
        }


        div[data-testid="stMetricValue"] {
            font-size: 0.9rem !important;
        }


        div[data-testid="stMetricLabel"] {
            font-size: 0.6rem !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TICKER UNIVERSE
#
# State Street SPDR sector ETFs and bonds removed because
# they are displayed on a separate page.
# ============================================================

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
# YAHOO FINANCE SYMBOL ALIASES
# ============================================================

yf_aliases = {

    # SK Hynix
    "SKHY": "000660.KS",

    # Victoria's Secret
    "VSXY": "VSCO",
}


def yf_symbol(ticker):

    return yf_aliases.get(
        ticker,
        ticker
    )


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


# ============================================================
# FORMATTING
# ============================================================

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


# ============================================================
# DOWNLOAD PRICE DATA
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def download_price_data(ticker_list):

    price_data = {}


    def download_one(ticker):

        symbol = yf_symbol(ticker)

        try:

            data = yf.download(

                symbol,

                period="2y",

                interval="1d",

                auto_adjust=True,

                progress=False,

                threads=False,
            )


            if (
                data is None
                or data.empty
            ):

                return ticker, None


            # ----------------------------------------------
            # MULTIINDEX
            # ----------------------------------------------

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                if (
                    "Close"
                    not in
                    data.columns
                    .get_level_values(0)
                ):

                    return ticker, None


                close = data["Close"]


                if isinstance(
                    close,
                    pd.DataFrame
                ):

                    close = close.iloc[:, 0]


            # ----------------------------------------------
            # NORMAL COLUMNS
            # ----------------------------------------------

            else:

                if "Close" not in data.columns:

                    return ticker, None


                close = data["Close"]


            close = pd.to_numeric(

                close,

                errors="coerce"
            ).dropna()


            if len(close) < 2:

                return ticker, None


            return ticker, close


        except Exception:

            return ticker, None


    # ========================================================
    # PARALLEL DOWNLOAD
    # ========================================================

    with ThreadPoolExecutor(
        max_workers=8
    ) as executor:

        futures = {

            executor.submit(
                download_one,
                ticker
            ): ticker

            for ticker in ticker_list
        }


        for future in as_completed(
            futures
        ):

            try:

                ticker, prices = (
                    future.result()
                )


                if prices is not None:

                    price_data[ticker] = prices


            except Exception:

                pass


    return price_data


# ============================================================
# FUNDAMENTAL DATA
# ============================================================

@st.cache_data(
    ttl=21600,
    show_spinner=False
)
def get_fundamental_data(ticker_list):

    rows = []


    def get_one(ticker):

        result = {

            "Ticker": ticker,

            "Category": category_map.get(
                ticker,
                "Other"
            ),

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


        symbol = yf_symbol(ticker)


        try:

            stock = yf.Ticker(
                symbol
            )


            # =================================================
            # MARKET CAP
            # =================================================

            try:

                info = stock.info

                market_cap = info.get(
                    "marketCap"
                )


                if market_cap is not None:

                    result[
                        "Market Cap"
                    ] = pd.to_numeric(

                        market_cap,

                        errors="coerce"
                    )

            except Exception:

                pass


            # =================================================
            # EPS ESTIMATES
            # =================================================

            try:

                estimates = (
                    stock.get_earnings_estimate()
                )


                if (
                    estimates is not None
                    and not estimates.empty
                ):

                    if "+1y" in estimates.index:

                        row = estimates.loc["+1y"]


                        result[
                            "EPS Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "EPS Growth Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )


                    if "+2y" in estimates.index:

                        row = estimates.loc["+2y"]


                        result[
                            "EPS Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "EPS Growth Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )

            except Exception:

                pass


            # =================================================
            # REVENUE ESTIMATES
            # =================================================

            try:

                revenue_estimates = (
                    stock.get_revenue_estimate()
                )


                if (
                    revenue_estimates is not None
                    and not revenue_estimates.empty
                ):

                    if "+1y" in revenue_estimates.index:

                        row = revenue_estimates.loc["+1y"]


                        result[
                            "Revenue Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "Revenue Growth Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )


                    if "+2y" in revenue_estimates.index:

                        row = revenue_estimates.loc["+2y"]


                        result[
                            "Revenue Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "Revenue Growth Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )

            except Exception:

                pass


        except Exception:

            pass


        return result


    # ========================================================
    # PARALLEL FUNDAMENTALS
    # ========================================================

    with ThreadPoolExecutor(
        max_workers=6
    ) as executor:

        futures = {

            executor.submit(
                get_one,
                ticker
            ): ticker

            for ticker in ticker_list
        }


        for future in as_completed(
            futures
        ):

            try:

                rows.append(
                    future.result()
                )

            except Exception:

                pass


    return pd.DataFrame(
        rows
    )


# ============================================================
# PERFORMANCE CALCULATION
# ============================================================

def calculate_performance(
    price_data
):

    rows = []


    for ticker, prices in price_data.items():

        try:

            prices = pd.to_numeric(

                prices,

                errors="coerce"
            ).dropna()


            if len(prices) < 2:

                continue


            daily_returns = (

                prices

                .pct_change()

                .dropna()
            )


            row = {

                "Ticker": ticker,

                "Category": category_map.get(
                    ticker,
                    "Other"
                ),
            }


            # =================================================
            # RETURNS
            # =================================================

            for label, window in (
                RETURN_WINDOWS.items()
            ):

                column = (
                    f"{label} Return"
                )


                if len(prices) > window:

                    row[column] = (

                        prices.iloc[-1]

                        /

                        prices.iloc[
                            -(window + 1)
                        ]

                    ) - 1


                else:

                    row[column] = np.nan


            # =================================================
            # REALISED VOLATILITY
            # =================================================

            for label, window in (
                VOL_WINDOWS.items()
            ):

                column = (
                    f"{label} Volatility"
                )


                if (
                    len(daily_returns)
                    >= window
                ):

                    recent_returns = (
                        daily_returns
                        .tail(window)
                    )


                    volatility = (

                        recent_returns.std()

                        *

                        np.sqrt(252)
                    )


                    row[column] = volatility


                else:

                    row[column] = np.nan


            rows.append(
                row
            )


        except Exception:

            continue


    return pd.DataFrame(
        rows
    )


# ============================================================
# HEATMAP
# ============================================================

def render_heatmap(

    performance_df,

    fundamental_df,

    timeframe
):

    return_col = (
        f"{timeframe} Return"
    )


    df = performance_df[

        [
            "Ticker",
            "Category",
            return_col,
        ]

    ].copy()


    # ========================================================
    # MARKET CAP
    # ========================================================

    if (

        fundamental_df is not None

        and not fundamental_df.empty

    ):

        df = df.merge(

            fundamental_df[
                [
                    "Ticker",
                    "Market Cap",
                ]
            ],

            on="Ticker",

            how="left",
        )

    else:

        df["Market Cap"] = np.nan


    # ========================================================
    # NUMERIC
    # ========================================================

    df[return_col] = pd.to_numeric(

        df[return_col],

        errors="coerce"
    )


    df["Market Cap"] = pd.to_numeric(

        df["Market Cap"],

        errors="coerce"
    )


    df = df.dropna(

        subset=[return_col]
    )


    df = df.sort_values(

        return_col,

        ascending=False
    )


    if df.empty:

        st.warning(
            "No data available for this timeframe."
        )

        return


    # ========================================================
    # GRID
    # ========================================================

    columns = 8


    rows = int(

        np.ceil(
            len(df) / columns
        )
    )


    z = np.full(

        (rows, columns),

        np.nan
    )


    ticker_grid = np.full(

        (rows, columns),

        "",

        dtype=object
    )


    cap_grid = np.full(

        (rows, columns),

        "",

        dtype=object
    )


    for i, (_, row) in enumerate(
        df.iterrows()
    ):

        r = i // columns

        c = i % columns


        z[r, c] = row[
            return_col
        ]


        ticker_grid[r, c] = (
            row["Ticker"]
        )


        cap_grid[r, c] = (
            format_market_cap(
                row["Market Cap"]
            )
        )


    # ========================================================
    # HEATMAP
    # ========================================================

    fig = go.Figure(

        data=go.Heatmap(

            z=z,

            x=list(
                range(columns)
            ),

            y=list(
                range(rows)
            ),

            colorscale=[

                [0.00, "#8B0000"],

                [0.20, "#C0392B"],

                [0.45, "#34495E"],

                [0.55, "#34495E"],

                [0.80, "#27AE60"],

                [1.00, "#00FF88"],
            ],

            zmid=0,

            customdata=np.dstack(

                (
                    ticker_grid,
                    cap_grid
                )
            ),

            hovertemplate=(

                "<b>%{customdata[0]}</b>"

                "<br>Return: %{z:+.2%}"

                "<br>Market Cap: %{customdata[1]}"

                "<extra></extra>"
            ),

            colorbar=dict(
                title="Return"
            )
        )
    )


    # ========================================================
    # ANNOTATIONS
    # ========================================================

    for r in range(rows):

        for c in range(columns):

            ticker = ticker_grid[
                r,
                c
            ]


            if ticker == "":

                continue


            ret = z[
                r,
                c
            ]


            cap = cap_grid[
                r,
                c
            ]


            fig.add_annotation(

                x=c,

                y=r,

                text=(

                    f"<b>{ticker}</b>"
                    f"<br>"
                    f"{ret:+.2%}"
                    f"<br>"
                    f"<span style='font-size:9px'>"
                    f"{cap}"
                    f"</span>"
                ),

                showarrow=False,

                font=dict(

                    color="white",

                    size=10
                )
            )


    # ========================================================
    # LAYOUT
    # ========================================================

    fig.update_layout(

        title=(
            f"{timeframe} Return "
            "— Market Cap below"
        ),

        height=max(

            450,

            rows * 78
        ),

        xaxis=dict(

            showticklabels=False,

            showgrid=False,

            zeroline=False
        ),

        yaxis=dict(

            showticklabels=False,

            showgrid=False,

            zeroline=False,

            autorange="reversed"
        ),

        margin=dict(

            l=5,

            r=5,

            t=55,

            b=5
        )
    )


    st.plotly_chart(

        fig,

        use_container_width=True,

        config={
            "responsive": True,
            "displayModeBar": False,
        },
    )


# ============================================================
# MAIN TABLE
# ============================================================

def prepare_main_table(

    performance_df,

    fundamental_df
):

    df = performance_df.copy()


    if (

        fundamental_df is not None

        and not fundamental_df.empty

    ):

        df = df.merge(

            fundamental_df,

            on=[
                "Ticker",
                "Category",
            ],

            how="left"
        )


    columns = [

        "Ticker",

        "Category",

        "Market Cap",

        "Daily Return",

        "Weekly Return",

        "Monthly Return",

        "Semi-Annual Return",

        "Annual Return",

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


    columns = [

        c

        for c in columns

        if c in df.columns
    ]


    return df[columns]


# ============================================================
# FILTERS
# ============================================================

def apply_filters(df):

    st.subheader(
        "Filters"
    )


    col1, col2 = st.columns(
        2
    )


    # ========================================================
    # CATEGORY
    # ========================================================

    with col1:

        categories = sorted(

            df[
                "Category"
            ]
            .dropna()
            .unique()
            .tolist()
        )


        selected_categories = (
            st.multiselect(

                "Category",

                categories,

                default=categories
            )
        )


    # ========================================================
    # TICKER
    # ========================================================

    with col2:

        all_tickers = sorted(

            df[
                "Ticker"
            ]
            .dropna()
            .unique()
            .tolist()
        )


        selected_tickers = (
            st.multiselect(

                "Compare specific tickers",

                all_tickers,

                default=[]
            )
        )


    # ========================================================
    # SEARCH
    # ========================================================

    search = st.text_input(

        "Search ticker",

        placeholder=(
            "e.g. NVDA, AMD, PLTR..."
        )
    )


    filtered = df.copy()


    if selected_categories:

        filtered = filtered[
            filtered[
                "Category"
            ].isin(
                selected_categories
            )
        ]


    if selected_tickers:

        filtered = filtered[
            filtered[
                "Ticker"
            ].isin(
                selected_tickers
            )
        ]


    if search:

        filtered = filtered[

            filtered[
                "Ticker"
            ]
            .str
            .contains(

                search.upper(),

                na=False
            )
        ]


    # ========================================================
    # ADVANCED FILTER
    # ========================================================

    with st.expander(
        "Advanced numeric filters"
    ):

        numeric_columns = [

            "Market Cap",

            "Daily Return",

            "Weekly Return",

            "Monthly Return",

            "Semi-Annual Return",

            "Annual Return",

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


        available = [

            c

            for c in numeric_columns

            if c in filtered.columns
        ]


        if available:

            metric = st.selectbox(

                "Metric",

                available
            )


            series = pd.to_numeric(

                filtered[metric],

                errors="coerce"
            ).dropna()


            if not series.empty:

                minimum = float(
                    series.min()
                )

                maximum = float(
                    series.max()
                )


                if minimum < maximum:

                    lower, upper = (
                        st.slider(

                            "Range",

                            min_value=minimum,

                            max_value=maximum,

                            value=(
                                minimum,
                                maximum
                            )
                        )
                    )


                    filtered = filtered[

                        pd.to_numeric(

                            filtered[metric],

                            errors="coerce"

                        ).between(

                            lower,

                            upper
                        )
                    ]


    return filtered


# ============================================================
# FORMAT MAIN TABLE
# ============================================================

def format_main_table(df):

    display = df.copy()


    # ========================================================
    # MARKET CAP
    # ========================================================

    if "Market Cap" in display.columns:

        display[
            "Market Cap"
        ] = display[
            "Market Cap"
        ].apply(
            format_market_cap
        )


    # ========================================================
    # RETURNS
    # ========================================================

    for col in [

        "Daily Return",

        "Weekly Return",

        "Monthly Return",

        "Semi-Annual Return",

        "Annual Return",

    ]:

        if col in display.columns:

            display[col] = (
                display[col]
                .apply(
                    format_percent
                )
            )


    # ========================================================
    # VOLATILITY
    # ========================================================

    for col in [

        "Monthly Volatility",

        "Semi-Annual Volatility",

        "Annual Volatility",

    ]:

        if col in display.columns:

            display[col] = (
                display[col]
                .apply(
                    format_percent
                )
            )


    # ========================================================
    # EPS
    # ========================================================

    for col in [

        "EPS Next Year",

        "EPS Following Year",

    ]:

        if col in display.columns:

            display[col] = (
                display[col]
                .apply(
                    format_number
                )
            )


    # ========================================================
    # REVENUE
    # ========================================================

    for col in [

        "Revenue Next Year",

        "Revenue Following Year",

    ]:

        if col in display.columns:

            display[col] = (
                display[col]
                .apply(
                    format_billions
                )
            )


    # ========================================================
    # GROWTH
    # ========================================================

    for col in [

        "EPS Growth Next Year",

        "EPS Growth Following Year",

        "Revenue Growth Next Year",

        "Revenue Growth Following Year",

    ]:

        if col in display.columns:

            display[col] = (
                display[col]
                .apply(
                    format_percent
                )
            )


    # ========================================================
    # COLUMN NAMES
    # ========================================================

    display = display.rename(

        columns={

            "Market Cap":
                "Market Cap (B)",

            "Semi-Annual Return":
                "6M Return",

            "Annual Return":
                "1Y Return",

            "Semi-Annual Volatility":
                "6M Volatility",

            "Annual Volatility":
                "1Y Volatility",

            "Revenue Next Year":
                "Revenue Next Year (B)",

            "Revenue Following Year":
                "Revenue Following Year (B)",
        }
    )


    return display


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "📊 Equity Dashboard"
)


st.sidebar.write(
    f"**{len(tickers)} unique tickers**"
)


st.sidebar.divider()


st.sidebar.markdown(

    """
### Methodology

**Returns**

Daily = 1 trading day

Weekly = 5 trading days

Monthly = 21 trading days

Semi-Annual = 126 trading days

Annual = 252 trading days


**Matched realised volatility**

Monthly = 21 daily returns

Semi-Annual = 126 daily returns

Annual = 252 daily returns


Volatility is annualised:

**Daily volatility × √252**


**Return / Volatility**

Period return divided by matched
annualised realised volatility.

This is **not a Sharpe ratio** because
the risk-free rate is not subtracted.
"""
)


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
    "Market Capitalisation • "
    "Forward Analyst Estimates"
)


# ============================================================
# PRICE DATA
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
# PERFORMANCE
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
# FUNDAMENTALS
# ============================================================

with st.spinner(
    "Loading market capitalisation "
    "and analyst estimates..."
):

    fundamental_df = get_fundamental_data(
        tuple(tickers)
    )


# ============================================================
# TOP METRICS
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
        len(price_data)
    )


col3, col4 = st.columns(2)


with col3:

    market_cap_count = 0


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


    st.metric(
        "Market Caps",
        market_cap_count
    )


with col4:

    st.metric(

        "Updated",

        datetime.now().strftime(
            "%d %b %Y"
        )
    )


# ============================================================
# PART 1
# ============================================================

st.divider()

st.header(
    "1. Performance Heat Map"
)


heatmap_timeframe = st.radio(

    "Timeframe",

    [

        "Daily",

        "Weekly",

        "Monthly",

        "Semi-Annual",

        "Annual",

    ],

    horizontal=True,

    key="heatmap_timeframe",
)


render_heatmap(

    performance_df,

    fundamental_df,

    heatmap_timeframe,
)


# ============================================================
# PART 2
# ============================================================

st.divider()

st.header(
    "2. Equity Returns, Volatility & Fundamentals"
)


st.caption(

    "Filter the universe to compare "
    "companies across sectors, returns, "
    "volatility and forward estimates."
)


main_table = prepare_main_table(

    performance_df,

    fundamental_df
)


filtered_table = apply_filters(
    main_table
)


st.write(

    f"**{len(filtered_table)} securities selected**"
)


# ============================================================
# TABLE VIEW
# ============================================================

table_view = st.radio(

    "Table view",

    [

        "Essential",

        "Full",

    ],

    horizontal=True,

    key="table_view",
)


if table_view == "Essential":

    essential_columns = [

        "Ticker",

        "Category",

        "Market Cap",

        "Daily Return",

        "Weekly Return",

        "Monthly Return",

        "Semi-Annual Return",

        "Annual Return",

        "Monthly Volatility",

        "Semi-Annual Volatility",

        "Annual Volatility",

    ]


    essential_columns = [

        c

        for c in essential_columns

        if c in filtered_table.columns
    ]


    table_to_display = filtered_table[
        essential_columns
    ]


else:

    table_to_display = filtered_table


# ============================================================
# SORT
# ============================================================

sort_options = [

    "Ticker",

    "Market Cap",

    "Daily Return",

    "Weekly Return",

    "Monthly Return",

    "Semi-Annual Return",

    "Annual Return",

    "Monthly Volatility",

    "Semi-Annual Volatility",

    "Annual Volatility",

]


available_sort_options = [

    c

    for c in sort_options

    if c in table_to_display.columns
]


sort_col = st.selectbox(

    "Sort by",

    available_sort_options,

    key="sort_col",
)


sort_ascending = st.checkbox(

    "Ascending",

    value=True,

    key="sort_ascending",
)


table_to_display = (

    table_to_display

    .sort_values(

        sort_col,

        ascending=sort_ascending,

        na_position="last"
    )
)


display_table = format_main_table(
    table_to_display
)


st.dataframe(

    display_table,

    use_container_width=True,

    hide_index=True,

    height=600,
)


# ============================================================
# PART 3
# RETURN VS REALISED VOLATILITY
#
# ONLY:
# Monthly
# Semi-Annual
# Annual
# ============================================================

st.divider()

st.header(
    "3. Return vs. Realised Volatility"
)


st.caption(

    "Return and realised volatility "
    "use the same measurement horizon."
)


rv_timeframe = st.radio(

    "Select timeframe",

    [

        "Monthly",

        "Semi-Annual",

        "Annual",

    ],

    horizontal=True,

    key="rv_timeframe",
)


return_col = (
    f"{rv_timeframe} Return"
)


vol_col = (
    f"{rv_timeframe} Volatility"
)


# ============================================================
# BUILD RV DATA
# ============================================================

rv_df = pd.DataFrame()


if (

    return_col in performance_df.columns

    and

    vol_col in performance_df.columns

):

    rv_df = performance_df[

        [

            "Ticker",

            "Category",

            return_col,

            vol_col,

        ]

    ].copy()


    # ========================================================
    # MARKET CAP
    # ========================================================

    if (

        fundamental_df is not None

        and not fundamental_df.empty

        and "Market Cap" in fundamental_df.columns

    ):

        rv_df = rv_df.merge(

            fundamental_df[

                [

                    "Ticker",

                    "Market Cap",

                ]

            ],

            on="Ticker",

            how="left"
        )

    else:

        rv_df["Market Cap"] = np.nan


    # ========================================================
    # FORCE NUMERIC
    # ========================================================

    rv_df[return_col] = pd.to_numeric(

        rv_df[return_col],

        errors="coerce"
    )


    rv_df[vol_col] = pd.to_numeric(

        rv_df[vol_col],

        errors="coerce"
    )


    rv_df["Market Cap"] = pd.to_numeric(

        rv_df["Market Cap"],

        errors="coerce"
    )


    # ========================================================
    # REMOVE INVALID VALUES
    # ========================================================

    rv_df = rv_df.dropna(

        subset=[

            return_col,

            vol_col,

        ]
    ).copy()


    # ========================================================
    # RETURN / VOL
    # ========================================================

    rv_df["Return / Volatility"] = np.where(

        rv_df[vol_col] > 0,

        rv_df[return_col]
        /
        rv_df[vol_col],

        np.nan
    )


    rv_df = rv_df.replace(

        [
            np.inf,

            -np.inf,
        ],

        np.nan
    )


    rv_df = rv_df.dropna(

        subset=[

            "Return / Volatility"

        ]
    )


# ============================================================
# DATA COUNT
# ============================================================

st.caption(

    f"{len(rv_df)} securities with valid "
    f"{rv_timeframe.lower()} return and "
    f"matched realised volatility."
)


# ============================================================
# SCATTER PLOT
# MOBILE-OPTIMISED
# ============================================================

if len(rv_df) < 2:

    st.warning(

        "Not enough valid data to create "
        "the return vs realised volatility chart."
    )

else:

    rv_df = rv_df.sort_values(
        "Ticker"
    ).reset_index(
        drop=True
    )


    # ========================================================
    # PREPARE DISPLAY DATA
    # ========================================================

    rv_df["Market Cap Display"] = (
        rv_df["Market Cap"]
        .apply(format_market_cap)
    )


    rv_df["Return / Vol Display"] = (
        rv_df["Return / Volatility"]
        .apply(
            lambda x:
                f"{x:.2f}"
                if pd.notna(x)
                else "N/A"
        )
    )


    # ========================================================
    # PLOTLY SCATTER
    #
    # IMPORTANT MOBILE CHANGE:
    #
    # Do NOT display ticker names permanently on the chart.
    # With ~100+ securities, permanent labels become
    # unreadable on an iPhone.
    #
    # Instead, use larger touch-friendly points and show
    # the ticker in the hover tooltip.
    # ========================================================

    fig = px.scatter(

        rv_df,

        x=vol_col,

        y=return_col,

        color="Category",

        hover_name="Ticker",

        hover_data={

            "Ticker": False,

            "Category": True,

            return_col: ":.2%",

            vol_col: ":.2%",

            "Market Cap Display": True,

            "Return / Vol Display": True,

        },

        labels={

            vol_col:
                "Matched realised volatility",

            return_col:
                f"{rv_timeframe} return",

            "Category":
                "Category",

            "Market Cap Display":
                "Market cap",

            "Return / Vol Display":
                "Return / volatility",

        },

        title=(
            f"{rv_timeframe} Return "
            "vs Matched Realised Volatility"
        ),

    )


    # ========================================================
    # MOBILE-FRIENDLY POINTS
    # ========================================================

    fig.update_traces(

        mode="markers",

        marker=dict(

            size=12,

            opacity=0.82,

            line=dict(

                width=0.8,

                color="rgba(255,255,255,0.55)"
            ),
        ),

        hovertemplate=(

            "<b>%{hovertext}</b>"

            "<br>Category: %{customdata[0]}"

            f"<br>{rv_timeframe} Return: "
            "%{y:+.2%}"

            "<br>Realised Volatility: "
            "%{x:.2%}"

            "<br>Market Cap: "
            "%{customdata[1]}"

            "<br>Return / Volatility: "
            "%{customdata[2]}"

            "<extra></extra>"
        ),

    )


    # ========================================================
    # ZERO RETURN
    # ========================================================

    fig.add_hline(

        y=0,

        line_dash="dash",

        line_color="white",

        opacity=0.45,

        line_width=1,
    )


    # ========================================================
    # MEDIAN VOLATILITY
    # ========================================================

    median_vol = rv_df[
        vol_col
    ].median()


    if pd.notna(
        median_vol
    ):

        fig.add_vline(

            x=median_vol,

            line_dash="dash",

            line_color="#AAAAAA",

            opacity=0.5,

            line_width=1,
        )


    # ========================================================
    # MEDIAN RETURN
    # ========================================================

    median_return = rv_df[
        return_col
    ].median()


    if pd.notna(
        median_return
    ):

        fig.add_hline(

            y=median_return,

            line_dash="dot",

            line_color="#AAAAAA",

            opacity=0.5,

            line_width=1,
        )


    # ========================================================
    # AXES
    #
    # More generous margins make the axis titles readable
    # on narrow iPhone screens.
    # ========================================================

    fig.update_xaxes(

        tickformat=".0%",

        title_text=(
            "Matched realised volatility"
        ),

        title_font=dict(
            size=12
        ),

        tickfont=dict(
            size=10
        ),

        showgrid=True,

        gridcolor="rgba(255,255,255,0.10)",

        zeroline=False,

        automargin=True,
    )


    fig.update_yaxes(

        tickformat=".0%",

        title_text=(
            f"{rv_timeframe} return"
        ),

        title_font=dict(
            size=12
        ),

        tickfont=dict(
            size=10
        ),

        showgrid=True,

        gridcolor="rgba(255,255,255,0.10)",

        zeroline=False,

        automargin=True,
    )


    # ========================================================
    # MOBILE-FRIENDLY LAYOUT
    # ========================================================

    fig.update_layout(

        # Shorter than the previous 550px so it fits
        # more naturally on an iPhone screen.
        height=470,

        autosize=True,

        hovermode="closest",

        dragmode="pan",

        margin=dict(

            l=55,

            r=15,

            t=55,

            b=105,
        ),

        # Horizontal legend below the chart.
        # This prevents the vertical legend from consuming
        # valuable width on mobile.
        legend=dict(

            orientation="h",

            yanchor="top",

            y=-0.22,

            xanchor="center",

            x=0.5,

            font=dict(
                size=9
            ),

            bgcolor="rgba(0,0,0,0)",
        ),

        title=dict(

            x=0.5,

            xanchor="center",

            font=dict(
                size=15
            ),
        ),

        paper_bgcolor="rgba(0,0,0,0)",

        plot_bgcolor="rgba(0,0,0,0)",

    )


    # ========================================================
    # RESPONSIVE CONFIG
    #
    # Removes the Plotly modebar on mobile and allows
    # touch interaction without extra UI taking space.
    # ========================================================

    st.plotly_chart(

        fig,

        use_container_width=True,

        config={

            "responsive": True,

            "displayModeBar": False,

            "scrollZoom": False,

            "doubleClick": "reset",

            "showTips": True,

        },

    )


    st.caption(
        "Tip: tap a point to view the ticker, "
        "return, volatility, market cap and "
        "return/volatility."
    )


# ============================================================
# PART 4
# RETURN / REALISED VOLATILITY RANKING
#
# ONLY:
# Monthly
# Semi-Annual
# Annual
# ============================================================

st.divider()

st.header(
    "4. Return / Realised Volatility Ranking"
)


st.caption(

    "Period return divided by matched "
    "annualised realised volatility."
)


ranking_timeframe = st.radio(

    "Select ranking timeframe",

    [

        "Monthly",

        "Semi-Annual",

        "Annual",

    ],

    horizontal=True,

    key="ranking_timeframe",
)


ranking_return_col = (
    f"{ranking_timeframe} Return"
)


ranking_vol_col = (
    f"{ranking_timeframe} Volatility"
)


# ============================================================
# BUILD RANKING DATA
# ============================================================

ranking_df = pd.DataFrame()


if (

    ranking_return_col
    in performance_df.columns

    and

    ranking_vol_col
    in performance_df.columns

):

    ranking_df = performance_df[

        [

            "Ticker",

            "Category",

            ranking_return_col,

            ranking_vol_col,

        ]

    ].copy()


    # ========================================================
    # MARKET CAP
    # ========================================================

    if (

        fundamental_df is not None

        and not fundamental_df.empty

        and "Market Cap" in fundamental_df.columns

    ):

        ranking_df = ranking_df.merge(

            fundamental_df[

                [

                    "Ticker",

                    "Market Cap",

                ]

            ],

            on="Ticker",

            how="left"
        )

    else:

        ranking_df[
            "Market Cap"
        ] = np.nan


    # ========================================================
    # FORCE NUMERIC
    # ========================================================

    ranking_df[
        ranking_return_col
    ] = pd.to_numeric(

        ranking_df[
            ranking_return_col
        ],

        errors="coerce"
    )


    ranking_df[
        ranking_vol_col
    ] = pd.to_numeric(

        ranking_df[
            ranking_vol_col
        ],

        errors="coerce"
    )


    ranking_df[
        "Market Cap"
    ] = pd.to_numeric(

        ranking_df[
            "Market Cap"
        ],

        errors="coerce"
    )


    # ========================================================
    # REMOVE INVALID
    # ========================================================

    ranking_df = ranking_df.dropna(

        subset=[

            ranking_return_col,

            ranking_vol_col,

        ]
    ).copy()


    # ========================================================
    # RETURN / VOL
    # ========================================================

    ranking_df[
        "Return / Volatility"
    ] = np.where(

        ranking_df[
            ranking_vol_col
        ] > 0,

        ranking_df[
            ranking_return_col
        ]
        /
        ranking_df[
            ranking_vol_col
        ],

        np.nan
    )


    ranking_df = ranking_df.replace(

        [

            np.inf,

            -np.inf,

        ],

        np.nan
    )


    ranking_df = ranking_df.dropna(

        subset=[

            "Return / Volatility"

        ]
    )


# ============================================================
# RANKING
# ============================================================

if ranking_df.empty:

    st.warning(

        "No ranking data available for "
        f"{ranking_timeframe.lower()}."
    )

else:

    ranking_df = (

        ranking_df

        .sort_values(

            "Return / Volatility",

            ascending=False,

            na_position="last"
        )

        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # RANK
    # ========================================================

    ranking_df.insert(

        0,

        "Rank",

        np.arange(

            1,

            len(ranking_df) + 1
        )
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    top_row = ranking_df.iloc[0]


    c1, c2, c3 = st.columns(3)


    with c1:

        st.metric(

            "Rank #1",

            top_row["Ticker"]
        )


    with c2:

        st.metric(

            "Return / Vol",

            f"{top_row['Return / Volatility']:.2f}"
        )


    with c3:

        st.metric(

            "Securities Ranked",

            len(ranking_df)
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    ranking_display = ranking_df.copy()


    # --------------------------------------------------------
    # MARKET CAP
    # --------------------------------------------------------

    ranking_display[
        "Market Cap"
    ] = ranking_display[
        "Market Cap"
    ].apply(
        format_market_cap
    )


    # --------------------------------------------------------
    # RETURN
    # --------------------------------------------------------

    ranking_display[
        ranking_return_col
    ] = ranking_display[
        ranking_return_col
    ].apply(
        format_percent
    )


    # --------------------------------------------------------
    # VOL
    # --------------------------------------------------------

    ranking_display[
        ranking_vol_col
    ] = ranking_display[
        ranking_vol_col
    ].apply(
        format_percent
    )


    # --------------------------------------------------------
    # RETURN / VOL
    # --------------------------------------------------------

    ranking_display[
        "Return / Volatility"
    ] = ranking_display[
        "Return / Volatility"
    ].apply(

        lambda x:

            f"{x:.2f}"

            if pd.notna(x)

            else "N/A"
    )


    # --------------------------------------------------------
    # RENAME
    # --------------------------------------------------------

    ranking_display = ranking_display.rename(

        columns={

            "Market Cap":
                "Market Cap (B)",

            ranking_return_col:
                "Return",

            ranking_vol_col:
                "Realised Volatility",

        }
    )


    # ========================================================
    # MOBILE VIEW
    # ========================================================

    ranking_view = st.radio(

        "Ranking table view",

        [

            "Essential",

            "Full",

        ],

        horizontal=True,

        key="ranking_view",
    )


    if ranking_view == "Essential":

        ranking_columns = [

            "Rank",

            "Ticker",

            "Return",

            "Realised Volatility",

            "Return / Volatility",

        ]

    else:

        ranking_columns = [

            "Rank",

            "Ticker",

            "Category",

            "Market Cap (B)",

            "Return",

            "Realised Volatility",

            "Return / Volatility",

        ]


    ranking_columns = [

        c

        for c in ranking_columns

        if c in ranking_display.columns
    ]


    ranking_display = ranking_display[
        ranking_columns
    ]


    # ========================================================
    # RANKING TABLE
    # ========================================================

    st.dataframe(

        ranking_display,

        use_container_width=True,

        hide_index=True,

        height=600,

    )


# ============================================================
# DATA QUALITY
# ============================================================

st.divider()


with st.expander(
    "Data quality / unavailable tickers"
):

    unavailable = [

        ticker

        for ticker in tickers

        if ticker not in price_data
    ]


    if unavailable:

        st.warning(

            f"{len(unavailable)} ticker(s) "
            "did not return price data:"
        )


        st.write(

            ", ".join(
                unavailable
            )
        )

    else:

        st.success(

            "Price data available for all tickers."
        )


    if (

        fundamental_df is not None

        and not fundamental_df.empty

        and "Market Cap" in fundamental_df.columns

    ):

        missing_market_cap = (

            fundamental_df[
                "Market Cap"
            ]
            .isna()
            .sum()
        )


        st.info(

            f"{missing_market_cap} ticker(s) "
            "do not have market-cap data."
        )


    st.caption(

        "Yahoo Finance may not provide EPS "
        "or revenue estimates for ETFs, "
        "commodities, international securities, "
        "or some smaller companies."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(

    "Data source: Yahoo Finance • "
    "Returns calculated from adjusted daily prices • "
    "Realised volatility annualised using √252"
)
