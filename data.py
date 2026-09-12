# Yahoo Finance data retrieval and performance calculations

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import category_map, yf_symbol, RETURN_WINDOWS, VOL_WINDOWS

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


            if (
                data is None
                or data.empty
            ):

                return ticker, None


            # ------------------------------------------------
            # MULTIINDEX
            # ------------------------------------------------

            if isinstance(
                data.columns,
                pd.MultiIndex
            ):

                if (
                    "Close"
                    not in
                    data.columns
                    .get_level_values(0)
                ):

                    return ticker, None


                close = data["Close"]


                if isinstance(
                    close,
                    pd.DataFrame
                ):

                    close = close.iloc[:, 0]


            # ------------------------------------------------
            # NORMAL COLUMNS
            # ------------------------------------------------

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


    # ========================================================
    # PARALLEL DOWNLOAD
    # ========================================================

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


        for future in as_completed(
            futures
        ):

            try:

                ticker, prices = (
                    future.result()
                )


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

            "TTM EPS": np.nan,
            "NTM EPS": np.nan,

            "TTM Revenue": np.nan,
            "NTM Revenue": np.nan,
        }

        symbol = yf_symbol(ticker)

        try:

            stock = yf.Ticker(symbol)

            # =================================================
            # YAHOO INFO
            # =================================================

            try:

                info = stock.info or {}

                # Current share price
                current_price = (
                    info.get("currentPrice")
                    or info.get("regularMarketPrice")
                )

                if current_price is not None:
                    result["Current Price"] = pd.to_numeric(
                        current_price,
                        errors="coerce"
                    )

                # Market capitalisation
                market_cap = info.get("marketCap")

                if market_cap is not None:
                    result["Market Cap"] = pd.to_numeric(
                        market_cap,
                        errors="coerce"
                    )

                # Trailing 12-month EPS
                trailing_eps = info.get("trailingEps")

                if trailing_eps is not None:
                    result["TTM EPS"] = pd.to_numeric(
                        trailing_eps,
                        errors="coerce"
                    )

                # Forward / next 12-month EPS
                forward_eps = info.get("forwardEps")

                if forward_eps is not None:
                    result["NTM EPS"] = pd.to_numeric(
                        forward_eps,
                        errors="coerce"
                    )

                # Trailing 12-month revenue
                total_revenue = info.get("totalRevenue")

                if total_revenue is not None:
                    result["TTM Revenue"] = pd.to_numeric(
                        total_revenue,
                        errors="coerce"
                    )

            except Exception:
                pass

            # =================================================
            # FORWARD REVENUE ESTIMATE
            # =================================================
            #
            # Yahoo Finance / yfinance does not consistently
            # expose a true rolling NTM revenue number.
            #
            # We therefore use the next fiscal-year analyst
            # revenue estimate as the forward revenue proxy.
            # =================================================

            try:

                revenue_estimates = (
                    stock.get_revenue_estimate()
                )

                if (
                    revenue_estimates is not None
                    and not revenue_estimates.empty
                ):

                    # Prefer +1y = next fiscal year
                    if "+1y" in revenue_estimates.index:

                        row = revenue_estimates.loc["+1y"]

                        result["NTM Revenue"] = pd.to_numeric(
                            row.get(
                                "avg",
                                np.nan
                            ),
                            errors="coerce"
                        )

                    # Fallback to current FY estimate
                    elif "0y" in revenue_estimates.index:

                        row = revenue_estimates.loc["0y"]

                        result["NTM Revenue"] = pd.to_numeric(
                            row.get(
                                "avg",
                                np.nan
                            ),
                            errors="coerce"
                        )

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

        for future in as_completed(
            futures
        ):

            try:
                rows.append(
                    future.result()
                )

            except Exception:
                pass

    return pd.DataFrame(rows)

            # =================================================
            # MARKET CAP
            # =================================================

            try:

                info = stock.info

                market_cap = info.get(
                    "marketCap"
                )


                if market_cap is not None:

                    result[
                        "Market Cap"
                    ] = pd.to_numeric(

                        market_cap,

                        errors="coerce"
                    )

            except Exception:

                pass


            # =================================================
            # EPS ESTIMATES
            # =================================================

            try:

                estimates = (
                    stock.get_earnings_estimate()
                )


                if (
                    estimates is not None
                    and not estimates.empty
                ):

                    if "+1y" in estimates.index:

                        row = estimates.loc["+1y"]


                        result[
                            "EPS Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "EPS Growth Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )


                    if "+2y" in estimates.index:

                        row = estimates.loc["+2y"]


                        result[
                            "EPS Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "EPS Growth Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )

            except Exception:

                pass


            # =================================================
            # REVENUE ESTIMATES
            # =================================================

            try:

                revenue_estimates = (
                    stock.get_revenue_estimate()
                )


                if (
                    revenue_estimates is not None
                    and not revenue_estimates.empty
                ):

                    if "+1y" in revenue_estimates.index:

                        row = revenue_estimates.loc["+1y"]


                        result[
                            "Revenue Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "Revenue Growth Next Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )


                    if "+2y" in revenue_estimates.index:

                        row = revenue_estimates.loc["+2y"]


                        result[
                            "Revenue Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "avg",
                                np.nan
                            ),

                            errors="coerce"
                        )


                        result[
                            "Revenue Growth Following Year"
                        ] = pd.to_numeric(

                            row.get(
                                "growth",
                                np.nan
                            ),

                            errors="coerce"
                        )

            except Exception:

                pass


        except Exception:

            pass


        return result


    # ========================================================
    # PARALLEL FUNDAMENTALS
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


        for future in as_completed(
            futures
        ):

            try:

                rows.append(
                    future.result()
                )

            except Exception:

                pass


    return pd.DataFrame(
        rows
    )


# ============================================================
# PERFORMANCE CALCULATION
# ============================================================

def calculate_performance(
    price_data
):

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

            for label, window in (
                RETURN_WINDOWS.items()
            ):

                column = (
                    f"{label} Return"
                )


                if len(prices) > window:

                    row[column] = (

                        prices.iloc[-1]

                        /

                        prices.iloc[
                            -(window + 1)
                        ]

                    ) - 1


                else:

                    row[column] = np.nan


            # =================================================
            # REALISED VOLATILITY
            # =================================================

            for label, window in (
                VOL_WINDOWS.items()
            ):

                column = (
                    f"{label} Volatility"
                )


                if (
                    len(daily_returns)
                    >= window
                ):

                    recent_returns = (
                        daily_returns
                        .tail(window)
                    )


                    volatility = (

                        recent_returns.std()

                        *

                        np.sqrt(252)
                    )


                    row[column] = volatility


                else:

                    row[column] = np.nan


            rows.append(
                row
            )


        except Exception:

            continue


    return pd.DataFrame(
        rows
    )

