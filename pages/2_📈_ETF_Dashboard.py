# ============================================================
# ETF DASHBOARD
# Streamlit + Yahoo Finance
# ============================================================

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import plotly.graph_objects as go


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="ETF Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# MOBILE CSS
# ============================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 12px;
        border-radius: 8px;
    }

    @media (max-width: 768px) {

        .block-container {
            padding-top: 0.6rem !important;
            padding-left: 0.4rem !important;
            padding-right: 0.4rem !important;
        }

        h1 {
            font-size: 1.4rem !important;
        }

        h2 {
            font-size: 1.15rem !important;
        }

        h3 {
            font-size: 1rem !important;
        }

        p {
            font-size: 0.82rem !important;
        }

        div[data-testid="stMetric"] {
            padding: 7px !important;
            min-height: 60px !important;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.62rem !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 0.95rem !important;
        }

        .js-plotly-plot {
            width: 100% !important;
        }

        div[role="radiogroup"] {
            gap: 0.15rem !important;
            flex-wrap: wrap !important;
        }

    }

    @media (max-width: 480px) {

        .block-container {
            padding-left: 0.25rem !important;
            padding-right: 0.25rem !important;
        }

        h1 {
            font-size: 1.25rem !important;
        }

        h2 {
            font-size: 1.05rem !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 0.88rem !important;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.57rem !important;
        }

    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# ETF UNIVERSE
# ============================================================

ETF_TICKERS = [

    # SPDR sector ETFs
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

    # Aerospace / Defense
    "XAR",

    # Precious metals
    "GLD",
    "SLV",

    # Long duration Treasury
    "TLT",
]


# ============================================================
# ETF CATEGORIES
# ============================================================

ETF_CATEGORIES = {

    "Materials": [
        "XLB",
    ],

    "Communication Services": [
        "XLC",
    ],

    "Energy": [
        "XLE",
    ],

    "Financials": [
        "XLF",
    ],

    "Industrials": [
        "XLI",
    ],

    "Technology": [
        "XLK",
    ],

    "Consumer Staples": [
        "XLP",
    ],

    "Real Estate": [
        "XLRE",
    ],

    "Utilities": [
        "XLU",
    ],

    "Healthcare": [
        "XLV",
    ],

    "Consumer Discretionary": [
        "XLY",
    ],

    "Aerospace / Defense": [
        "XAR",
    ],

    "Gold": [
        "GLD",
    ],

    "Silver": [
        "SLV",
    ],

    "Treasuries": [
        "TLT",
    ],
}


category_map = {}

for category, symbols in ETF_CATEGORIES.items():

    for symbol in symbols:
        category_map[symbol] = category


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

    "Weekly": 5,

    "Monthly": 21,

    "Semi-Annual": 126,

    "Annual": 252,
}


# ============================================================
# FORMATTING
# ============================================================

def format_percent(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:+.2%}"


def format_market_cap(value):

    if pd.isna(value):
        return "N/A"

    return f"{value / 1e9:,.1f} B"


def format_volume(value):

    if pd.isna(value):
        return "N/A"

    return f"{value:,.0f}"


# ============================================================
# DOWNLOAD ETF DATA
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def download_etf_data(etf_list):

    data_dict = {}

    def download_one(ticker):

        try:

            data = yf.download(
                ticker,
                period="2y",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if data is None or data.empty:
                return ticker, None

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                data.columns = (
                    data.columns
                    .get_level_values(0)
                )

            required = [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]

            available = [
                c
                for c in required
                if c in data.columns
            ]

            if "Close" not in available:
                return ticker, None

            data = data[
                available
            ].copy()

            for column in available:

                data[column] = pd.to_numeric(
                    data[column],
                    errors="coerce"
                )

            data = data.dropna(
                subset=["Close"]
            )

            if len(data) < 2:
                return ticker, None

            return ticker, data

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

            for ticker in etf_list
        }

        for future in as_completed(
            futures
        ):

            try:

                ticker, data = (
                    future.result()
                )

                if data is not None:

                    data_dict[
                        ticker
                    ] = data

            except Exception:

                pass


    return data_dict


