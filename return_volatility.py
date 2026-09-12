import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px


def apply_return_volatility_css():
    """CSS owned by the Return vs Realised Volatility feature."""
    st.markdown(
        """
        <style>
        .js-plotly-plot { width: 100% !important; }

        @media (max-width: 768px) {
            /* Add scatterplot-specific mobile CSS here. */
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def show_return_volatility(performance_df, fundamental_df):
    apply_return_volatility_css()

    st.divider()

    st.header(
        "3. Return vs. Realised Volatility"
    )


    st.caption(

        "The chart is divided into four quadrants "
        "using the median return and median realised "
        "volatility of the selected universe."
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
        # QUADRANT BOUNDARIES
        # ========================================================

        median_vol = rv_df[
            vol_col
        ].median()


        median_return = rv_df[
            return_col
        ].median()


        # ========================================================
        # QUADRANT CLASSIFICATION
        # ========================================================

        def classify_quadrant(row):

            high_return = (
                row[return_col]
                >=
                median_return
            )


            low_volatility = (
                row[vol_col]
                <=
                median_vol
            )


            if high_return and low_volatility:

                return "High Return / Low Volatility"


            elif high_return and not low_volatility:

                return "High Return / High Volatility"


            elif not high_return and low_volatility:

                return "Low Return / Low Volatility"


            else:

                return "Low Return / High Volatility"


        rv_df["Quadrant"] = rv_df.apply(

            classify_quadrant,

            axis=1
        )


        # ========================================================
        # QUADRANT COLORS
        # ========================================================

        quadrant_colors = {

            "High Return / Low Volatility":
                "#00E676",

            "High Return / High Volatility":
                "#FFB300",

            "Low Return / Low Volatility":
                "#42A5F5",

            "Low Return / High Volatility":
                "#EF5350",
        }


        # ========================================================
        # MOBILE DISPLAY MODE
        # ========================================================

        scatter_view = st.radio(

            "Scatterplot view",

            [

                "Quadrants",

                "By Category",

            ],

            horizontal=True,

            key="scatter_view",
        )


        # ========================================================
        # OPTIONAL TICKER HIGHLIGHT
        # ========================================================

        ticker_options = [
            "None"
        ] + sorted(
            rv_df["Ticker"]
            .dropna()
            .unique()
            .tolist()
        )


        highlight_ticker = st.selectbox(

            "Highlight ticker",

            ticker_options,

            key="scatter_highlight",
        )


        # ========================================================
        # BUILD FIGURE
        # ========================================================

        fig = go.Figure()


        # ========================================================
        # QUADRANT BACKGROUNDS
        # ========================================================

        x_min = rv_df[vol_col].min()

        x_max = rv_df[vol_col].max()

        y_min = rv_df[return_col].min()

        y_max = rv_df[return_col].max()


        # Add a little padding to the boundaries.

        x_padding = (
            (x_max - x_min) * 0.08
            if x_max > x_min
            else 0.02
        )


        y_padding = (
            (y_max - y_min) * 0.08
            if y_max > y_min
            else 0.02
        )


        x_axis_min = x_min - x_padding

        x_axis_max = x_max + x_padding

        y_axis_min = y_min - y_padding

        y_axis_max = y_max + y_padding


        # --------------------------------------------------------
        # TOP LEFT
        # High Return / Low Volatility
        # --------------------------------------------------------

        fig.add_shape(

            type="rect",

            x0=x_axis_min,

            x1=median_vol,

            y0=median_return,

            y1=y_axis_max,

            fillcolor="#00E676",

            opacity=0.08,

            line_width=0,

            layer="below",
        )


        # --------------------------------------------------------
        # TOP RIGHT
        # High Return / High Volatility
        # --------------------------------------------------------

        fig.add_shape(

            type="rect",

            x0=median_vol,

            x1=x_axis_max,

            y0=median_return,

            y1=y_axis_max,

            fillcolor="#FFB300",

            opacity=0.08,

            line_width=0,

            layer="below",
        )


        # --------------------------------------------------------
        # BOTTOM LEFT
        # Low Return / Low Volatility
        # --------------------------------------------------------

        fig.add_shape(

            type="rect",

            x0=x_axis_min,

            x1=median_vol,

            y0=y_axis_min,

            y1=median_return,

            fillcolor="#42A5F5",

            opacity=0.08,

            line_width=0,

            layer="below",
        )


        # --------------------------------------------------------
        # BOTTOM RIGHT
        # Low Return / High Volatility
        # --------------------------------------------------------

        fig.add_shape(

            type="rect",

            x0=median_vol,

            x1=x_axis_max,

            y0=y_axis_min,

            y1=median_return,

            fillcolor="#EF5350",

            opacity=0.08,

            line_width=0,

            layer="below",
        )


        # ========================================================
        # SCATTER TRACES
        # ========================================================

        if scatter_view == "Quadrants":

            for quadrant in [

                "High Return / Low Volatility",

                "High Return / High Volatility",

                "Low Return / Low Volatility",

                "Low Return / High Volatility",

            ]:

                subset = rv_df[
                    rv_df["Quadrant"]
                    ==
                    quadrant
                ]


                if subset.empty:

                    continue


                fig.add_trace(

                    go.Scatter(

                        x=subset[vol_col],

                        y=subset[return_col],

                        mode="markers+text",

                        name=quadrant,

                        text=subset["Ticker"],

                        textposition="top center",

                        textfont=dict(
                            size=9
                        ),

                        marker=dict(

                            size=10,

                            color=quadrant_colors[
                                quadrant
                            ],

                            line=dict(

                                width=1,

                                color="#111111"
                            ),

                            opacity=0.88,
                        ),

                        customdata=np.column_stack(

                            [

                                subset["Ticker"],

                                subset["Category"],

                                subset["Market Cap"],

                                subset["Return / Volatility"],

                                subset["Quadrant"],

                            ]

                        ),

                        hovertemplate=(

                            "<b>%{customdata[0]}</b>"

                            "<br>Category: "
                            "%{customdata[1]}"

                            "<br>Return: "
                            "%{y:+.2%}"

                            "<br>Volatility: "
                            "%{x:.2%}"

                            "<br>Return / Vol: "
                            "%{customdata[3]:.2f}"

                            "<br>Quadrant: "
                            "%{customdata[4]}"

                            "<extra></extra>"
                        ),
                    )
                )


        else:

            categories = sorted(

                rv_df["Category"]
                .dropna()
                .unique()
                .tolist()
            )


            category_colors = px.colors.qualitative.Dark24


            for i, category in enumerate(
                categories
            ):

                subset = rv_df[
                    rv_df["Category"]
                    ==
                    category
                ]


                fig.add_trace(

                    go.Scatter(

                        x=subset[vol_col],

                        y=subset[return_col],

                        mode="markers+text",

                        name=category,

                        text=subset["Ticker"],

                        textposition="top center",

                        textfont=dict(
                            size=8
                        ),

                        marker=dict(

                            size=9,

                            color=category_colors[
                                i % len(category_colors)
                            ],

                            opacity=0.78,

                            line=dict(

                                width=0.7,

                                color="#111111"
                            )
                        ),

                        customdata=np.column_stack(

                            [

                                subset["Ticker"],

                                subset["Category"],

                                subset["Market Cap"],

                                subset["Return / Volatility"],

                                subset["Quadrant"],

                            ]

                        ),

                        hovertemplate=(

                            "<b>%{customdata[0]}</b>"

                            "<br>Category: "
                            "%{customdata[1]}"

                            "<br>Return: "
                            "%{y:+.2%}"

                            "<br>Volatility: "
                            "%{x:.2%}"

                            "<br>Return / Vol: "
                            "%{customdata[3]:.2f}"

                            "<br>Quadrant: "
                            "%{customdata[4]}"

                            "<extra></extra>"
                        ),
                    )
                )


        # ========================================================
        # HIGHLIGHT SELECTED TICKER
        # ========================================================

        if (
            highlight_ticker != "None"
            and
            highlight_ticker in rv_df["Ticker"].values
        ):

            selected = rv_df[
                rv_df["Ticker"]
                ==
                highlight_ticker
            ].iloc[0]


            fig.add_trace(

                go.Scatter(

                    x=[selected[vol_col]],

                    y=[selected[return_col]],

                    mode="markers+text",

                    name=f"★ {highlight_ticker}",

                    text=[highlight_ticker],

                    textposition="top center",

                    textfont=dict(

                        size=13,

                        color="white"
                    ),

                    marker=dict(

                        size=18,

                        color="#FFFFFF",

                        symbol="circle-open",

                        line=dict(

                            width=3,

                            color="#FFFFFF"
                        )
                    ),

                    hovertemplate=(

                        f"<b>{highlight_ticker}</b>"

                        "<br>Highlighted security"

                        "<extra></extra>"
                    ),
                )
            )


        # ========================================================
        # MEDIAN LINES
        # ========================================================

        fig.add_hline(

            y=median_return,

            line_dash="dash",

            line_color="#FFFFFF",

            opacity=0.55,

            line_width=1.5,
        )


        fig.add_vline(

            x=median_vol,

            line_dash="dash",

            line_color="#FFFFFF",

            opacity=0.55,

            line_width=1.5,
        )


        # ========================================================
        # QUADRANT LABELS
        # ========================================================

        fig.add_annotation(

            x=(
                x_axis_min
                +
                median_vol
            ) / 2,

            y=(
                median_return
                +
                y_axis_max
            ) / 2,

            text="<b>HIGH RETURN<br>LOW VOL</b>",

            showarrow=False,

            font=dict(

                size=11,

                color="#00E676"
            ),

            align="center",

            opacity=0.8,
        )


        fig.add_annotation(

            x=(
                median_vol
                +
                x_axis_max
            ) / 2,

            y=(
                median_return
                +
                y_axis_max
            ) / 2,

            text="<b>HIGH RETURN<br>HIGH VOL</b>",

            showarrow=False,

            font=dict(

                size=11,

                color="#FFB300"
            ),

            align="center",

            opacity=0.8,
        )


        fig.add_annotation(

            x=(
                x_axis_min
                +
                median_vol
            ) / 2,

            y=(
                y_axis_min
                +
                median_return
            ) / 2,

            text="<b>LOW RETURN<br>LOW VOL</b>",

            showarrow=False,

            font=dict(

                size=11,

                color="#42A5F5"
            ),

            align="center",

            opacity=0.8,
        )


        fig.add_annotation(

            x=(
                median_vol
                +
                x_axis_max
            ) / 2,

            y=(
                y_axis_min
                +
                median_return
            ) / 2,

            text="<b>LOW RETURN<br>HIGH VOL</b>",

            showarrow=False,

            font=dict(

                size=11,

                color="#EF5350"
            ),

            align="center",

            opacity=0.8,
        )


        # ========================================================
        # AXES
        # ========================================================

        fig.update_xaxes(

            title="Realised Volatility",

            tickformat=".0%",

            range=[

                x_axis_min,

                x_axis_max,

            ],

            showgrid=True,

            gridcolor="rgba(255,255,255,0.08)",

            zeroline=False,

            fixedrange=True,

            title_font=dict(
                size=11
            ),

            tickfont=dict(
                size=9
            ),
        )


        fig.update_yaxes(

            title=f"{rv_timeframe} Return",

            tickformat=".0%",

            range=[

                y_axis_min,

                y_axis_max,

            ],

            showgrid=True,

            gridcolor="rgba(255,255,255,0.08)",

            zeroline=False,

            fixedrange=True,

            title_font=dict(
                size=11
            ),

            tickfont=dict(
                size=9
            ),
        )


        # ========================================================
        # MOBILE-FRIENDLY LAYOUT
        # ========================================================

        fig.update_layout(

            height=620,

            autosize=True,

            hovermode="closest",

            dragmode=False,

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            margin=dict(

                l=48,

                r=15,

                t=30,

                b=50
            ),

            legend=dict(

                orientation="h",

                yanchor="bottom",

                y=1.01,

                xanchor="left",

                x=0,

                font=dict(
                    size=8
                ),

                bgcolor="rgba(0,0,0,0)",
            ),
        )


        # ========================================================
        # MOBILE CONFIG
        # ========================================================

        st.plotly_chart(

            fig,

            use_container_width=True,

            config={

                "responsive": True,
                "displayModeBar": False,
                "displaylogo": False,
            }
        )
