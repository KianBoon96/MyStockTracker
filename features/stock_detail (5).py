import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from config import yf_symbol


# ============================================================
# CSS
# ============================================================

def apply_stock_detail_css():
    st.markdown(
        """
        <style>
        div[data-testid="stPlotlyChart"] {
            width: 100% !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DOWNLOAD STOCK HISTORY
# ============================================================

@st.cache_data(ttl=3600, show_spinner=False)
def download_stock_history(ticker):
    symbol = yf_symbol(ticker)

    try:
        data = yf.download(
            symbol,
            period="5y",
            interval="1d",
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if data is None or data.empty:
            return pd.DataFrame()

        if isinstance(data.columns, pd.MultiIndex):
            clean_data = pd.DataFrame()

            for column in [
                "Open",
                "High",
                "Low",
                "Close",
                "Volume",
            ]:
                if column in data.columns.get_level_values(0):
                    values = data[column]

                    if isinstance(values, pd.DataFrame):
                        values = values.iloc[:, 0]

                    clean_data[column] = pd.to_numeric(
                        values,
                        errors="coerce",
                    )

            data = clean_data

        else:
            available_columns = [
                column
                for column in [
                    "Open",
                    "High",
                    "Low",
                    "Close",
                    "Volume",
                ]
                if column in data.columns
            ]

            data = data[available_columns].copy()

        if "Close" not in data.columns:
            return pd.DataFrame()

        data = data.dropna(subset=["Close"])

        data.index = pd.to_datetime(data.index)

        if getattr(data.index, "tz", None) is not None:
            data.index = data.index.tz_localize(None)

        return data

    except Exception:
        return pd.DataFrame()


# ============================================================
# DOWNLOAD EARNINGS DATES
# ============================================================

@st.cache_data(ttl=21600, show_spinner=False)
def download_earnings_dates(ticker):
    symbol = yf_symbol(ticker)

    try:
        stock = yf.Ticker(symbol)

        earnings = stock.get_earnings_dates(
            limit=40
        )

        if (
            earnings is None
            or earnings.empty
        ):
            return []

        dates = pd.to_datetime(
            earnings.index,
            errors="coerce",
        )

        clean_dates = []

        for date in dates:
            if pd.isna(date):
                continue

            date = pd.Timestamp(date)

            if date.tzinfo is not None:
                date = date.tz_localize(None)

            clean_dates.append(date)

        return sorted(
            set(clean_dates)
        )

    except Exception:
        return []


# ============================================================
# PRICE CHART
# ============================================================

def render_price_chart(
    ticker,
    price_df,
    earnings_dates,
    chart_type
):
    if price_df.empty:
        st.warning(
            f"No price history available for {ticker}."
        )
        return

    fig = go.Figure()

    # ========================================================
    # LINE CHART
    # ========================================================

    if chart_type == "Line":
        fig.add_trace(
            go.Scatter(
                x=price_df.index,
                y=price_df["Close"],
                mode="lines",
                name=ticker,
                line=dict(
                    width=2
                ),
                hovertemplate=(
                    "<b>%{x|%d %b %Y}</b><br>"
                    "Price: $%{y:,.2f}"
                    "<extra></extra>"
                ),
            )
        )

    # ========================================================
    # CANDLESTICK CHART
    # ========================================================

    else:
        required_columns = [
            "Open",
            "High",
            "Low",
            "Close",
        ]

        if not all(
            column in price_df.columns
            for column in required_columns
        ):
            st.warning(
                "OHLC data is unavailable for "
                "this stock. Showing line chart instead."
            )

            fig.add_trace(
                go.Scatter(
                    x=price_df.index,
                    y=price_df["Close"],
                    mode="lines",
                    name=ticker,
                    hovertemplate=(
                        "<b>%{x|%d %b %Y}</b><br>"
                        "Price: $%{y:,.2f}"
                        "<extra></extra>"
                    ),
                )
            )

        else:
            # Daily open-to-close move
            change_pct = (
                (
                    price_df["Close"]
                    - price_df["Open"]
                )
                / price_df["Open"]
                * 100
            )

            fig.add_trace(
                go.Candlestick(
                    x=price_df.index,
                    open=price_df["Open"],
                    high=price_df["High"],
                    low=price_df["Low"],
                    close=price_df["Close"],
                    name="",
                    showlegend=False,
                    increasing_line_color="#00C853",
                    decreasing_line_color="#FF1744",
                    increasing_fillcolor="#00C853",
                    decreasing_fillcolor="#FF1744",
                    hoverinfo="skip",
                )
            )

            # Invisible overlay to give cleaner custom hover
            fig.add_trace(
                go.Scatter(
                    x=price_df.index,
                    y=price_df["Close"],
                    mode="markers",
                    marker=dict(
                        size=14,
                        opacity=0,
                    ),
                    customdata=np.column_stack(
                        [
                            price_df["Open"],
                            price_df["High"],
                            price_df["Low"],
                            price_df["Close"],
                            change_pct.map(lambda x: f"{x:+.2f}%"),
                        ]
                    ),
                    hovertemplate=(
                        "<b>%{x|%d %b %Y}</b>"
                        "<br><br>"
                        "<b>Open</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$%{customdata[0]:,.2f}"
                        "<br>"
                        "<b>High</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$%{customdata[1]:,.2f}"
                        "<br>"
                        "<b>Low</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;$%{customdata[2]:,.2f}"
                        "<br>"
                        "<b>Close</b>&nbsp;&nbsp;&nbsp;&nbsp;$%{customdata[3]:,.2f}"
                        "<br><br>"
                        "<b>Change</b>&nbsp;&nbsp;%{customdata[4]}"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                )
            )

    # ========================================================
    # EARNINGS DATE LINES
    # ========================================================

    start_date = price_df.index.min()
    end_date = price_df.index.max()

    visible_earnings = [
        date
        for date in earnings_dates
        if start_date <= date <= end_date
    ]

    for date in visible_earnings:
        fig.add_vline(
            x=date,
            line_width=1,
            line_dash="dot",
            line_color="gray",
            opacity=0.7,
        )

    # ========================================================
    # LAYOUT
    # ========================================================

    fig.update_layout(
        title=None,
        xaxis_title="",
        yaxis_title="Price ($)",
        hovermode=(
            "x unified"
            if chart_type == "Line"
            else "closest"
        ),
        margin=dict(
            l=20,
            r=20,
            t=25,
            b=20,
        ),
        height=600,
        showlegend=False,
        xaxis_rangeslider_visible=False,
    )

    # ========================================================
    # RANGE BUTTONS
    # ========================================================

    fig.update_yaxes(
        tickformat=",.2f",
        separatethousands=True,
        automargin=True,
        title_standoff=12,
    )

    fig.update_xaxes(
        automargin=True,
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=[
                dict(
                    count=1,
                    label="1M",
                    step="month",
                    stepmode="backward",
                ),
                dict(
                    count=3,
                    label="3M",
                    step="month",
                    stepmode="backward",
                ),
                dict(
                    count=6,
                    label="6M",
                    step="month",
                    stepmode="backward",
                ),
                dict(
                    count=1,
                    label="1Y",
                    step="year",
                    stepmode="backward",
                ),
                dict(
                    count=2,
                    label="2Y",
                    step="year",
                    stepmode="backward",
                ),
                dict(
                    step="all",
                    label="5Y",
                ),
            ]
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "displayModeBar": False,
            "displaylogo": False,
        }
    )

    if visible_earnings:
        st.caption(
            "Dotted vertical lines represent "
            "historical earnings dates."
        )
    else:
        st.caption(
            "No historical earnings dates were "
            "returned by Yahoo Finance for this period."
        )


# ============================================================
# WEEKLY RETURNS
# ============================================================

def calculate_weekly_returns(price_df):
    if price_df.empty:
        return pd.DataFrame()

    weekly_prices = (
        price_df["Close"]
        .resample("W-FRI")
        .last()
        .dropna()
    )

    weekly_returns = (
        weekly_prices
        .pct_change(fill_method=None)
        .dropna()
    )

    weekly_df = pd.DataFrame(
        {
            "Weekly Return":
            weekly_returns
        }
    )

    iso_calendar = (
        weekly_df.index
        .to_series()
        .dt
        .isocalendar()
    )

    weekly_df["Year"] = (
        iso_calendar["year"]
        .astype(int)
        .values
    )

    weekly_df["Week"] = (
        iso_calendar["week"]
        .astype(int)
        .values
    )

    return weekly_df


# ============================================================
# WEEKLY HEATMAP
# ============================================================

def render_weekly_heatmap(
    ticker,
    price_df
):
    weekly_df = (
        calculate_weekly_returns(
            price_df
        )
    )

    if weekly_df.empty:
        st.warning(
            "Not enough data to calculate weekly returns."
        )
        return

    heatmap_df = (
        weekly_df
        .pivot_table(
            index="Year",
            columns="Week",
            values="Weekly Return",
            aggfunc="last",
        )
        .sort_index(
            ascending=False
        )
    )

    heatmap_percent = (
        heatmap_df * 100
    )

    fig = px.imshow(
        heatmap_percent,
        aspect="auto",
        color_continuous_scale="RdYlGn",
        color_continuous_midpoint=0,
        labels={
            "x": "Week",
            "y": "Year",
            "color": "Return %",
        },
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Year %{y}</b><br>"
            "Week %{x}<br>"
            "Return: %{z:+.2f}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title=f"{ticker} Weekly Returns Heatmap",
        margin=dict(
            l=10,
            r=10,
            t=55,
            b=10,
        ),
        height=420,
    )

    fig.update_xaxes(
        dtick=4,
        title="Week of Year",
    )

    fig.update_yaxes(
        title=""
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "displayModeBar": False,
            "displaylogo": False,
        }
    )

    st.caption(
        "Each cell represents the stock's weekly return. "
        "Green = positive • Red = negative."
    )


# ============================================================
# SUMMARY METRICS
# ============================================================

def render_stock_metrics(
    price_df
):
    if (
        price_df is None
        or price_df.empty
        or len(price_df) < 2
    ):
        return

    current_price = (
        price_df["Close"]
        .iloc[-1]
    )

    daily_return = (
        current_price
        /
        price_df["Close"].iloc[-2]
        - 1
    )

    weekly_return = (
        current_price
        /
        price_df["Close"].iloc[-6]
        - 1
        if len(price_df) > 5
        else np.nan
    )

    monthly_return = (
        current_price
        /
        price_df["Close"].iloc[-22]
        - 1
        if len(price_df) > 21
        else np.nan
    )

    annual_return = (
        current_price
        /
        price_df["Close"].iloc[-253]
        - 1
        if len(price_df) > 252
        else np.nan
    )

    columns = st.columns(5)

    columns[0].metric(
        "Price",
        f"${current_price:,.2f}"
    )

    columns[1].metric(
        "Daily",
        (
            f"{daily_return:+.2%}"
            if pd.notna(daily_return)
            else "—"
        )
    )

    columns[2].metric(
        "Weekly",
        (
            f"{weekly_return:+.2%}"
            if pd.notna(weekly_return)
            else "—"
        )
    )

    columns[3].metric(
        "Monthly",
        (
            f"{monthly_return:+.2%}"
            if pd.notna(monthly_return)
            else "—"
        )
    )

    columns[4].metric(
        "1 Year",
        (
            f"{annual_return:+.2%}"
            if pd.notna(annual_return)
            else "—"
        )
    )


# ============================================================
# MAIN FEATURE
# ============================================================

def show_stock_detail(
    ticker_list
):
    apply_stock_detail_css()

    st.divider()

    st.header(
        "3. Individual Stock Analysis"
    )

    st.caption(
        "Select a stock to view its historical price, "
        "earnings dates and weekly return pattern."
    )

    if not ticker_list:
        st.warning(
            "No tickers are available."
        )
        return

    # ========================================================
    # STOCK + CHART TYPE SELECTOR
    # ========================================================

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:
        selected_ticker = (
            st.selectbox(
                "Select Stock",
                options=sorted(
                    ticker_list
                ),
                key=(
                    "individual_stock_selector"
                ),
            )
        )

    with col2:
        chart_type = (
            st.radio(
                "Chart Type",
                [
                    "Line",
                    "Candlestick",
                ],
                horizontal=True,
                key=(
                    "stock_chart_type"
                ),
            )
        )

    # ========================================================
    # DOWNLOAD DATA
    # ========================================================

    with st.spinner(
        f"Loading {selected_ticker}..."
    ):
        price_df = (
            download_stock_history(
                selected_ticker
            )
        )

        earnings_dates = (
            download_earnings_dates(
                selected_ticker
            )
        )

    if price_df.empty:
        st.warning(
            f"No data available for {selected_ticker}."
        )
        return

    # ========================================================
    # METRICS
    # ========================================================

    render_stock_metrics(
        price_df
    )

    # ========================================================
    # PRICE CHART
    # ========================================================

    st.subheader(
        "Price & Earnings History"
    )

    render_price_chart(
        selected_ticker,
        price_df,
        earnings_dates,
        chart_type,
    )

    # ========================================================
    # WEEKLY HEATMAP
    # ========================================================

    st.subheader(
        "Weekly Returns"
    )

    render_weekly_heatmap(
        selected_ticker,
        price_df,
    )
