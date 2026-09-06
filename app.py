# ============================================================
# EQUITY FACTOR / MOMENTUM DASHBOARD
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
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
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

    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 12px;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TICKER UNIVERSE
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
    # CONSUMER / RETAIL / RESTAURANTS / APPAREL
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


    # --------------------------------------------------------
    # STATE STREET / SPDR SECTOR ETFs
    # --------------------------------------------------------

    "XLB",
    "XLC",
    "XLE",
    "XLF",
    "XLI",
    "XLK",
    "XLP",
    "XLRE",
    "XLU",
    "XLV",
    "XLY",


    # --------------------------------------------------------
    # BONDS
    # --------------------------------------------------------

    "TLT",
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


    "Sector ETFs": [

        "XLB",
        "XLC",
        "XLE",
        "XLF",
        "XLI",
        "XLK",
        "XLP",
        "XLRE",
        "XLU",
        "XLV",
        "XLY",
    ],


    "Bonds": [

        "TLT",
    ],
}


category_map = {}

for category, symbols in groups.items():

    for ticker in symbols:

        category_map[ticker] = category


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
# TIMEFRAMES
# ============================================================

TIMEFRAMES = {

    "Daily": 1,

    "Weekly": 5,

    "Monthly": 21,

    "Semi-Annual": 126,

    "Annual": 252,
}


# ============================================================
# FORMATTING FUNCTIONS
# ============================================================

def format_market_cap(value):

    if pd.isna(value):

        return "N/A"

    return f"{value / 1e9:,.1f} B"


def format_revenue(value):

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


def format_ratio(value):

    if pd.isna(value):

        return "N/A"

    return f"{value:.2f}"


# ============================================================
# RETURN CALCULATION
# ============================================================

def calculate_return(
    prices,
    days
):

    if prices is None:

        return np.nan


    if len(prices) < days + 1:

        return np.nan


    try:

        return (

            prices.iloc[-1]
            /
            prices.iloc[-days - 1]

        ) - 1

    except Exception:

        return np.nan


# ============================================================
# REALISED VOLATILITY
# ============================================================

def calculate_volatility(
    returns,
    days
):

    if returns is None:

        return np.nan


    if len(returns) < days:

        return np.nan


    try:

        window = returns.iloc[-days:]


        if len(window) < 2:

            return np.nan


        return (

            window.std()
            *
            np.sqrt(252)

        )

    except Exception:

        return np.nan