# ============================================================
# ETF FUNDAMENTALS
# ============================================================

@st.cache_data(
    ttl=21600,
    show_spinner=False
)
def get_etf_fundamentals(
    etf_list
):

    rows = []

    def get_one(ticker):

        result = {

            "Ticker": ticker,

            "Category":
                category_map.get(
                    ticker,
                    "ETF"
                ),

            "Market Cap": np.nan,

            "AUM": np.nan,

        }

        try:

            etf = yf.Ticker(
                ticker
            )

            try:

                info = etf.info

                result[
                    "Market Cap"
                ] = pd.to_numeric(
                    info.get(
                        "marketCap",
                        np.nan
                    ),
                    errors="coerce"
                )

                result[
                    "AUM"
                ] = pd.to_numeric(
                    info.get(
                        "totalAssets",
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

            for ticker in etf_list
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
# PERFORMANCE
# ============================================================

def calculate_performance(
    price_data
):

    rows = []

    for ticker, data in price_data.items():

        try:

            prices = pd.to_numeric(
                data["Close"],
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

                "Ticker":
                    ticker,

                "Category":
                    category_map.get(
                        ticker,
                        "ETF"
                    ),
            }

            # ------------------------------------------------
            # RETURNS
            # ------------------------------------------------

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


            # ------------------------------------------------
            # MATCHED VOLATILITY
            # ------------------------------------------------

            for label, window in (
                VOL_WINDOWS.items()
            ):

                column = (
                    f"{label} Volatility"
                )

                if len(
                    daily_returns
                ) >= window:

                    recent = (
                        daily_returns
                        .tail(window)
                    )

                    row[column] = (

                        recent.std()
                        *
                        np.sqrt(252)

                    )

                else:

                    row[column] = np.nan


            rows.append(row)

        except Exception:

            continue


    return pd.DataFrame(
        rows
    )


# ============================================================
# HEATMAP
# ============================================================

def render_etf_heatmap(
    performance_df,
    fundamentals_df,
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

    if (
        fundamentals_df is not None
        and not fundamentals_df.empty
    ):

        df = df.merge(
            fundamentals_df[
                [
                    "Ticker",
                    "AUM",
                ]
            ],
            on="Ticker",
            how="left"
        )

    else:

        df["AUM"] = np.nan


    df[return_col] = pd.to_numeric(
        df[return_col],
        errors="coerce"
    )

    df["AUM"] = pd.to_numeric(
        df["AUM"],
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
            "No ETF data available."
        )

        return


    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

    columns = 4

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

    aum_grid = np.full(
        (rows, columns),
        "",
        dtype=object
    )


    for i, (_, row) in enumerate(
        df.iterrows()
    ):

        r = i // columns
        c = i % columns

        z[r, c] = float(
            row[return_col]
        )

        ticker_grid[r, c] = (
            row["Ticker"]
        )

        aum_grid[r, c] = (
            format_market_cap(
                row["AUM"]
            )
        )


    customdata = np.empty(
        (rows, columns, 2),
        dtype=object
    )


    for r in range(rows):

        for c in range(columns):

            customdata[
                r, c, 0
            ] = ticker_grid[r, c]

            customdata[
                r, c, 1
            ] = aum_grid[r, c]


    # --------------------------------------------------------
    # CHART
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

            customdata=customdata,

            hovertemplate=(

                "<b>%{customdata[0]}</b>"
                "<br>Return: %{z:+.2%}"
                "<br>AUM: %{customdata[1]}"
                "<extra></extra>"
            ),

            colorbar=dict(
                title="Return"
            )
        )
    )


    for r in range(rows):

        for c in range(columns):

            ticker = (
                ticker_grid[r, c]
            )

            if ticker == "":
                continue

            ret = z[r, c]

            if pd.isna(ret):
                continue

            aum = (
                aum_grid[r, c]
            )

            fig.add_annotation(

                x=c,

                y=r,

                text=(

                    f"<b>{ticker}</b>"
                    f"<br>"
                    f"{ret:+.2%}"
                    f"<br>"
                    f"<span style='font-size:9px'>"
                    f"AUM {aum}"
                    f"</span>"
                ),

                showarrow=False,

                font=dict(
                    color="white",
                    size=11
                )
            )


    fig.update_layout(

        height=max(
            350,
            rows * 85
        ),

        margin=dict(
            l=5,
            r=5,
            t=55,
            b=5
        ),

        title=(
            f"{timeframe} ETF Returns"
        ),

        xaxis=dict(
            showticklabels=False,
            showgrid=False
        ),

        yaxis=dict(
            showticklabels=False,
            showgrid=False,
            autorange="reversed"
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# LOAD DATA
# ============================================================

st.title(
    "📈 ETF Dashboard"
)

st.caption(
    "ETF performance • realised volatility • "
    "AUM • relative risk/return"
)


with st.spinner(
    "Downloading ETF market data..."
):

    price_data = download_etf_data(
        tuple(ETF_TICKERS)
    )


if not price_data:

    st.error(
        "Yahoo Finance returned no ETF price data."
    )

    st.stop()


performance_df = calculate_performance(
    price_data
)


with st.spinner(
    "Loading ETF AUM..."
):

    fundamentals_df = (
        get_etf_fundamentals(
            tuple(ETF_TICKERS)
        )
    )


# ============================================================
# TOP METRICS
# ============================================================

c1, c2, c3, c4 = st.columns(4)

with c1:

    st.metric(
        "ETFs",
        len(ETF_TICKERS)
    )

with c2:

    st.metric(
        "Price Data",
        len(price_data)
    )

with c3:

    if (
        fundamentals_df is not None
        and "AUM" in fundamentals_df.columns
    ):

        aum_count = (
            fundamentals_df[
                "AUM"
            ]
            .notna()
            .sum()
        )

    else:

        aum_count = 0

    st.metric(
        "AUM Available",
        aum_count
    )

with c4:

    st.metric(
        "Updated",
        datetime.now().strftime(
            "%d %b %Y"
        )
    )


# ============================================================
# PART 1
# ETF HEATMAP
# ============================================================

st.divider()

st.header(
    "1. ETF Performance Heat Map"
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

    key="etf_heatmap_timeframe",
)


render_etf_heatmap(
    performance_df,
    fundamentals_df,
    heatmap_timeframe
)


# ============================================================
# PART 2
# ETF TABLE
# ============================================================

st.divider()

st.header(
    "2. ETF Comparison"
)

st.caption(
    "Use the filters and sorting controls "
    "to compare ETFs."
)


table_df = performance_df.copy()


if (
    fundamentals_df is not None
    and not fundamentals_df.empty
):

    table_df = table_df.merge(
        fundamentals_df,
        on=[
            "Ticker",
            "Category",
        ],
        how="left"
    )


# ============================================================
# FILTERS
# ============================================================

col1, col2 = st.columns(2)

with col1:

    categories = sorted(
        table_df[
            "Category"
        ]
        .dropna()
        .unique()
        .tolist()
    )

    selected_categories = st.multiselect(

        "ETF Category",

        categories,

        default=categories,

        key="etf_categories",
    )


with col2:

    selected_etfs = st.multiselect(

        "Compare ETFs",

        sorted(
            table_df[
                "Ticker"
            ]
            .tolist()
        ),

        default=[],

        key="etf_selection",
    )


search = st.text_input(
    "Search ETF",
    placeholder="e.g. XLK, XLE, GLD..."
)


if selected_categories:

    table_df = table_df[
        table_df[
            "Category"
        ].isin(
            selected_categories
        )
    ]


if selected_etfs:

    table_df = table_df[
        table_df[
            "Ticker"
        ].isin(
            selected_etfs
        )
    ]


if search:

    table_df = table_df[
        table_df[
            "Ticker"
        ]
        .astype(str)
        .str
        .contains(
            search.upper(),
            na=False
        )
    ]


# ============================================================
# SORTING
# ============================================================

sort_columns = [

    "Ticker",
    "Category",
    "AUM",

    "Daily Return",
    "Weekly Return",
    "Monthly Return",
    "Semi-Annual Return",
    "Annual Return",

    "Weekly Volatility",
    "Monthly Volatility",
    "Semi-Annual Volatility",
    "Annual Volatility",
]


available_sort_columns = [

    c
    for c in sort_columns
    if c in table_df.columns
]


sort_col = st.selectbox(
    "Sort by",
    available_sort_columns,
    key="etf_sort"
)


ascending = st.checkbox(
    "Ascending",
    value=False,
    key="etf_ascending"
)


table_df = table_df.sort_values(

    sort_col,

    ascending=ascending,

    na_position="last"
)


# ============================================================
# FORMAT TABLE
# ============================================================

display_df = table_df.copy()


if "AUM" in display_df.columns:

    display_df["AUM"] = (
        display_df["AUM"]
        .apply(format_market_cap)
    )


for column in [

    "Daily Return",
    "Weekly Return",
    "Monthly Return",
    "Semi-Annual Return",
    "Annual Return",

    "Weekly Volatility",
    "Monthly Volatility",
    "Semi-Annual Volatility",
    "Annual Volatility",
]:

    if column in display_df.columns:

        display_df[column] = (
            display_df[column]
            .apply(format_percent)
        )


display_df = display_df.rename(
    columns={

        "AUM":
            "AUM (B)",

        "Semi-Annual Return":
            "6M Return",

        "Annual Return":
            "1Y Return",

        "Weekly Volatility":
            "1W Volatility",

        "Monthly Volatility":
            "1M Volatility",

        "Semi-Annual Volatility":
            "6M Volatility",

        "Annual Volatility":
            "1Y Volatility",
    }
)


# ============================================================
# DISPLAY
# ============================================================

st.write(
    f"**{len(display_df)} ETFs selected**"
)


st.dataframe(

    display_df,

    use_container_width=True,

    hide_index=True,

    height=550,
)


# ============================================================
# PART 3
# RETURN VS VOLATILITY
# ============================================================

st.divider()

st.header(
    "3. ETF Return vs Realised Volatility"
)

rv_timeframe = st.radio(

    "Timeframe",

    [
        "Weekly",
        "Monthly",
        "Semi-Annual",
        "Annual",
    ],

    horizontal=True,

    key="etf_rv_timeframe",
)


return_col = (
    f"{rv_timeframe} Return"
)

vol_col = (
    f"{rv_timeframe} Volatility"
)


rv_df = performance_df[
    [
        "Ticker",
        "Category",
        return_col,
        vol_col,
    ]
].copy()


rv_df[return_col] = pd.to_numeric(
    rv_df[return_col],
    errors="coerce"
)


rv_df[vol_col] = pd.to_numeric(
    rv_df[vol_col],
    errors="coerce"
)


rv_df = rv_df.dropna(
    subset=[
        return_col,
        vol_col,
    ]
)


if len(rv_df) < 2:

    st.warning(
        "Not enough data to create "
        "the chart."
    )

else:

    fig = go.Figure()


    categories = sorted(
        rv_df[
            "Category"
        ]
        .dropna()
        .unique()
        .tolist()
    )


    colors = [

        "#4DA3FF",
        "#FF6B6B",
        "#2ECC71",
        "#F1C40F",
        "#9B59B6",
        "#1ABC9C",
        "#E67E22",
        "#E84393",
        "#00CEC9",
        "#6C5CE7",
        "#FD79A8",
        "#55EFC4",
        "#74B9FF",
        "#A29BFE",
        "#95A5A6",
    ]


    color_map = {

        category:
            colors[i % len(colors)]

        for i, category
        in enumerate(categories)
    }


    for category in categories:

        subset = rv_df[
            rv_df[
                "Category"
            ] == category
        ].copy()


        fig.add_trace(

            go.Scatter(

                x=subset[
                    vol_col
                ].astype(float),

                y=subset[
                    return_col
                ].astype(float),

                mode="markers+text",

                name=category,

                text=subset[
                    "Ticker"
                ].astype(str),

                textposition="top center",

                textfont=dict(
                    size=9
                ),

                marker=dict(

                    size=10,

                    color=
                        color_map[
                            category
                        ],

                    opacity=0.85
                ),

                hovertemplate=(

                    "<b>%{text}</b>"
                    "<br>Return: %{y:.2%}"
                    "<br>Realised Vol: %{x:.2%}"
                    "<extra></extra>"
                ),
            )
        )


    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="white",
        opacity=0.45
    )


    fig.update_xaxes(
        tickformat=".0%",
        title=(
            "Matched Realised Volatility"
        )
    )


    fig.update_yaxes(
        tickformat=".0%",
        title=(
            f"{rv_timeframe} Return"
        )
    )


    fig.update_layout(

        height=550,

        hovermode="closest",

        margin=dict(
            l=45,
            r=15,
            t=55,
            b=45
        )
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# PART 4
# RETURN / VOLATILITY RANKING
# ============================================================

st.divider()

st.header(
    "4. ETF Return / Volatility Ranking"
)

ranking_timeframe = st.radio(

    "Timeframe",

    [
        "Weekly",
        "Monthly",
        "Semi-Annual",
        "Annual",
    ],

    horizontal=True,

    key="etf_ranking_timeframe",
)


ranking_return_col = (
    f"{ranking_timeframe} Return"
)

ranking_vol_col = (
    f"{ranking_timeframe} Volatility"
)


ranking_df = performance_df[
    [
        "Ticker",
        "Category",
        ranking_return_col,
        ranking_vol_col,
    ]
].copy()


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


ranking_df = ranking_df.dropna(
    subset=[
        ranking_return_col,
        ranking_vol_col,
    ]
)


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


ranking_df = (
    ranking_df
    .sort_values(
        "Return / Volatility",
        ascending=False
    )
    .reset_index(drop=True)
)


if ranking_df.empty:

    st.warning(
        "No ranking data available."
    )

else:

    ranking_df.insert(
        0,
        "Rank",
        np.arange(
            1,
            len(ranking_df) + 1
        )
    )


    ranking_df[
        "Return"
    ] = ranking_df[
        ranking_return_col
    ].apply(
        format_percent
    )


    ranking_df[
        "Realised Volatility"
    ] = ranking_df[
        ranking_vol_col
    ].apply(
        format_percent
    )


    ranking_df[
        "Return / Volatility"
    ] = ranking_df[
        "Return / Volatility"
    ].apply(

        lambda x:
        f"{x:.2f}"
        if pd.notna(x)
        else "N/A"
    )


    ranking_display = ranking_df[
        [
            "Rank",
            "Ticker",
            "Category",
            "Return",
            "Realised Volatility",
            "Return / Volatility",
        ]
    ]


    st.dataframe(

        ranking_display,

        use_container_width=True,

        hide_index=True,

        height=500,
    )


# ============================================================
# PART 5
# INDIVIDUAL ETF
# ============================================================

st.divider()

st.header(
    "5. Individual ETF Analysis"
)

available_etfs = sorted(
    price_data.keys()
)


if available_etfs:

    default_index = (

        available_etfs.index("XLK")

        if "XLK" in available_etfs

        else 0
    )


    selected_etf = st.selectbox(

        "Select ETF",

        available_etfs,

        index=default_index,

        key="selected_etf",
    )


    etf_data = price_data[
        selected_etf
    ].copy()


    etf_data = etf_data.sort_index()


    # ========================================================
    # RETURNS
    # ========================================================

    etf_data[
        "Daily Return"
    ] = etf_data[
        "Close"
    ].pct_change()


    etf_data[
        "Weekly Return"
    ] = etf_data[
        "Close"
    ].pct_change(5)


    etf_data[
        "Monthly Return"
    ] = etf_data[
        "Close"
    ].pct_change(21)


    # ========================================================
    # CURRENT METRICS
    # ========================================================

    latest = etf_data.iloc[-1]


    current_price = float(
        latest["Close"]
    )


    daily_return = latest[
        "Daily Return"
    ]


    weekly_return = latest[
        "Weekly Return"
    ]


    monthly_return = latest[
        "Monthly Return"
    ]


    # ========================================================
    # METRICS
    # ========================================================

    m1, m2, m3, m4 = st.columns(4)


    with m1:

        st.metric(
            "Price",
            f"{current_price:,.2f}"
        )


    with m2:

        st.metric(
            "Daily Return",
            format_percent(
                daily_return
            )
        )


    with m3:

        st.metric(
            "Weekly Return",
            format_percent(
                weekly_return
            )
        )


    with m4:

        st.metric(
            "Monthly Return",
            format_percent(
                monthly_return
            )
        )


    # ========================================================
    # HISTORICAL HEATMAP
    # ========================================================

    st.subheader(
        "Historical Return Heatmap"
    )


    historical_frequency = st.radio(

        "Frequency",

        [
            "Daily",
            "Weekly",
            "Monthly",
        ],

        horizontal=True,

        key="etf_historical_frequency",
    )


    if historical_frequency == "Daily":

        series = (
            etf_data[
                "Daily Return"
            ]
            .dropna()
            .tail(252)
        )

        columns = 21


    elif historical_frequency == "Weekly":

        series = (
            etf_data[
                "Weekly Return"
            ]
            .dropna()
            .tail(104)
        )

        columns = 13


    else:

        series = (
            etf_data[
                "Monthly Return"
            ]
            .dropna()
            .tail(60)
        )

        columns = 12


    if not series.empty:

        rows = int(
            np.ceil(
                len(series)
                /
                columns
            )
        )


        z = np.full(
            (rows, columns),
            np.nan
        )


        custom = np.full(
            (rows, columns),
            "",
            dtype=object
        )


        for i, (
            date,
            value
        ) in enumerate(
            series.items()
        ):

            r = i // columns

            c = i % columns

            value = pd.to_numeric(
                value,
                errors="coerce"
            )


            if pd.notna(value):

                z[r, c] = float(
                    value
                )


            custom[r, c] = (
                date.strftime(
                    "%d %b %Y"
                )
            )


        fig_heat = go.Figure(

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

                    [0.30, "#C0392B"],

                    [0.50, "#30363D"],

                    [0.70, "#27AE60"],

                    [1.00, "#00FF88"],
                ],

                zmid=0,

                customdata=custom,

                hovertemplate=(

                    "<b>%{customdata}</b>"
                    "<br>Return: %{z:+.2%}"
                    "<extra></extra>"
                ),

                colorbar=dict(
                    title="Return"
                )
            )
        )


        fig_heat.update_layout(

            height=max(
                300,
                min(
                    650,
                    rows * 42
                )
            ),

            margin=dict(
                l=5,
                r=5,
                t=20,
                b=5
            ),

            xaxis=dict(
                showticklabels=False
            ),

            yaxis=dict(
                showticklabels=False,
                autorange="reversed"
            )
        )


        st.plotly_chart(
            fig_heat,
            use_container_width=True
        )


    # ========================================================
    # PRICE RANGE
    # ========================================================

    st.subheader(
        "Price Movement"
    )


    price_range = st.radio(

        "History",

        [
            "1 Month",
            "6 Months",
            "1 Year",
            "2 Years",
        ],

        horizontal=True,

        key="etf_price_range",
    )


    range_map = {

        "1 Month": 21,

        "6 Months": 126,

        "1 Year": 252,

        "2 Years": 504,
    }


    display_data = (
        etf_data
        .tail(
            range_map[
                price_range
            ]
        )
        .copy()
    )


    # ========================================================
    # PRICE CHART
    # ========================================================

    fig_price = go.Figure()


    fig_price.add_trace(

        go.Scatter(

            x=display_data.index,

            y=display_data[
                "Close"
            ],

            mode="lines",

            name="Price",

            line=dict(
                color="#4DA3FF",
                width=2
            ),

            hovertemplate=(

                "<b>%{x|%d %b %Y}</b>"
                "<br>Price: %{y:,.2f}"
                "<extra></extra>"
            )
        )
    )


    fig_price.update_layout(

        height=420,

        title=(
            f"{selected_etf} Price"
        ),

        hovermode="x unified",

        margin=dict(
            l=45,
            r=15,
            t=55,
            b=40
        ),

        xaxis=dict(
            title="Date"
        ),

        yaxis=dict(
            title="Price",
            tickformat=",.2f"
        )
    )


    st.plotly_chart(
        fig_price,
        use_container_width=True
    )


    # ========================================================
    # VOLUME
    # ========================================================

    st.subheader(
        "Trading Volume"
    )


    display_data[
        "Volume Color"
    ] = np.where(

        display_data[
            "Daily Return"
        ].fillna(0) >= 0,

        "#26A269",

        "#C0392B"
    )


    fig_volume = go.Figure()


    fig_volume.add_trace(

        go.Bar(

            x=display_data.index,

            y=display_data[
                "Volume"
            ],

            name="Volume",

            marker_color=(
                display_data[
                    "Volume Color"
                ]
            ),

            hovertemplate=(

                "<b>%{x|%d %b %Y}</b>"
                "<br>Volume: %{y:,.0f}"
                "<extra></extra>"
            )
        )
    )


    fig_volume.update_layout(

        height=260,

        title=(
            f"{selected_etf} Volume"
        ),

        margin=dict(
            l=45,
            r=15,
            t=50,
            b=40
        ),

        xaxis=dict(
            title="Date"
        ),

        yaxis=dict(
            title="Volume",
            tickformat=",.0s"
        )
    )


    st.plotly_chart(
        fig_volume,
        use_container_width=True
    )


    # ========================================================
    # VOLUME STATISTICS
    # ========================================================

    v1, v2, v3 = st.columns(3)


    with v1:

        avg_volume = (
            display_data[
                "Volume"
            ]
            .mean()
        )

        st.metric(
            "Average Volume / Session",
            format_volume(
                avg_volume
            )
        )


    with v2:

        median_volume = (
            display_data[
                "Volume"
            ]
            .median()
        )

        st.metric(
            "Median Volume / Session",
            format_volume(
                median_volume
            )
        )


    with v3:

        latest_volume = (
            display_data[
                "Volume"
            ]
            .iloc[-1]
        )

        st.metric(
            "Latest Volume",
            format_volume(
                latest_volume
            )
        )


# ============================================================
# DATA QUALITY
# ============================================================

st.divider()

with st.expander(
    "Data quality"
):

    unavailable = [

        ticker

        for ticker in ETF_TICKERS

        if ticker not in price_data
    ]


    if unavailable:

        st.warning(
            "No price data for: "
            + ", ".join(unavailable)
        )

    else:

        st.success(
            "Price data available for "
            "all ETFs."
        )


st.caption(
    "Data source: Yahoo Finance • "
    "Returns use adjusted daily prices • "
    "Realised volatility is annualised using √252"
)
