from __future__ import annotations

import sqlite3

import pandas as pd

from app.signals.signal_engine import generate_signal_for_ticker


def _build_strong_setup_rows() -> list[dict[str, object]]:
    rows = []
    dates = pd.date_range("2024-01-01", periods=80, freq="D")

    for index, date in enumerate(dates):
        close_price = 10 + index * 0.05
        volume = 5_000_000 if index == 79 else 1_000_000

        rows.append(
            {
                "ticker": "TEST",
                "date": date.date().isoformat(),
                "open": close_price - 0.1,
                "high": close_price + 0.2,
                "low": close_price - 0.2,
                "close": close_price,
                "adj_close": close_price,
                "volume": volume,
            }
        )

    return rows


def test_generate_signal_for_ticker_returns_signal_for_strong_setup() -> None:
    rows = _build_strong_setup_rows()

    signal = generate_signal_for_ticker("TEST", rows)

    assert signal is not None
    assert signal.ticker == "TEST"
    assert signal.score >= 60
    assert signal.entry_price > signal.close_price
    assert signal.target_1 > signal.close_price
    assert signal.stop_loss < signal.close_price


def test_generate_signal_for_ticker_returns_none_when_not_enough_data() -> None:
    rows = [
        {
            "ticker": "TEST",
            "date": "2024-01-01",
            "open": 10,
            "high": 11,
            "low": 9,
            "close": 10,
            "adj_close": 10,
            "volume": 1000,
        }
    ]

    signal = generate_signal_for_ticker("TEST", rows)

    assert signal is None


def test_generate_signal_for_ticker_accepts_sqlite_rows() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE price_data (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL,
            volume INTEGER
        );
        """
    )

    for row in _build_strong_setup_rows():
        connection.execute(
            """
            INSERT INTO price_data (
                ticker, date, open, high, low, close, adj_close, volume
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                row["ticker"],
                row["date"],
                row["open"],
                row["high"],
                row["low"],
                row["close"],
                row["adj_close"],
                row["volume"],
            ),
        )

    rows = connection.execute(
        """
        SELECT ticker, date, open, high, low, close, adj_close, volume
        FROM price_data
        ORDER BY date ASC;
        """
    ).fetchall()

    signal = generate_signal_for_ticker("TEST", rows)

    assert signal is not None
    assert signal.to_signal_table_row()["ticker"] == "TEST"