# ============================================================
# DOWNLOAD PRICE DATA
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def download_price_data(
    ticker_list
):

    price_data = {}


    def download_one(ticker):

        symbol = yf_symbol(
            ticker
        )


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


            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                close = data[
                    "Close"
                ].iloc[:, 0]

            else:

                close = data[
                    "Close"
                ]


            close = pd.to_numeric(
                close,
                errors="coerce"
            )


            close = close.dropna()


            if len(close) < 10:

                return ticker, None


            return ticker, close


        except Exception:

            return ticker, None


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

                    price_data[
                        ticker
                    ] = prices


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
def get_fundamental_data(
    ticker_list
):

    rows = []


    def get_one(ticker):

        result = {

            "Ticker":
                ticker,

            "Category":
                category_map.get(
                    ticker,
                    "Other"
                ),

            "Market Cap":
                np.nan,

            "EPS Next Year":
                np.nan,

            "EPS Following Year":
                np.nan,

            "Revenue Next Year":
                np.nan,

            "Revenue Following Year":
                np.nan,

            "EPS Growth Next Year":
                np.nan,

            "EPS Growth Following Year":
                np.nan,

            "Revenue Growth Next Year":
                np.nan,

            "Revenue Growth Following Year":
                np.nan,
        }


        symbol = yf_symbol(
            ticker
        )


        try:

            stock = yf.Ticker(
                symbol
            )


            # ==================================================
            # MARKET CAP
            # ==================================================

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


            # ==================================================
            # EPS ESTIMATES
            # ==================================================

            try:

                estimates = (
                    stock.get_earnings_estimate()
                )


                if (
                    estimates is not None
                    and not estimates.empty
                ):

                    if "+1y" in estimates.index:

                        result[
                            "EPS Next Year"
                        ] = pd.to_numeric(

                            estimates.loc[
                                "+1y"
                            ].get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "EPS Growth Next Year"
                        ] = pd.to_numeric(

                            estimates.loc[
                                "+1y"
                            ].get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )


                    if "+2y" in estimates.index:

                        result[
                            "EPS Following Year"
                        ] = pd.to_numeric(

                            estimates.loc[
                                "+2y"
                            ].get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "EPS Growth Following Year"
                        ] = pd.to_numeric(

                            estimates.loc[
                                "+2y"
                            ].get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )

            except Exception:

                pass


            # ==================================================
            # REVENUE ESTIMATES
            # ==================================================

            try:

                revenue_estimates = (
                    stock.get_revenue_estimate()
                )


                if (
                    revenue_estimates is not None
                    and not revenue_estimates.empty
                ):

                    if "+1y" in revenue_estimates.index:

                        result[
                            "Revenue Next Year"
                        ] = pd.to_numeric(

                            revenue_estimates.loc[
                                "+1y"
                            ].get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "Revenue Growth Next Year"
                        ] = pd.to_numeric(

                            revenue_estimates.loc[
                                "+1y"
                            ].get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )


                    if "+2y" in revenue_estimates.index:

                        result[
                            "Revenue Following Year"
                        ] = pd.to_numeric(

                            revenue_estimates.loc[
                                "+2y"
                            ].get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "Revenue Growth Following Year"
                        ] = pd.to_numeric(

                            revenue_estimates.loc[
                                "+2y"
                            ].get(
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
# PERFORMANCE DATAFRAME
# ============================================================

def calculate_performance(
    price_data
):

    rows = []


    for ticker, prices in (
        price_data.items()
    ):

        daily_returns = (
            prices
            .pct_change()
            .dropna()
        )


        row = {

            "Ticker":
                ticker,

            "Category":
                category_map.get(
                    ticker,
                    "Other"
                ),
        }


        for timeframe, days in (
            TIMEFRAMES.items()
        ):

            row[
                f"{timeframe} Return"
            ] = calculate_return(
                prices,
                days
            )


            row[
                f"{timeframe} Volatility"
            ] = calculate_volatility(
                daily_returns,
                days
            )


        rows.append(
            row
        )


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
            return_col
        ]
    ].copy()


    if (
        fundamental_df is not None
        and not fundamental_df.empty
    ):

        df = df.merge(

            fundamental_df[
                [
                    "Ticker",
                    "Market Cap"
                ]
            ],

            on="Ticker",

            how="left"
        )

    else:

        df["Market Cap"] = np.nan


    df[return_col] = pd.to_numeric(
        df[return_col],
        errors="coerce"
    )


    df = df.dropna(
        subset=[
            return_col
        ]
    )


    df = df.sort_values(
        return_col,
        ascending=False
    )


    if df.empty:

        st.warning(
            "No data available."
        )

        return


    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # HEATMAP
    # --------------------------------------------------------

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
                "<br>"
                "Return: %{z:+.2%}"
                "<br>"
                "Market Cap: %{customdata[1]}"
                "<extra></extra>"
            ),

            colorbar=dict(
                title="Return"
            )
        )
    )


    # --------------------------------------------------------
    # ANNOTATIONS
    # --------------------------------------------------------

    for r in range(rows):

        for c in range(columns):

            ticker = (
                ticker_grid[r, c]
            )


            if ticker == "":

                continue


            ret = z[r, c]


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
                    f"<span style='font-size:10px'>"
                    f"{cap}"
                    f"</span>"
                ),

                showarrow=False,

                font=dict(
                    color="white",
                    size=11
                )
            )


    fig.update_layout(

        title=(
            f"{timeframe} Return — "
            "Market Cap shown below"
        ),

        height=max(
            500,
            rows * 85
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
# PREPARE MAIN TABLE
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
                "Category"
            ],

            how="left"
        )


    columns = [

        "Ticker",

        "Category",

        "Market Cap",


        # RETURNS

        "Daily Return",

        "Weekly Return",

        "Monthly Return",

        "Semi-Annual Return",

        "Annual Return",


        # VOLATILITY

        "Daily Volatility",

        "Weekly Volatility",

        "Monthly Volatility",

        "Semi-Annual Volatility",

        "Annual Volatility",


        # EPS

        "EPS Next Year",

        "EPS Following Year",


        # REVENUE

        "Revenue Next Year",

        "Revenue Following Year",


        # EPS GROWTH

        "EPS Growth Next Year",

        "EPS Growth Following Year",


        # REVENUE GROWTH

        "Revenue Growth Next Year",

        "Revenue Growth Following Year",
    ]


    columns = [

        col

        for col in columns

        if col in df.columns
    ]


    return df[
        columns
    ]


