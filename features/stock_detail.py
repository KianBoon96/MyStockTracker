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
            if "Close" not in data.columns.get_level_values(0):
                return pd.DataFrame()

            close = data["Close"]

            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]
        else:
            if "Close" not in data.columns:
                return pd.DataFrame()

            close = data["Close"]

        df = pd.DataFrame({
            "Close": pd.to_numeric(close, errors="coerce")
        }).dropna()

        df.index = pd.to_datetime(df.index)

        if getattr(df.index, "tz", None) is not None:
            df.index = df.index.tz_localize(None)

        return df

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
        earnings = stock.get_earnings_dates(limit=40)

        if earnings is None or earnings.empty:
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

        return sorted(set(clean_dates))

    except Exception:
        return []


# ============================================================
# PRICE CHART
# ============================================================

def render_price_chart(ticker, price_df, earnings_dates):
    if price_df.empty:
        st.warning(f"No price history available for {ticker}.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=price_df.index,
            y=price_df["Close"],
            mode="lines",
            name=ticker,
            line=dict(width=2),
            hovertemplate=(
                "<b>%{x|%d %b %Y}</b><br>"
                "Price: $%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

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
            opacity=0.65,
        )

    fig.update_layout(
        title=f"{ticker} Price History",
        xaxis_title="",
        yaxis_title="Price",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=55, b=10),
        height=500,
        legend=dict(orientation="h"),
    )

    fig.update_xaxes(
        rangeslider_visible=False,
        rangeselector=dict(
            buttons=[
                dict(count=3, label="3M", step="month", stepmode="backward"),
                dict(count=6, label="6M", step="month", stepmode="backward"),
                dict(count=1, label="1Y", step="year", stepmode="backward"),
                dict(count=2, label="2Y", step="year", stepmode="backward"),
                dict(step="all", label="5Y"),
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
        },
    )

    if visible_earnings:
        st.caption(
            f"Dotted vertical lines represent historical earnings dates. "
            f"{len(visible_earnings)} earnings dates are shown."
        )
    else:
        st.caption(
            "No historical earnings dates were returned by Yahoo Finance "
            "for the selected period."
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

    weekly_df = pd.DataFrame({
        "Weekly Return": weekly_returns
    })

    iso_calendar = (
        weekly_df.index
        .to_series()
        .dt.isocalendar()
    )

    weekly_df["Year"] = iso_calendar["year"].astype(int).values
    weekly_df["Week"] = iso_calendar["week"].astype(int).values

    return weekly_df


# ============================================================
# WEEKLY RETURN HEATMAP
# ============================================================

def render_weekly_heatmap(ticker, price_df):
    weekly_df = calculate_weekly_returns(price_df)

    if weekly_df.empty:
        st.warning("Not enough data to calculate weekly returns.")
        return

    heatmap_df = (
        weekly_df
        .pivot_table(
            index="Year",
            columns="Week",
            values="Weekly Return",
            aggfunc="last",
        )
        .sort_index(ascending=False)
    )

    heatmap_percent = heatmap_df * 100

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
            "Return: %{z:.2f}%"
            "<extra></extra>"
        )
    )

    fig.update_layout(
        title=f"{ticker} Weekly Returns Heatmap",
        margin=dict(l=10, r=10, t=55, b=10),
        height=420,
    )

    fig.update_xaxes(
        dtick=4,
        title="Week of Year",
    )

    fig.update_yaxes(title="")

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "responsive": True,
            "displayModeBar": False,
            "displaylogo": False,
        },
    )

    st.caption(
        "Each cell represents the stock's return for that week. "
        "Green = positive return • Red = negative return."
    )


# ============================================================
# SUMMARY METRICS
# ============================================================

def render_stock_metrics(price_df):
    if price_df is None or price_df.empty or len(price_df) < 2:
        return

    current_price = price_df["Close"].iloc[-1]

    daily_return = (
        current_price / price_df["Close"].iloc[-2] - 1
    )

    weekly_return = (
        current_price / price_df["Close"].iloc[-6] - 1
        if len(price_df) > 5
        else np.nan
    )

    monthly_return = (
        current_price / price_df["Close"].iloc[-22] - 1
        if len(price_df) > 21
        else np.nan
    )

    annual_return = (
        current_price / price_df["Close"].iloc[-253] - 1
        if len(price_df) > 252
        else np.nan
    )

    columns = st.columns(5)

    columns[0].metric("Price", f"${current_price:,.2f}")
    columns[1].metric(
        "Daily",
        f"{daily_return:+.2%}" if pd.notna(daily_return) else "—",
    )
    columns[2].metric(
        "Weekly",
        f"{weekly_return:+.2%}" if pd.notna(weekly_return) else "—",
    )
    columns[3].metric(
        "Monthly",
        f"{monthly_return:+.2%}" if pd.notna(monthly_return) else "—",
    )
    columns[4].metric(
        "1 Year",
        f"{annual_return:+.2%}" if pd.notna(annual_return) else "—",
    )


# ============================================================
# MAIN FEATURE
# ============================================================

def show_stock_detail(ticker_list):
    apply_stock_detail_css()

    st.divider()
    st.header("3. Individual Stock Analysis")

    st.caption(
        "Select a stock to view its historical price, "
        "earnings dates and weekly return pattern."
    )

    if not ticker_list:
        st.warning("No tickers are available.")
        return

    selected_ticker = st.selectbox(
        "Select Stock",
        options=sorted(ticker_list),
        key="individual_stock_selector",
    )

    with st.spinner(f"Loading {selected_ticker}..."):
        price_df = download_stock_history(selected_ticker)
        earnings_dates = download_earnings_dates(selected_ticker)

    if price_df.empty:
        st.warning(f"No data available for {selected_ticker}.")
        return

    render_stock_metrics(price_df)

    st.subheader("Price & Earnings History")
    render_price_chart(
        selected_ticker,
        price_df,
        earnings_dates,
    )

    st.subheader("Weekly Returns")
    render_weekly_heatmap(
        selected_ticker,
        price_df,
    )
