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
# CHART RANGE
# ============================================================

def filter_price_range(price_df, range_label):
    if price_df is None or price_df.empty:
        return price_df

    end_date = price_df.index.max()

    offsets = {
        "1M": pd.DateOffset(months=1),
        "3M": pd.DateOffset(months=3),
        "6M": pd.DateOffset(months=6),
        "1Y": pd.DateOffset(years=1),
        "2Y": pd.DateOffset(years=2),
        "5Y": pd.DateOffset(years=5),
    }

    offset = offsets.get(range_label, pd.DateOffset(years=5))
    start_date = end_date - offset

    filtered = price_df.loc[price_df.index >= start_date].copy()

    return filtered if not filtered.empty else price_df.copy()


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
                name="",
                showlegend=False,
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
                    name="",
                    showlegend=False,
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

            # Draw candles manually instead of using Plotly's native
            # Candlestick trace. This completely removes the native
            # candlestick legend / "undefined" trace label.
            up_mask = price_df["Close"] >= price_df["Open"]
            down_mask = ~up_mask

            # Candle width in milliseconds for a datetime x-axis.
            if len(price_df.index) > 1:
                median_step = (
                    price_df.index.to_series()
                    .diff()
                    .dropna()
                    .median()
                )
                candle_width = max(
                    median_step.total_seconds() * 1000 * 0.65,
                    1,
                )
            else:
                candle_width = 12 * 60 * 60 * 1000

            # Wicks
            for mask, candle_color in [
                (up_mask, "#00C853"),
                (down_mask, "#FF1744"),
            ]:
                wick_x = []
                wick_y = []

                for date, low_price, high_price in zip(
                    price_df.index[mask],
                    price_df.loc[mask, "Low"],
                    price_df.loc[mask, "High"],
                ):
                    wick_x.extend([date, date, None])
                    wick_y.extend([low_price, high_price, None])

                if wick_x:
                    fig.add_trace(
                        go.Scatter(
                            x=wick_x,
                            y=wick_y,
                            mode="lines",
                            line=dict(
                                color=candle_color,
                                width=1.5,
                            ),
                            hoverinfo="skip",
                            showlegend=False,
                            name="",
                        )
                    )

            # Candle bodies
            body_bottom = pd.concat(
                [
                    price_df["Open"],
                    price_df["Close"],
                ],
                axis=1,
            ).min(axis=1)

            body_height = (
                price_df["Close"]
                - price_df["Open"]
            ).abs()

            # Give doji candles a tiny visible body.
            min_body = (
                price_df["Close"].abs() * 0.0002
            ).clip(lower=0.001)

            body_height = body_height.where(
                body_height > 0,
                min_body,
            )

            candle_colors = np.where(
                up_mask,
                "#00C853",
                "#FF1744",
            )

            fig.add_trace(
                go.Bar(
                    x=price_df.index,
                    y=body_height,
                    base=body_bottom,
                    width=candle_width,
                    marker=dict(
                        color=candle_colors,
                        line=dict(width=0),
                    ),
                    hoverinfo="skip",
                    showlegend=False,
                    name="",
                )
            )

            # Build the hover label as fully formatted text.
            # This avoids Plotly exposing the raw floating-point percentage.
            hover_text = [
                (
                    f"<b>{date.strftime('%d %b %Y')}</b>"
                    "<br><br>"
                    f"<b>Open</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${open_price:,.2f}"
                    "<br>"
                    f"<b>High</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${high_price:,.2f}"
                    "<br>"
                    f"<b>Low</b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${low_price:,.2f}"
                    "<br>"
                    f"<b>Close</b>&nbsp;&nbsp;&nbsp;&nbsp;${close_price:,.2f}"
                    "<br><br>"
                    f"<b>Change</b>&nbsp;&nbsp;{change:+.2f}%"
                )
                for date, open_price, high_price, low_price, close_price, change
                in zip(
                    price_df.index,
                    price_df["Open"],
                    price_df["High"],
                    price_df["Low"],
                    price_df["Close"],
                    change_pct,
                )
            ]

            # Invisible overlay used as the only hover source.
            fig.add_trace(
                go.Scatter(
                    x=price_df.index,
                    y=price_df["Close"],
                    mode="markers",
                    marker=dict(
                        size=14,
                        opacity=0,
                    ),
                    text=hover_text,
                    hovertemplate="%{text}<extra></extra>",
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
        legend=dict(
            title_text="",
            itemsizing="constant",
        ),
        barmode="overlay",
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
    )

    # Final safeguard: no trace names / "undefined" / candlestick legend.
    fig.update_traces(showlegend=False)
    fig.update_layout(showlegend=False)

    # Hard-disable all Plotly legends for this chart.
    for trace in fig.data:
        trace.showlegend = False
        trace.name = ""

    fig.update_layout(
        showlegend=False,
        legend_title_text="",
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

    range_label = st.radio(
        "Range",
        [
            "1M",
            "3M",
            "6M",
            "1Y",
            "2Y",
            "5Y",
        ],
        index=5,
        horizontal=True,
        label_visibility="collapsed",
        key="stock_price_range",
    )

    chart_price_df = filter_price_range(
        price_df,
        range_label,
    )

    render_price_chart(
        selected_ticker,
        chart_price_df,
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