# ============================================================
# FILTERS
# ============================================================

def apply_filters(df):

    st.subheader(
        "Filters"
    )


    col1, col2, col3 = st.columns(
        [1.4, 1.4, 2]
    )


    # --------------------------------------------------------
    # CATEGORY
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # TICKER
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    with col3:

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


        available = [

            col

            for col in numeric_columns

            if col in filtered.columns
        ]


        if available:

            metric = st.selectbox(

                "Metric",

                available
            )


            series = pd.to_numeric(

                filtered[
                    metric
                ],

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

                            filtered[
                                metric
                            ],

                            errors="coerce"
                        )
                        .between(
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


    # --------------------------------------------------------
    # MARKET CAP
    # --------------------------------------------------------

    if "Market Cap" in display.columns:

        display[
            "Market Cap"
        ] = (

            display[
                "Market Cap"
            ]

            .apply(
                format_market_cap
            )
        )


    # --------------------------------------------------------
    # RETURNS
    # --------------------------------------------------------

    return_columns = [

        "Daily Return",

        "Weekly Return",

        "Monthly Return",

        "Semi-Annual Return",

        "Annual Return",
    ]


    for col in return_columns:

        if col in display.columns:

            display[col] = (

                display[col]

                .apply(
                    format_percent
                )
            )


    # --------------------------------------------------------
    # VOLATILITY
    # --------------------------------------------------------

    volatility_columns = [

        "Daily Volatility",

        "Weekly Volatility",

        "Monthly Volatility",

        "Semi-Annual Volatility",

        "Annual Volatility",
    ]


    for col in volatility_columns:

        if col in display.columns:

            display[col] = (

                display[col]

                .apply(
                    format_percent
                )
            )


    # --------------------------------------------------------
    # EPS
    # --------------------------------------------------------

    eps_columns = [

        "EPS Next Year",

        "EPS Following Year",
    ]


    for col in eps_columns:

        if col in display.columns:

            display[col] = (

                display[col]

                .apply(
                    format_number
                )
            )


    # --------------------------------------------------------
    # REVENUE
    # --------------------------------------------------------

    revenue_columns = [

        "Revenue Next Year",

        "Revenue Following Year",
    ]


    for col in revenue_columns:

        if col in display.columns:

            display[col] = (

                display[col]

                .apply(
                    format_revenue
                )
            )


    # --------------------------------------------------------
    # GROWTH
    # --------------------------------------------------------

    growth_columns = [

        "EPS Growth Next Year",

        "EPS Growth Following Year",

        "Revenue Growth Next Year",

        "Revenue Growth Following Year",
    ]


    for col in growth_columns:

        if col in display.columns:

            display[col] = (

                display[col]

                .apply(
                    format_percent
                )
            )


    # --------------------------------------------------------
    # RENAME
    # --------------------------------------------------------

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


st.sidebar.markdown(
    "### Universe"
)


st.sidebar.write(
    f"**{len(tickers)} unique tickers**"
)


st.sidebar.divider()


st.sidebar.markdown(
    """
### Methodology

**Return**

Price return over the selected
lookback period.

**Realised Volatility**

Standard deviation of daily returns
annualised by √252.

**Market Cap**

Yahoo Finance market capitalisation.

**Fundamentals**

Yahoo Finance analyst estimates.

**6M**

126 trading days.

**1Y**

252 trading days.
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
    "Market Capitalisation • Analyst Estimates"
)


# ============================================================
# DOWNLOAD PRICE DATA
# ============================================================

with st.spinner(
    "Downloading market data..."
):

    price_data = (
        download_price_data(
            tuple(tickers)
        )
    )


if not price_data:

    st.error(
        "No price data was returned "
        "by Yahoo Finance."
    )

    st.stop()


# ============================================================
# PERFORMANCE
# ============================================================

performance_df = (
    calculate_performance(
        price_data
    )
)


# ============================================================
# FUNDAMENTALS
# ============================================================

with st.spinner(
    "Loading market capitalisation "
    "and analyst estimates..."
):

    fundamental_df = (
        get_fundamental_data(
            tuple(tickers)
        )
    )


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = (
    st.columns(4)
)


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


with col3:

    if (
        fundamental_df is not None
        and not fundamental_df.empty
    ):

        market_cap_count = (

            fundamental_df[
                "Market Cap"
            ]
            .notna()
            .sum()
        )

    else:

        market_cap_count = 0


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
# SECTION 1
# PERFORMANCE HEATMAP
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
# SECTION 2
# MAIN EQUITY TABLE
# ============================================================

st.divider()

st.header(
    "2. Equity Returns, Volatility & Fundamentals"
)


st.caption(
    "Use the filters to narrow the universe "
    "and compare companies."
)


main_table = prepare_main_table(

    performance_df,

    fundamental_df
)


filtered_table = apply_filters(
    main_table
)


st.write(
    f"**{len(filtered_table)} "
    "companies selected**"
)


# ============================================================
# DEFAULT SORT
# ============================================================

sort_options = [

    "Ticker",

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


sort_col = st.selectbox(

    "Sort table by",

    [

        col

        for col in sort_options

        if col in filtered_table.columns
    ],

    index=0
)


sort_ascending = st.checkbox(
    "Ascending",
    value=True
)


filtered_table = (
    filtered_table
    .sort_values(
        sort_col,
        ascending=sort_ascending,
        na_position="last"
    )
)


# ============================================================
# FORMAT AFTER FILTERING
# ============================================================

display_table = format_main_table(
    filtered_table
)


st.dataframe(

    display_table,

    use_container_width=True,

    hide_index=True,

    height=700
)


# ============================================================
# SECTION 3
# RETURN VS REALISED VOLATILITY
# ============================================================

st.divider()

st.header(
    "3. Return vs. Realised Volatility"
)


rv_timeframe = st.radio(

    "Timeframe",

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


return_col = (
    f"{rv_timeframe} Return"
)


vol_col = (
    f"{rv_timeframe} Volatility"
)


# ============================================================
# CREATE RV DATAFRAME
# ============================================================

rv_df = performance_df[

    [
        "Ticker",
        "Category",
        return_col,
        vol_col
    ]

].copy()


# Add market cap
if (

    fundamental_df is not None

    and not fundamental_df.empty

):

    market_cap_data = (
        fundamental_df[
            [
                "Ticker",
                "Market Cap"
            ]
        ].copy()
    )


    rv_df = rv_df.merge(

        market_cap_data,

        on="Ticker",

        how="left"
    )

else:

    rv_df[
        "Market Cap"
    ] = np.nan


# ============================================================
# FORCE NUMERIC
# ============================================================

rv_df[
    return_col
] = pd.to_numeric(

    rv_df[
        return_col
    ],

    errors="coerce"
)


rv_df[
    vol_col
] = pd.to_numeric(

    rv_df[
        vol_col
    ],

    errors="coerce"
)


rv_df[
    "Market Cap"
] = pd.to_numeric(

    rv_df[
        "Market Cap"
    ],

    errors="coerce"
)


# ============================================================
# REMOVE INVALID VALUES
# ============================================================

rv_df = rv_df.dropna(

    subset=[
        return_col,
        vol_col
    ]

).copy()


# ============================================================
# RETURN / VOLATILITY
# ============================================================

rv_df[
    "Return / Volatility"
] = np.where(

    rv_df[
        vol_col
    ] != 0,

    rv_df[
        return_col
    ]
    /
    rv_df[
        vol_col
    ],

    np.nan
)


# ============================================================
# SCATTER PLOT
# ============================================================

if rv_df.empty:

    st.warning(
        "There is not enough data "
        "to create the chart."
    )

else:

    fig = px.scatter(

        rv_df,

        x=vol_col,

        y=return_col,

        color="Category",

        text="Ticker",

        hover_data={

            "Ticker": True,

            "Category": True,

            return_col:
                ":.2%",

            vol_col:
                ":.2%",

            "Market Cap":
                ":,.0f",

            "Return / Volatility":
                ":.2f",
        },

        title=(

            f"{rv_timeframe} Return "
            "vs Realised Volatility"
        )
    )


    # --------------------------------------------------------
    # POINT STYLE
    # --------------------------------------------------------

    fig.update_traces(

        textposition="top center",

        textfont=dict(
            size=9
        ),

        marker=dict(

            size=9,

            opacity=0.80
        )
    )


    # --------------------------------------------------------
    # ZERO RETURN LINE
    # --------------------------------------------------------

    fig.add_hline(

        y=0,

        line_dash="dash",

        line_color="#888888",

        opacity=0.7
    )


    # --------------------------------------------------------
    # MEDIAN VOLATILITY
    # --------------------------------------------------------

    median_vol = rv_df[
        vol_col
    ].median()


    if pd.notna(
        median_vol
    ):

        fig.add_vline(

            x=median_vol,

            line_dash="dash",

            line_color="#888888",

            opacity=0.7
        )


    # --------------------------------------------------------
    # MEDIAN RETURN
    # --------------------------------------------------------

    median_return = rv_df[
        return_col
    ].median()


    if pd.notna(
        median_return
    ):

        fig.add_hline(

            y=median_return,

            line_dash="dot",

            line_color="#555555",

            opacity=0.5
        )


    # --------------------------------------------------------
    # LAYOUT
    # --------------------------------------------------------

    fig.update_layout(

        height=700,

        xaxis_title=(
            "Realised Volatility"
        ),

        yaxis_title=(
            f"{rv_timeframe} Return"
        ),

        legend_title=(
            "Category"
        ),

        hovermode="closest",

        margin=dict(

            l=60,

            r=30,

            t=70,

            b=60
        )
    )


    # --------------------------------------------------------
    # AXIS FORMAT
    # --------------------------------------------------------

    fig.update_xaxes(

        tickformat=".0%",

        zeroline=True,

        zerolinecolor="#555555"
    )


    fig.update_yaxes(

        tickformat=".0%",

        zeroline=True,

        zerolinecolor="#555555"
    )


    st.plotly_chart(

        fig,

        use_container_width=True
    )


# ============================================================
# RETURN / VOLATILITY RANKING
# ============================================================

st.subheader(

    f"{rv_timeframe} "
    "Return / Realised Volatility Ranking"
)


if rv_df.empty:

    st.warning(
        "No ranking data available."
    )

else:

    ranking_df = rv_df[

        [
            "Ticker",

            "Category",

            "Market Cap",

            return_col,

            vol_col,

            "Return / Volatility"
        ]

    ].copy()


    # --------------------------------------------------------
    # SORT
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # RANK
    # --------------------------------------------------------

    ranking_df.insert(

        0,

        "Rank",

        np.arange(

            1,

            len(ranking_df) + 1
        )
    )


    # --------------------------------------------------------
    # FORMAT
    # --------------------------------------------------------

    ranking_display = (
        ranking_df.copy()
    )


    ranking_display[
        "Market Cap"
    ] = (

        ranking_display[
            "Market Cap"
        ]

        .apply(
            format_market_cap
        )
    )


    ranking_display[
        return_col
    ] = (

        ranking_display[
            return_col
        ]

        .apply(
            format_percent
        )
    )


    ranking_display[
        vol_col
    ] = (

        ranking_display[
            vol_col
        ]

        .apply(
            format_percent
        )
    )


    ranking_display[
        "Return / Volatility"
    ] = (

        ranking_display[
            "Return / Volatility"
        ]

        .apply(
            format_ratio
        )
    )


    # --------------------------------------------------------
    # RENAME
    # --------------------------------------------------------

    ranking_display = (
        ranking_display.rename(

            columns={

                "Market Cap":
                    "Market Cap (B)",

                return_col:
                    "Return",

                vol_col:
                    "Realised Volatility",
            }
        )
    )


    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    st.dataframe(

        ranking_display,

        use_container_width=True,

        hide_index=True,

        height=600
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

            "Price data available "
            "for all tickers."
        )


    if (

        fundamental_df is not None

        and not fundamental_df.empty

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

        "Yahoo Finance may not provide "
        "EPS or revenue estimates for "
        "ETFs, bonds, commodities, "
        "international securities, or "
        "some smaller companies."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Data source: Yahoo Finance • "
    "Returns and realised volatility "
    "calculated from adjusted daily prices."
)
