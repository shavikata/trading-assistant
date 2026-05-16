from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.storage.database import get_connection
from app.storage.schema import create_schema


st.set_page_config(
    page_title="Trading Assistant MVP",
    page_icon="📈",
    layout="wide",
)


def table_exists(connection, table_name: str) -> bool:
    row = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = ?;
        """,
        (table_name,),
    ).fetchone()

    return row is not None


def get_columns(connection, table_name: str) -> list[str]:
    if not table_exists(connection, table_name):
        return []

    rows = connection.execute(f"PRAGMA table_info({table_name});").fetchall()
    return [row["name"] for row in rows]


def read_sql_or_empty(connection, query: str, table_name: str) -> pd.DataFrame:
    if not table_exists(connection, table_name):
        return pd.DataFrame()

    return pd.read_sql_query(query, connection)


@st.cache_data(ttl=60)
def load_data() -> dict[str, pd.DataFrame]:
    with get_connection() as connection:
        create_schema(connection)

        universe = read_sql_or_empty(
            connection,
            """
            SELECT *
            FROM stock_universe
            ORDER BY ticker;
            """,
            "stock_universe",
        )

        prices = read_sql_or_empty(
            connection,
            """
            SELECT ticker, date, open, high, low, close, adj_close, volume
            FROM price_data
            ORDER BY ticker, date;
            """,
            "price_data",
        )

        signals = read_sql_or_empty(
            connection,
            """
            SELECT *
            FROM signals
            ORDER BY signal_date DESC, ticker ASC;
            """,
            "signals",
        )

        pipeline_columns = get_columns(connection, "pipeline_runs")

        if "started_at" in pipeline_columns:
            runs_order_column = "started_at"
        else:
            runs_order_column = "id"

        runs = read_sql_or_empty(
            connection,
            f"""
            SELECT *
            FROM pipeline_runs
            ORDER BY {runs_order_column} DESC
            LIMIT 20;
            """,
            "pipeline_runs",
        )

        backtests = read_sql_or_empty(
            connection,
            """
            SELECT *
            FROM backtest_results
            ORDER BY run_at DESC, ticker ASC;
            """,
            "backtest_results",
        )

    return {
        "universe": universe,
        "prices": prices,
        "signals": signals,
        "runs": runs,
        "backtests": backtests,
    }


def select_available_columns(
    dataframe: pd.DataFrame,
    wanted_columns: list[str],
) -> pd.DataFrame:
    available_columns = [column for column in wanted_columns if column in dataframe.columns]

    if not available_columns:
        return dataframe

    return dataframe[available_columns]


def main() -> None:
    st.title("📈 Trading Assistant MVP")
    st.caption("Small-cap stock signal dashboard")

    if st.button("Refresh dashboard"):
        st.cache_data.clear()
        st.rerun()

    data = load_data()

    universe = data["universe"]
    prices = data["prices"]
    signals = data["signals"]
    runs = data["runs"]
    backtests = data["backtests"]

    total_tickers = len(universe)
    total_price_rows = len(prices)
    total_signals = len(signals)
    total_backtests = len(backtests)

    latest_signal_date = "N/A"

    if not signals.empty and "signal_date" in signals.columns:
        latest_signal_date = str(signals["signal_date"].max())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Tickers", total_tickers)
    col2.metric("Price rows", total_price_rows)
    col3.metric("Signals", total_signals)
    col4.metric("Backtest rows", total_backtests)

    st.caption(f"Latest signal date: {latest_signal_date}")

    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Signals",
            "Backtesting",
            "Price chart",
            "Universe",
            "Pipeline runs",
        ]
    )

    with tab1:
        st.subheader("Latest signals")

        if signals.empty:
            st.warning("No signals yet. Run the signal job first.")
        else:
            wanted_columns = [
                "signal_date",
                "ticker",
                "close_price",
                "entry_price",
                "stop_loss",
                "target_1",
                "target_2",
                "volume_spike_ratio",
                "atr_compression_ratio",
                "rsi_14",
                "status",
                "reason",
            ]

            st.dataframe(
                select_available_columns(signals, wanted_columns),
                use_container_width=True,
                hide_index=True,
            )

    with tab2:
        st.subheader("Backtesting / OddsMaker-lite")

        if backtests.empty:
            st.warning("No backtest results yet. Run: python -m scripts.run_backtest")
        else:
            wanted_columns = [
                "run_at",
                "ticker",
                "setup_name",
                "sample_size",
                "win_rate_5d",
                "avg_return_5d",
                "win_rate_10d",
                "avg_return_10d",
                "win_rate_20d",
                "avg_return_20d",
                "avg_max_drawdown_20d",
                "best_return_20d",
                "worst_return_20d",
            ]

            clean_backtests = select_available_columns(backtests, wanted_columns)

            st.dataframe(
                clean_backtests,
                use_container_width=True,
                hide_index=True,
            )

            if "ticker" in backtests.columns and "avg_return_20d" in backtests.columns:
                latest_by_ticker = (
                    backtests.sort_values("run_at")
                    .groupby("ticker", as_index=False)
                    .tail(1)
                    .sort_values("avg_return_20d", ascending=False)
                )

                st.subheader("Best setups by 20-day average return")

                chart_data = latest_by_ticker.set_index("ticker")["avg_return_20d"]
                st.bar_chart(chart_data, use_container_width=True)

    with tab3:
        st.subheader("Price chart")

        if prices.empty:
            st.warning("No price data yet. Run market data download first.")
        else:
            available_tickers = sorted(prices["ticker"].dropna().unique().tolist())

            selected_ticker = st.selectbox(
                "Choose ticker",
                available_tickers,
            )

            ticker_prices = prices[prices["ticker"] == selected_ticker].copy()
            ticker_prices["date"] = pd.to_datetime(ticker_prices["date"])
            ticker_prices = ticker_prices.sort_values("date")

            st.line_chart(
                ticker_prices.set_index("date")["close"],
                use_container_width=True,
            )

            st.dataframe(
                ticker_prices.tail(20).sort_values("date", ascending=False),
                use_container_width=True,
                hide_index=True,
            )

    with tab4:
        st.subheader("Stock universe")

        if universe.empty:
            st.warning("Universe is empty. Run refresh universe first.")
        else:
            st.dataframe(
                universe,
                use_container_width=True,
                hide_index=True,
            )

    with tab5:
        st.subheader("Pipeline runs")

        if runs.empty:
            st.warning("No pipeline runs yet.")
        else:
            st.dataframe(
                runs,
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    main()