from __future__ import annotations

import sqlite3

from app.telegram_bot.message_formatter import build_latest_telegram_signal_message


def test_build_latest_telegram_signal_message_includes_signal() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE signals (
            ticker TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            close_price REAL NOT NULL,
            volume_spike_ratio REAL,
            atr_compression_ratio REAL,
            rsi_14 REAL,
            entry_price REAL,
            stop_loss REAL,
            target_1 REAL,
            target_2 REAL,
            score INTEGER,
            reason TEXT,
            status TEXT DEFAULT 'open'
        );
        """
    )

    connection.execute(
        """
        INSERT INTO signals (
            ticker,
            signal_date,
            close_price,
            volume_spike_ratio,
            atr_compression_ratio,
            rsi_14,
            entry_price,
            stop_loss,
            target_1,
            target_2,
            score,
            reason,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            "TEST",
            "2024-01-01",
            10.0,
            1.5,
            0.9,
            55.0,
            10.1,
            9.25,
            11.0,
            11.5,
            80,
            "volume spike 1.50x; RSI setup zone 55.0",
            "open",
        ),
    )

    message = build_latest_telegram_signal_message(connection)

    assert "AI Stock Signals" in message
    assert "TEST" in message
    assert "Score 80" in message
    assert "Entry: $10.10" in message
    assert "volume spike 1.50x" in message


def test_build_latest_telegram_signal_message_handles_no_signals() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE signals (
            ticker TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            close_price REAL NOT NULL
        );
        """
    )

    message = build_latest_telegram_signal_message(connection)

    assert "No active signals found." in message


def test_build_latest_telegram_signal_message_handles_missing_table() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    message = build_latest_telegram_signal_message(connection)

    assert "No signals table found." in message