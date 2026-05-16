from __future__ import annotations

import sqlite3

from app.reports.report_builder import build_latest_signal_report


def test_build_latest_signal_report_includes_signal_and_backtest() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE signals (
            ticker TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            close_price REAL NOT NULL,
            volume INTEGER,
            volume_spike_ratio REAL,
            atr_compression_ratio REAL,
            rsi_14 REAL,
            distance_from_52w_high_pct REAL,
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
        CREATE TABLE backtest_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at TEXT DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT NOT NULL,
            setup_name TEXT NOT NULL,
            sample_size INTEGER NOT NULL,
            win_rate_20d REAL,
            avg_return_20d REAL,
            avg_max_drawdown_20d REAL
        );
        """
    )

    connection.execute(
        """
        INSERT INTO signals (
            ticker,
            signal_date,
            close_price,
            volume,
            volume_spike_ratio,
            atr_compression_ratio,
            rsi_14,
            distance_from_52w_high_pct,
            entry_price,
            stop_loss,
            target_1,
            target_2,
            score,
            reason,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        (
            "TEST",
            "2024-01-01",
            10.0,
            1_000_000,
            1.5,
            0.9,
            55.0,
            -12.5,
            10.1,
            9.25,
            11.0,
            11.5,
            80,
            "volume spike 1.50x; RSI setup zone 55.0",
            "open",
        ),
    )

    connection.execute(
        """
        INSERT INTO backtest_results (
            ticker,
            setup_name,
            sample_size,
            win_rate_20d,
            avg_return_20d,
            avg_max_drawdown_20d
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """,
        (
            "TEST",
            "small_cap_pre_breakout",
            12,
            58.33,
            4.25,
            -6.75,
        ),
    )

    report = build_latest_signal_report(connection)

    assert "TEST" in report
    assert "Score: 80" in report
    assert "volume spike 1.50x" in report
    assert "20d win=58.33%" in report


def test_build_latest_signal_report_handles_no_signals() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute(
        """
        CREATE TABLE signals (
            ticker TEXT NOT NULL,
            signal_date TEXT NOT NULL,
            close_price REAL NOT NULL,
            status TEXT DEFAULT 'open'
        );
        """
    )

    report = build_latest_signal_report(connection)

    assert "No signals found." in report