import sqlite3

import pandas as pd

from app.config.settings import settings
from app.indicators.atr import calculate_atr
from app.indicators.rsi import calculate_rsi
from app.indicators.volume import calculate_avg_volume, calculate_volume_spike_ratio
from app.backtesting.models import BacktestSummary


SETUP_NAME = "small_cap_pre_breakout"


def create_backtest_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT NOT NULL,
            setup_name TEXT NOT NULL,
            sample_size INTEGER NOT NULL,
            win_rate_5d REAL,
            avg_return_5d REAL,
            win_rate_10d REAL,
            avg_return_10d REAL,
            win_rate_20d REAL,
            avg_return_20d REAL,
            avg_max_drawdown_20d REAL,
            best_return_20d REAL,
            worst_return_20d REAL
        );
        """
    )
    connection.commit()


def load_price_frame(connection: sqlite3.Connection, ticker: str) -> pd.DataFrame:
    rows = connection.execute(
        """
        SELECT ticker, date, open, high, low, close, adj_close, volume
        FROM price_data
        WHERE ticker = ?
        ORDER BY date ASC;
        """,
        (ticker.upper(),),
    ).fetchall()

    frame = pd.DataFrame([dict(row) for row in rows])

    if frame.empty:
        return frame

    frame["date"] = pd.to_datetime(frame["date"])

    numeric_columns = ["open", "high", "low", "close", "adj_close", "volume"]

    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame = frame.dropna(subset=["high", "low", "close", "volume"])
    frame = frame.sort_values("date").reset_index(drop=True)

    return frame


def add_setup_columns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()

    frame["rsi_14"] = calculate_rsi(frame["close"], period=14)
    frame["atr_14"] = calculate_atr(frame["high"], frame["low"], frame["close"], period=14)
    frame["avg_volume_20"] = calculate_avg_volume(frame["volume"], period=20)
    frame["volume_spike_ratio"] = calculate_volume_spike_ratio(frame["volume"], period=20)

    frame["high_52w"] = frame["high"].rolling(252, min_periods=60).max()
    frame["distance_from_52w_high_pct"] = (frame["close"] / frame["high_52w"] - 1) * 100

    frame["atr_14_prev"] = frame["atr_14"].shift(settings.atr_compression_lookback)
    frame["atr_compression_ratio"] = frame["atr_14"] / frame["atr_14_prev"].mask(
        frame["atr_14_prev"] == 0
    )

    frame["recent_close_mean"] = frame["close"].rolling(5).mean()
    frame["prior_close_mean"] = frame["close"].shift(5).rolling(15).mean()

    frame["setup_score"] = 0

    frame.loc[frame["volume_spike_ratio"] >= 1.2, "setup_score"] += 30
    frame.loc[(frame["rsi_14"] >= 40) & (frame["rsi_14"] <= 75), "setup_score"] += 25
    frame.loc[frame["atr_compression_ratio"] <= 1.15, "setup_score"] += 20
    frame.loc[frame["distance_from_52w_high_pct"] >= -35, "setup_score"] += 15
    frame.loc[frame["recent_close_mean"] > frame["prior_close_mean"], "setup_score"] += 10

    frame["is_setup"] = frame["setup_score"] >= 50

    return frame

def add_forward_returns(frame: pd.DataFrame) -> pd.DataFrame:
    frame = frame.copy()

    for days in [5, 10, 20]:
        frame[f"future_close_{days}d"] = frame["close"].shift(-days)
        frame[f"return_{days}d_pct"] = (
            (frame[f"future_close_{days}d"] / frame["close"] - 1) * 100
        )

    max_drawdowns = []

    for index, row in frame.iterrows():
        close_price = row["close"]
        future_window = frame.iloc[index + 1 : index + 21]

        if future_window.empty or pd.isna(close_price):
            max_drawdowns.append(pd.NA)
            continue

        lowest_low = future_window["low"].min()
        max_drawdown_pct = (lowest_low / close_price - 1) * 100
        max_drawdowns.append(max_drawdown_pct)

    frame["max_drawdown_20d_pct"] = max_drawdowns

    return frame


def _safe_mean(series: pd.Series) -> float | None:
    series = series.dropna()

    if series.empty:
        return None

    return round(float(series.mean()), 2)


def _safe_win_rate(series: pd.Series) -> float | None:
    series = series.dropna()

    if series.empty:
        return None

    return round(float((series > 0).mean() * 100), 2)


def _safe_max(series: pd.Series) -> float | None:
    series = series.dropna()

    if series.empty:
        return None

    return round(float(series.max()), 2)


def _safe_min(series: pd.Series) -> float | None:
    series = series.dropna()

    if series.empty:
        return None

    return round(float(series.min()), 2)


def backtest_ticker(connection: sqlite3.Connection, ticker: str) -> BacktestSummary | None:
    frame = load_price_frame(connection, ticker)

    if len(frame) < 80:
        return None

    frame = add_setup_columns(frame)
    frame = add_forward_returns(frame)

    setup_rows = frame[frame["is_setup"]].copy()
    setup_rows = setup_rows.dropna(subset=["return_5d_pct", "return_10d_pct", "return_20d_pct"])

    if setup_rows.empty:
        return None

    return BacktestSummary(
        ticker=ticker.upper(),
        setup_name=SETUP_NAME,
        sample_size=int(len(setup_rows)),
        win_rate_5d=_safe_win_rate(setup_rows["return_5d_pct"]),
        avg_return_5d=_safe_mean(setup_rows["return_5d_pct"]),
        win_rate_10d=_safe_win_rate(setup_rows["return_10d_pct"]),
        avg_return_10d=_safe_mean(setup_rows["return_10d_pct"]),
        win_rate_20d=_safe_win_rate(setup_rows["return_20d_pct"]),
        avg_return_20d=_safe_mean(setup_rows["return_20d_pct"]),
        avg_max_drawdown_20d=_safe_mean(setup_rows["max_drawdown_20d_pct"]),
        best_return_20d=_safe_max(setup_rows["return_20d_pct"]),
        worst_return_20d=_safe_min(setup_rows["return_20d_pct"]),
    )


def save_backtest_summaries(
    connection: sqlite3.Connection,
    summaries: list[BacktestSummary],
) -> int:
    if not summaries:
        return 0

    rows = [summary.to_db_row() for summary in summaries]

    connection.executemany(
        """
        INSERT INTO backtest_results (
            ticker,
            setup_name,
            sample_size,
            win_rate_5d,
            avg_return_5d,
            win_rate_10d,
            avg_return_10d,
            win_rate_20d,
            avg_return_20d,
            avg_max_drawdown_20d,
            best_return_20d,
            worst_return_20d
        )
        VALUES (
            :ticker,
            :setup_name,
            :sample_size,
            :win_rate_5d,
            :avg_return_5d,
            :win_rate_10d,
            :avg_return_10d,
            :win_rate_20d,
            :avg_return_20d,
            :avg_max_drawdown_20d,
            :best_return_20d,
            :worst_return_20d
        );
        """,
        rows,
    )

    connection.commit()
    return len(rows)


def run_backtest(connection: sqlite3.Connection, tickers: list[str]) -> dict[str, int]:
    create_backtest_schema(connection)

    summaries: list[BacktestSummary] = []

    for ticker in tickers:
        summary = backtest_ticker(connection, ticker)

        if summary is None:
            print(f"{ticker}: no historical setup found")
            continue

        summaries.append(summary)

        print(
            f"{ticker}: samples={summary.sample_size}, "
            f"20d win={summary.win_rate_20d}%, "
            f"20d avg={summary.avg_return_20d}%"
        )

    saved_count = save_backtest_summaries(connection, summaries)

    return {
        "tickers_scanned": len(tickers),
        "backtest_results_saved": saved_count,
    }