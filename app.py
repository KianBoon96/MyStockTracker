import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="My Stock Tracker",
    page_icon="📈",
    layout="wide"
)


# ============================================================
# DEFAULT STOCKS
# ============================================================

DEFAULT_STOCKS = {
    "MRVL": {
        "forward_eps": 5.46,
        "tp": 250
    },
    "CIEN": {
        "forward_eps": 8.67,
        "tp": 400
    },
    "VRT": {
        "forward_eps": 7.81,
        "tp": 300
    },
    "APP": {
        "forward_eps": 18.26,
        "tp": 400
    }
}


# ============================================================
# TITLE
# ============================================================

st.title("📈 My Stock Tracker")

st.caption(
    "1-Year Forward P/E Valuation Dashboard"
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Dashboard Settings")


# ------------------------------------------------------------
# STOCK SELECTION
# ------------------------------------------------------------

selected_tickers = st.sidebar.multiselect(
    "Select Stocks",
    options=list(DEFAULT_STOCKS.keys()),
    default=list(DEFAULT_STOCKS.keys())
)


# ------------------------------------------------------------
# PERIOD
# ------------------------------------------------------------

period = st.sidebar.selectbox(
    "Price History",
    ["6mo", "1y", "2y", "5y"],
    index=1
)


st.sidebar.divider()


# ============================================================
# VALUATION INPUTS
# ============================================================

st.sidebar.subheader("Valuation Inputs")

stocks = {}


for ticker in selected_tickers:

    st.sidebar.markdown(f"### {ticker}")

    forward_eps = st.sidebar.number_input(
        f"{ticker} Forward EPS",
        min_value=0.01,
        value=float(
            DEFAULT_STOCKS[ticker]["forward_eps"]
        ),
        step=0.01,
        format="%.2f",
        key=f"eps_{ticker}"
    )

    target_price = st.sidebar.number_input(
        f"{ticker} Target Price",
        min_value=0.01,
        value=float(
            DEFAULT_STOCKS[ticker]["tp"]
        ),
        step=1.0,
        format="%.2f",
        key=f"tp_{ticker}"
    )

    stocks[ticker] = {
        "forward_eps": forward_eps,
        "tp": target_price
    }


# ============================================================
# NO STOCK SELECTED
# ============================================================

if not selected_tickers:

    st.warning(
        "Please select at least one stock from the sidebar."
    )

    st.stop()


# ============================================================
# DATA LOADING
# ============================================================

@st.cache_data(ttl=300)
def load_prices(tickers, period):

    data = yf.download(
        list(tickers),
        period=period,
        interval="1d",
        auto_adjust=True,
        progress=False
    )

    return data["Close"]


@st.cache_data(ttl=300)
def load_earnings_dates(ticker):

    try:

        earnings = yf.Ticker(
            ticker
        ).get_earnings_dates(
            limit=12
        )

        if earnings is None or len(earnings) == 0:

            return pd.DatetimeIndex([])

        earnings_dates = pd.to_datetime(
            earnings.index
        )

        # Remove timezone
        if earnings_dates.tz is not None:

            earnings_dates = (
                earnings_dates
                .tz_localize(None)
            )

        return earnings_dates

    except Exception:

        return pd.DatetimeIndex([])


# ============================================================
# LOAD DATA
# ============================================================

with st.spinner("Loading market data..."):

    prices = load_prices(
        tuple(selected_tickers),
        period
    )


# ============================================================
# CREATE FIGURE
# ============================================================

fig = make_subplots(
    rows=len(selected_tickers),
    cols=1,
    shared_xaxes=True,
    vertical_spacing=0.05,
    subplot_titles=[
        f"{ticker} — Forward P/E"
        for ticker in selected_tickers
    ]
)


# ============================================================
# SNAPSHOT
# ============================================================

snapshot = {}


# ============================================================
# PROCESS EACH STOCK
# ============================================================

for row, ticker in enumerate(
    selected_tickers,
    start=1
):

    eps = stocks[ticker]["forward_eps"]

    tp = stocks[ticker]["tp"]


    # --------------------------------------------------------
    # PRICE DATA
    # --------------------------------------------------------

    if len(selected_tickers) == 1:

        price = prices.dropna()

    else:

        price = prices[ticker].dropna()


    if len(price) == 0:

        continue


    # --------------------------------------------------------
    # 20-DAY MOVING AVERAGE
    # --------------------------------------------------------

    ma20 = price.rolling(
        window=20
    ).mean()


    # --------------------------------------------------------
    # FORWARD P/E
    # --------------------------------------------------------

    pe = price / eps


    # --------------------------------------------------------
    # HIGH P/E
    # --------------------------------------------------------

    highest_pe = pe.max()

    highest_date = pe.idxmax()

    highest_price = price.loc[
        highest_date
    ]


    # --------------------------------------------------------
    # CURRENT VALUES
    # --------------------------------------------------------

    current_price = price.iloc[-1]

    current_ma20 = ma20.iloc[-1]

    current_pe = pe.iloc[-1]


    # --------------------------------------------------------
    # PRICE VS MA
    # --------------------------------------------------------

    if pd.notna(current_ma20):

        price_vs_ma = (
            current_price / current_ma20 - 1
        ) * 100

    else:

        price_vs_ma = 0


    # --------------------------------------------------------
    # TARGET PRICE P/E
    # --------------------------------------------------------

    tp_pe = tp / eps


    # --------------------------------------------------------
    # UPSIDE TO TARGET
    # --------------------------------------------------------

    upside = (
        tp / current_price - 1
    ) * 100


    # --------------------------------------------------------
    # SAVE SNAPSHOT
    # --------------------------------------------------------

    snapshot[ticker] = {

        "price": current_price,

        "ma20": current_ma20,

        "price_vs_ma": price_vs_ma,

        "eps": eps,

        "pe": current_pe,

        "tp": tp,

        "tp_pe": tp_pe,

        "high_pe": highest_pe,

        "upside": upside
    }


    # ========================================================
    # FORWARD P/E LINE
    # ========================================================

    fig.add_trace(

        go.Scatter(

            x=pe.index,

            y=pe,

            mode="lines",

            name=ticker,

            customdata=[
                [
                    price.loc[d],
                    eps
                ]
                for d in pe.index
            ],

            hovertemplate=(

                f"<b>{ticker}</b><br>"

                "Date: %{x|%d %b %Y}<br>"

                "Price: $%{customdata[0]:.2f}<br>"

                "Forward EPS: $%{customdata[1]:.2f}<br>"

                "Forward P/E: %{y:.2f}x"

                "<extra></extra>"
            ),

            line=dict(
                width=2.5,
                color="#2563eb"
            ),

            showlegend=False
        ),

        row=row,
        col=1
    )


    # ========================================================
    # 1-YEAR HIGH P/E
    # ========================================================

    fig.add_trace(

        go.Scatter(

            x=[highest_date],

            y=[highest_pe],

            mode="markers+text",

            text=[
                f"High: {highest_pe:.1f}x"
            ],

            textposition="top center",

            marker=dict(
                size=13,
                symbol="diamond",
                color="red"
            ),

            hovertemplate=(

                f"<b>{ticker} HIGH P/E</b><br>"

                f"Date: "
                f"{highest_date:%d %b %Y}<br>"

                f"Price: "
                f"${highest_price:.2f}<br>"

                f"Forward EPS: "
                f"${eps:.2f}<br>"

                f"Forward P/E: "
                f"{highest_pe:.2f}x"

                "<extra></extra>"
            ),

            showlegend=False
        ),

        row=row,
        col=1
    )


    # ========================================================
    # TARGET P/E LINE
    # ========================================================

    fig.add_trace(

        go.Scatter(

            x=[
                pe.index.min(),
                pe.index.max()
            ],

            y=[
                tp_pe,
                tp_pe
            ],

            mode="lines",

            line=dict(
                dash="dash",
                width=2,
                color="green"
            ),

            hovertemplate=(

                f"<b>{ticker} TARGET</b><br>"

                f"Target Price: "
                f"${tp:.2f}<br>"

                f"Forward EPS: "
                f"${eps:.2f}<br>"

                f"Target Forward P/E: "
                f"{tp_pe:.2f}x"

                "<extra></extra>"
            ),

            showlegend=False
        ),

        row=row,
        col=1
    )


    # ========================================================
    # EARNINGS DATES
    # ========================================================

    earnings_dates = load_earnings_dates(
        ticker
    )


    if len(earnings_dates) > 0:

        chart_start = pd.Timestamp(
            pe.index.min()
        ).tz_localize(None)

        chart_end = pd.Timestamp(
            pe.index.max()
        ).tz_localize(None)


        earnings_dates = earnings_dates[
            (earnings_dates >= chart_start)
            &
            (earnings_dates <= chart_end)
        ]


        earnings_dates = (
            earnings_dates
            .drop_duplicates()
            .sort_values()
        )


        # Last 4 earnings

        earnings_dates = earnings_dates[-4:]


        # ----------------------------------------------------
        # DRAW EARNINGS LINES
        # ----------------------------------------------------

        for earnings_date in earnings_dates:

            fig.add_vline(

                x=earnings_date,

                line_width=2,

                line_dash="dot",

                line_color="orange",

                row=row,

                col=1
            )


    # ========================================================
    # Y AXIS
    # ========================================================

    fig.update_yaxes(

        title_text="P/E (x)",

        showline=True,

        linewidth=2,

        linecolor="black",

        showgrid=True,

        gridcolor="#e5e7eb",

        ticks="outside",

        tickformat=".0f",

        row=row,

        col=1
    )


# ============================================================
# X AXIS
# ============================================================

fig.update_xaxes(

    showline=True,

    linewidth=2,

    linecolor="black",

    showgrid=True,

    gridcolor="#e5e7eb",

    ticks="outside",

    tickformat="%b %Y",

    row=len(selected_tickers),

    col=1
)


# ============================================================
# GRAPH LAYOUT
# ============================================================

fig.update_layout(

    title=dict(

        text=(
            "Forward P/E — "
            "Individual Stock Valuation"
        ),

        font=dict(size=20)
    ),

    template="plotly_white",

    height=max(
        350 * len(selected_tickers),
        600
    ),

    hovermode="closest",

    margin=dict(
        l=80,
        r=50,
        t=100,
        b=50
    )
)


# ============================================================
# DISPLAY CHART
# ============================================================

st.plotly_chart(
    fig,
    use_container_width=True
)


# ============================================================
# KPI SECTION
# ============================================================

st.subheader(
    "Current Valuation"
)


kpi_columns = st.columns(
    len(selected_tickers)
)


for col, ticker in zip(
    kpi_columns,
    selected_tickers
):

    data = snapshot[ticker]


    with col:

        st.metric(

            label=f"{ticker} Price",

            value=(
                f"${data['price']:.2f}"
            ),

            delta=(
                f"{data['upside']:+.1f}% "
                "to TP"
            )
        )


# ============================================================
# SNAPSHOT TABLE
# ============================================================

st.subheader(
    "Current Valuation Snapshot"
)


snapshot_df = pd.DataFrame(
    snapshot
).T


snapshot_df.index.name = "Stock"


display_df = snapshot_df.rename(

    columns={

        "price": "Price",

        "ma20": "1M MA",

        "price_vs_ma": "vs MA",

        "eps": "Fwd EPS",

        "pe": "Fwd P/E",

        "tp": "TP",

        "tp_pe": "TP P/E",

        "high_pe": "1Y High P/E",

        "upside": "Upside"
    }
)


# ============================================================
# FORMAT TABLE
# ============================================================

display_df["Price"] = (
    display_df["Price"]
    .map(lambda x: f"${x:.2f}")
)


display_df["1M MA"] = (
    display_df["1M MA"]
    .map(lambda x: f"${x:.2f}")
)


display_df["vs MA"] = (
    display_df["vs MA"]
    .map(lambda x: f"{x:+.1f}%")
)


display_df["Fwd EPS"] = (
    display_df["Fwd EPS"]
    .map(lambda x: f"${x:.2f}")
)


display_df["Fwd P/E"] = (
    display_df["Fwd P/E"]
    .map(lambda x: f"{x:.2f}x")
)


display_df["TP"] = (
    display_df["TP"]
    .map(lambda x: f"${x:.2f}")
)


display_df["TP P/E"] = (
    display_df["TP P/E"]
    .map(lambda x: f"{x:.2f}x")
)


display_df["1Y High P/E"] = (
    display_df["1Y High P/E"]
    .map(lambda x: f"{x:.2f}x")
)


display_df["Upside"] = (
    display_df["Upside"]
    .map(lambda x: f"{x:+.1f}%")
)


# ============================================================
# DISPLAY TABLE
# ============================================================

st.dataframe(
    display_df,
    use_container_width=True
)


# ============================================================
# LEGEND
# ============================================================

st.caption(
    "🔵 Forward P/E  |  "
    "🟢 Target Price P/E  |  "
    "🔴 Highest P/E  |  "
    "🟠 Earnings Date"
)


st.caption(
    "Market data provided by Yahoo Finance via yfinance. "
    "Forward EPS and target prices are manually entered inputs."
)