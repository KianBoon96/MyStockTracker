import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import (
    category_map,
    yf_symbol,
    RETURN_WINDOWS,
    VOL_WINDOWS,
)


# ============================================================
# PRICE DATA
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def download_price_data(ticker_list):

    price_data = {}

    def download_one(ticker):

        symbol = yf_symbol(ticker)

        try:

            data = yf.download(
                symbol,
                period="4y",
                interval="1d",
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if data is None or data.empty:
                return ticker, None

            if isinstance(data.columns, pd.MultiIndex):

                if "Close" not in data.columns.get_level_values(0):
                    return ticker, None

                close = data["Close"]

                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]

            else:

                if "Close" not in data.columns:
                    return ticker, None

                close = data["Close"]

            close = pd.to_numeric(
                close,
                errors="coerce"
            ).dropna()

            if len(close) < 2:
                return ticker, None

            return ticker, close

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

            for ticker in ticker_list
        }

        for future in as_completed(futures):

            try:

                ticker, prices = future.result()

                if prices is not None:
                    price_data[ticker] = prices

            except Exception:
                pass

    return price_data


# ============================================================
# FUNDAMENTAL DATA
# ============================================================

@st.cache_data(
    ttl=21600,
    show_spinner=False
)
def get_fundamental_data(ticker_list):

    rows = []

    def get_one(ticker):

        result = {
            "Ticker": ticker,
            "Category": category_map.get(
                ticker,
                "Other"
            ),

            "Current Price": np.nan,
            "Market Cap": np.nan,

            "TTM Adjusted EPS": np.nan,
            "Forward Adjusted EPS": np.nan,

            "TTM Revenue": np.nan,
            "Forward Revenue": np.nan,
        }

        symbol = yf_symbol(ticker)

        try:

            stock = yf.Ticker(symbol)


            # =================================================
            # CURRENT PRICE / MARKET CAP / TTM REVENUE
            # =================================================

            try:

                info = stock.info or {}

                current_price = (
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                )

                if current_price is not None:

                    result["Current Price"] = pd.to_numeric(
                        current_price,
                        errors="coerce"
                    )


                market_cap = info.get("marketCap")

                if market_cap is not None:

                    result["Market Cap"] = pd.to_numeric(
                        market_cap,
                        errors="coerce"
                    )


                total_revenue = info.get("totalRevenue")

                if total_revenue is not None:

                    result["TTM Revenue"] = pd.to_numeric(
                        total_revenue,
                        errors="coerce"
                    )

            except Exception:
                pass


            # =================================================
            # TTM EPS
            #
            # Sum latest 4 quarters of Yahoo reported EPS.
            # =================================================

            try:

                earnings_history = (
                    stock.get_earnings_history()
                )

                if (
                    earnings_history is not None
                    and not earnings_history.empty
                    and "epsActual" in earnings_history.columns
                ):

                    earnings_history = (
                        earnings_history.copy()
                    )

                    eps_actual = pd.to_numeric(
                        earnings_history["epsActual"],
                        errors="coerce"
                    ).dropna()


                    if len(eps_actual) >= 4:

                        # get_earnings_history normally runs
                        # oldest -> newest, so use last 4
                        ttm_eps = (
                            eps_actual
                            .iloc[-4:]
                            .sum()
                        )

                        result[
                            "TTM Adjusted EPS"
                        ] = ttm_eps

            except Exception:
                pass


            # =================================================
            # FORWARD EPS
            #
            # Yahoo analyst consensus EPS estimate.
            # Prefer +1y, then 0y as fallback.
            # =================================================

            try:

                earnings_estimates = (
                    stock.get_earnings_estimate()
                )

                if (
                    earnings_estimates is not None
                    and not earnings_estimates.empty
                ):

                    forward_eps = np.nan


                    if "+1y" in earnings_estimates.index:

                        try:

                            forward_eps = pd.to_numeric(
                                earnings_estimates.loc[
                                    "+1y",
                                    "avg"
                                ],
                                errors="coerce"
                            )

                        except Exception:
                            pass


                    if (
                        pd.isna(forward_eps)
                        and "0y" in earnings_estimates.index
                    ):

                        try:

                            forward_eps = pd.to_numeric(
                                earnings_estimates.loc[
                                    "0y",
                                    "avg"
                                ],
                                errors="coerce"
                            )

                        except Exception:
                            pass


                    result[
                        "Forward Adjusted EPS"
                    ] = forward_eps

            except Exception:
                pass


            # =================================================
            # FORWARD REVENUE
            #
            # Yahoo analyst consensus revenue estimate.
            # Prefer +1y, then 0y as fallback.
            # =================================================

            try:

                revenue_estimates = (
                    stock.get_revenue_estimate()
                )

                if (
                    revenue_estimates is not None
                    and not revenue_estimates.empty
                ):

                    forward_revenue = np.nan


                    if "+1y" in revenue_estimates.index:

                        try:

                            forward_revenue = pd.to_numeric(
                                revenue_estimates.loc[
                                    "+1y",
                                    "avg"
                                ],
                                errors="coerce"
                            )

                        except Exception:
                            pass


                    if (
                        pd.isna(forward_revenue)
                        and "0y" in revenue_estimates.index
                    ):

                        try:

                            forward_revenue = pd.to_numeric(
                                revenue_estimates.loc[
                                    "0y",
                                    "avg"
                                ],
                                errors="coerce"
                            )

                        except Exception:
                            pass


                    result[
                        "Forward Revenue"
                    ] = forward_revenue

            except Exception:
                pass


        except Exception:
            pass

        return result


    # ========================================================
    # PARALLEL FUNDAMENTALS DOWNLOAD
    # ========================================================

    with ThreadPoolExecutor(
        max_workers=6
    ) as executor:

        futures = {
            executor.submit(
                get_one,
                ticker
            ): ticker

            for ticker in ticker_list
        }


        for future in as_completed(futures):

            try:

                rows.append(
                    future.result()
                )

            except Exception:
                pass


    return pd.DataFrame(rows)


# ============================================================
# PERFORMANCE CALCULATION
# ============================================================

def calculate_performance(price_data):

    rows = []

    for ticker, prices in price_data.items():

        try:

            prices = pd.to_numeric(
                prices,
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
                "Ticker": ticker,
                "Category": category_map.get(
                    ticker,
                    "Other"
                ),
            }


            # =================================================
            # RETURNS
            # =================================================

            for label, window in RETURN_WINDOWS.items():

                column = f"{label} Return"

                if len(prices) > window:

                    row[column] = (
                        prices.iloc[-1]
                        /
                        prices.iloc[-(window + 1)]
                    ) - 1

                else:

                    row[column] = np.nan


            # =================================================
            # REALISED VOLATILITY
            # =================================================

            for label, window in VOL_WINDOWS.items():

                column = f"{label} Volatility"

                if len(daily_returns) >= window:

                    recent_returns = (
                        daily_returns
                        .tail(window)
                    )

                    volatility = (
                        recent_returns.std()
                        * np.sqrt(252)
                    )

                    row[column] = volatility

                else:

                    row[column] = np.nan


            rows.append(row)

        except Exception:
            continue


    return pd.DataFrame(rows)
