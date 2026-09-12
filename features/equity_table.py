import streamlit as st
import pandas as pd
import numpy as np


# ============================================================
# CSS
# ============================================================

def apply_equity_table_css():

    st.markdown(
        """
        <style>

        div[data-testid="stDataFrame"] {
            width: 100% !important;
        }

        @media (max-width: 768px) {

            div[data-testid="stDataFrame"] {
                overflow-x: auto !important;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# HELPERS
# ============================================================

def safe_divide(numerator, denominator):

    numerator = pd.to_numeric(
        numerator,
        errors="coerce"
    )

    denominator = pd.to_numeric(
        denominator,
        errors="coerce"
    )

    if (
        pd.isna(numerator)
        or pd.isna(denominator)
        or denominator == 0
    ):
        return np.nan

    return numerator / denominator


def format_price(value):

    if pd.isna(value):
        return "—"

    return f"${value:,.2f}"


def format_eps(value):

    if pd.isna(value):
        return "—"

    return f"{value:,.2f}"


def format_multiple(value):

    if pd.isna(value):
        return "—"

    return f"{value:,.1f}x"


def format_revenue(value):

    if pd.isna(value):
        return "—"

    value = float(value)

    if abs(value) >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:,.2f}T"

    if abs(value) >= 1_000_000_000:
        return f"${value / 1_000_000_000:,.2f}B"

    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f}M"

    return f"${value:,.0f}"


# ============================================================
# PREPARE VALUATION TABLE
# ============================================================

def prepare_valuation_table(fundamental_df):

    if (
        fundamental_df is None
        or fundamental_df.empty
    ):
        return pd.DataFrame()

    df = fundamental_df.copy()

    required_columns = [
        "Ticker",
        "Category",
        "Current Price",
        "Market Cap",
        "TTM EPS",
        "NTM EPS",
        "TTM Revenue",
        "NTM Revenue",
    ]

    for column in required_columns:

        if column not in df.columns:
            df[column] = np.nan


    # ========================================================
    # P/E MULTIPLES
    # ========================================================

    df["P/E TTM"] = df.apply(
        lambda row: safe_divide(
            row["Current Price"],
            row["TTM EPS"]
        ),
        axis=1
    )

    df["P/E NTM"] = df.apply(
        lambda row: safe_divide(
            row["Current Price"],
            row["NTM EPS"]
        ),
        axis=1
    )


    # ========================================================
    # PRICE / SALES MULTIPLES
    #
    # Company revenue belongs to the whole company,
    # therefore Market Cap / Revenue is used.
    # ========================================================

    df["P/S TTM"] = df.apply(
        lambda row: safe_divide(
            row["Market Cap"],
            row["TTM Revenue"]
        ),
        axis=1
    )

    df["P/S NTM"] = df.apply(
        lambda row: safe_divide(
            row["Market Cap"],
            row["NTM Revenue"]
        ),
        axis=1
    )


    return df[
        [
            "Ticker",
            "Category",
            "Current Price",
            "TTM EPS",
            "NTM EPS",
            "P/E TTM",
            "P/E NTM",
            "TTM Revenue",
            "NTM Revenue",
            "P/S TTM",
            "P/S NTM",
        ]
    ]


# ============================================================
# FILTERS
# ============================================================

def apply_filters(df):

    col1, col2 = st.columns(2)

    with col1:

        categories = sorted(
            df["Category"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_categories = st.multiselect(
            "Industry / Category",
            categories,
            default=categories,
            key="valuation_categories"
        )


    with col2:

        tickers = sorted(
            df["Ticker"]
            .dropna()
            .unique()
            .tolist()
        )

        selected_tickers = st.multiselect(
            "Compare specific tickers",
            tickers,
            default=[],
            key="valuation_tickers"
        )


    search = st.text_input(
        "Search ticker",
        placeholder="e.g. NVDA, MRVL, PLTR...",
        key="valuation_search"
    )


    filtered = df.copy()


    if selected_categories:

        filtered = filtered[
            filtered["Category"].isin(
                selected_categories
            )
        ]


    if selected_tickers:

        filtered = filtered[
            filtered["Ticker"].isin(
                selected_tickers
            )
        ]


    if search:

        filtered = filtered[
            filtered["Ticker"]
            .str
            .contains(
                search.upper(),
                na=False
            )
        ]


    return filtered


# ============================================================
# DISPLAY FORMATTING
# ============================================================

def format_valuation_table(df):

    display = df.copy()

    display["Current Price"] = (
        display["Current Price"]
        .apply(format_price)
    )

    display["TTM EPS"] = (
        display["TTM EPS"]
        .apply(format_eps)
    )

    display["NTM EPS"] = (
        display["NTM EPS"]
        .apply(format_eps)
    )

    display["P/E TTM"] = (
        display["P/E TTM"]
        .apply(format_multiple)
    )

    display["P/E NTM"] = (
        display["P/E NTM"]
        .apply(format_multiple)
    )

    display["TTM Revenue"] = (
        display["TTM Revenue"]
        .apply(format_revenue)
    )

    display["NTM Revenue"] = (
        display["NTM Revenue"]
        .apply(format_revenue)
    )

    display["P/S TTM"] = (
        display["P/S TTM"]
        .apply(format_multiple)
    )

    display["P/S NTM"] = (
        display["P/S NTM"]
        .apply(format_multiple)
    )

    return display


# ============================================================
# FEATURE
# ============================================================

def show_equity_table(
    performance_df,
    fundamental_df
):

    apply_equity_table_css()

    st.divider()

    st.header(
        "2. Equity Valuation"
    )

    st.caption(
        "Current valuation based on trailing and forward "
        "earnings and revenue estimates."
    )


    valuation_df = prepare_valuation_table(
        fundamental_df
    )


    if valuation_df.empty:

        st.warning(
            "No valuation data is currently available."
        )

        return


    filtered_df = apply_filters(
        valuation_df
    )


    # ========================================================
    # SORTING
    # ========================================================

    col1, col2 = st.columns(
        [2, 1]
    )

    with col1:

        sort_by = st.selectbox(
            "Sort by",
            [
                "Ticker",
                "Current Price",
                "P/E TTM",
                "P/E NTM",
                "P/S TTM",
                "P/S NTM",
            ],
            key="valuation_sort"
        )


    with col2:

        ascending = st.checkbox(
            "Ascending",
            value=True,
            key="valuation_ascending"
        )


    filtered_df = filtered_df.sort_values(
        by=sort_by,
        ascending=ascending,
        na_position="last"
    )


    st.write(
        f"**{len(filtered_df)} securities selected**"
    )


    # ========================================================
    # DISPLAY TABLE
    # ========================================================

    display_df = format_valuation_table(
        filtered_df
    )


    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=600,
    )


    st.caption(
        "P/E TTM = Current Price ÷ TTM EPS • "
        "P/E NTM = Current Price ÷ Forward EPS • "
        "P/S TTM = Market Cap ÷ TTM Revenue • "
        "P/S NTM = Market Cap ÷ Forward Revenue estimate"
    )
