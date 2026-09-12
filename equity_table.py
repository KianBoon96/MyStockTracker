import streamlit as st
import pandas as pd

from config import format_market_cap, format_billions, format_percent, format_number


def apply_equity_table_css():
    """CSS owned by the Equity Returns / Fundamentals table feature."""
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


    col1, col2 = st.columns(2)


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



def show_equity_table(performance_df, fundamental_df):
    apply_equity_table_css()
    st.divider()
    st.header("2. Equity Returns, Volatility & Fundamentals")
    st.caption(
        "Filter the universe to compare companies across sectors, returns, "
        "volatility and forward estimates."
    )

    main_table = prepare_main_table(performance_df, fundamental_df)
    filtered_table = apply_filters(main_table)
    st.write(f"**{len(filtered_table)} securities selected**")

    table_view = st.radio(
        "Table view",
        ["Essential", "Full"],
        horizontal=True,
        key="table_view",
    )

    if table_view == "Essential":
        essential_columns = [
            "Ticker", "Category", "Market Cap", "Daily Return", "Weekly Return",
            "Monthly Return", "Semi-Annual Return", "Annual Return",
            "Monthly Volatility", "Semi-Annual Volatility", "Annual Volatility",
        ]
        essential_columns = [c for c in essential_columns if c in filtered_table.columns]
        table_to_display = filtered_table[essential_columns]
    else:
        table_to_display = filtered_table

    sort_options = [
        "Ticker", "Market Cap", "Daily Return", "Weekly Return", "Monthly Return",
        "Semi-Annual Return", "Annual Return", "Monthly Volatility",
        "Semi-Annual Volatility", "Annual Volatility",
    ]
    available_sort_options = [c for c in sort_options if c in table_to_display.columns]

    sort_col = st.selectbox("Sort by", available_sort_options, key="sort_col")
    sort_ascending = st.checkbox("Ascending", value=True, key="sort_ascending")

    table_to_display = table_to_display.sort_values(
        sort_col, ascending=sort_ascending, na_position="last"
    )
    display_table = format_main_table(table_to_display)
    st.dataframe(
        display_table, use_container_width=True, hide_index=True, height=600
    )
