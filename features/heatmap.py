import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from config import format_market_cap


def apply_heatmap_css():
    """CSS owned by the Performance Heat Map feature."""
    st.markdown(
        """
        <style>
        /* Performance Heat Map */
        .js-plotly-plot { width: 100% !important; }

        @media (max-width: 768px) {
            /* Add heatmap-specific mobile CSS here. */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

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

            "displaylogo": False,
        }
    )



def show_heatmap(performance_df, fundamental_df):
    apply_heatmap_css()
    st.divider()
    st.header("1. Performance Heat Map")

    heatmap_timeframe = st.radio(
        "Timeframe",
        ["Daily", "Weekly", "Monthly", "Semi-Annual", "Annual"],
        horizontal=True,
        key="heatmap_timeframe",
    )

    render_heatmap(performance_df, fundamental_df, heatmap_timeframe)
