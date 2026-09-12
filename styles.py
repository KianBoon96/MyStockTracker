import streamlit as st


def apply_global_css():
    """Global layout/typography and dashboard-wide controls only."""
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.0rem !important;
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
                padding-left: 0.45rem !important;
                padding-right: 0.45rem !important;
            }
            h1 { font-size: 1.45rem !important; line-height: 1.2 !important; }
            h2 { font-size: 1.2rem !important; }
            h3 { font-size: 1rem !important; }
            p { font-size: 0.85rem !important; }
            div[data-testid="stMetric"] {
                padding: 7px !important;
                min-height: 65px !important;
                border-radius: 7px !important;
            }
            div[data-testid="stMetricLabel"] { font-size: 0.65rem !important; }
            div[data-testid="stMetricValue"] { font-size: 1.0rem !important; }
            div[role="radiogroup"] {
                gap: 0.2rem !important;
                flex-wrap: wrap !important;
            }
            div[role="radiogroup"] label { font-size: 0.76rem !important; }
            div[data-baseweb="select"] { font-size: 0.8rem !important; }
            button { min-height: 40px !important; }
            div[data-testid="stCaptionContainer"] { font-size: 0.72rem !important; }
            details summary { font-size: 0.84rem !important; }
        }

        @media (max-width: 480px) {
            .block-container {
                padding-left: 0.3rem !important;
                padding-right: 0.3rem !important;
            }
            h1 { font-size: 1.3rem !important; }
            h2 { font-size: 1.1rem !important; }
            div[data-testid="stMetric"] { padding: 6px !important; }
            div[data-testid="stMetricValue"] { font-size: 0.9rem !important; }
            div[data-testid="stMetricLabel"] { font-size: 0.6rem !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
