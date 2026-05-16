from __future__ import annotations

import sqlite3
from typing import Any


def build_watchlist_summary_report(connection: sqlite3.Connection) -> str:
    if not _table_exists(connection, "backtest_results"):
        return _empty_report("Backtest table does not exist yet.")

    rows = connection.execute(
        """
        SELECT b.*
        FROM backtest_results b
        INNER JOIN (
            SELECT ticker, MAX(id) AS latest_id
            FROM backtest_results
            GROUP BY ticker
        ) latest
            ON b.id = latest.latest_id
        ORDER BY b.avg_return_20d DESC;
        """
    ).fetchall()

    if not rows:
        return _empty_report("No backtest results found yet.")

    lines = [
        "📊 Daily Watchlist Summary",
        "",
        "No active signal found today.",
        "",
        "Backtest context",
    ]

    for row in rows:
        data = dict(row)
        lines.append(
            "- "
            f"{data.get('ticker', 'N/A')}: "
            f"samples={_number(data.get('sample_size'))}, "
            f"20D win={_pct(data.get('win_rate_20d'))}, "
            f"20D avg={_pct(data.get('avg_return_20d'))}"
        )

    lines.extend(
        [
            "",
            "Interpretation:",
            "- No ticker reached the current signal threshold today.",
            "- Watchlist still has historical setup data for monitoring.",
            "",
            "Note: This is data-backed market analysis, not financial advice.",
        ]
    )

    return "\n".join(lines)


def _empty_report(reason: str) -> str:
    return "\n".join(
        [
            "📊 Daily Watchlist Summary",
            "",
            "No active signal found today.",
            "",
            reason,
            "",
            "Run these first:",
            "python -m scripts.run_daily_signals",
            "python -m scripts.run_backtest",
        ]
    )


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
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


def _pct(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "N/A"
    return f"{number:.2f}%"


def _number(value: Any) -> str:
    number = _to_float(value)
    if number is None:
        return "N/A"

    if number.is_integer():
        return f"{int(number):,}"

    return f"{number:,.2f}"


def _to_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None