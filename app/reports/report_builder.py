from __future__ import annotations

import sqlite3
from pathlib import Path


def build_latest_signal_report(
    connection: sqlite3.Connection,
    limit: int = 10,
) -> str:
    if not _table_exists(connection, "signals"):
        return "AI Stock Signal Report\n\nNo signals table found."

    signal_columns = _get_table_columns(connection, "signals")

    select_columns = [
        _select_expression(signal_columns, "ticker", "''"),
        _select_expression(signal_columns, "signal_date", "''"),
        _select_expression(signal_columns, "close_price", "NULL"),
        _select_expression(signal_columns, "volume", "NULL"),
        _select_expression(signal_columns, "volume_spike_ratio", "NULL"),
        _select_expression(signal_columns, "atr_compression_ratio", "NULL"),
        _select_expression(signal_columns, "rsi_14", "NULL"),
        _select_expression(signal_columns, "distance_from_52w_high_pct", "NULL"),
        _select_expression(signal_columns, "entry_price", "NULL"),
        _select_expression(signal_columns, "stop_loss", "NULL"),
        _select_expression(signal_columns, "target_1", "NULL"),
        _select_expression(signal_columns, "target_2", "NULL"),
        _select_expression(signal_columns, "score", "0"),
        _select_expression(signal_columns, "reason", "''"),
        _select_expression(signal_columns, "status", "'unknown'"),
    ]

    order_score = "score"

    rows = connection.execute(
        f"""
        SELECT
            {", ".join(select_columns)}
        FROM signals
        ORDER BY signal_date DESC, {order_score} DESC, ticker ASC
        LIMIT ?;
        """,
        (limit,),
    ).fetchall()

    if not rows:
        return "AI Stock Signal Report\n\nNo signals found."

    lines = [
        "AI Stock Signal Report",
        "",
        f"Signals shown: {len(rows)}",
        "",
    ]

    for row in rows:
        backtest = _get_latest_backtest_for_ticker(connection, str(row["ticker"]))

        lines.extend(
            [
                f"## {row['ticker']} — {row['signal_date']}",
                (
                    f"Close: {_format_money(row['close_price'])} | "
                    f"Score: {row['score']} | "
                    f"Status: {row['status']}"
                ),
                (
                    f"Entry: {_format_money(row['entry_price'])} | "
                    f"Stop: {_format_money(row['stop_loss'])} | "
                    f"Target 1: {_format_money(row['target_1'])} | "
                    f"Target 2: {_format_money(row['target_2'])}"
                ),
                (
                    f"Volume spike: {_format_ratio(row['volume_spike_ratio'])} | "
                    f"ATR compression: {_format_ratio(row['atr_compression_ratio'])} | "
                    f"RSI: {_format_number(row['rsi_14'])} | "
                    f"Distance from 52w high: "
                    f"{_format_percent(row['distance_from_52w_high_pct'])}"
                ),
                f"Reason: {row['reason'] or 'No reason stored.'}",
            ]
        )

        if backtest is not None:
            lines.append(
                "Backtest: "
                f"samples={backtest['sample_size']} | "
                f"20d win={_format_percent(backtest['win_rate_20d'])} | "
                f"20d avg={_format_percent(backtest['avg_return_20d'])} | "
                f"avg 20d drawdown="
                f"{_format_percent(backtest['avg_max_drawdown_20d'])}"
            )
        else:
            lines.append("Backtest: no historical result stored yet.")

        lines.append("")

    return "\n".join(lines).strip() + "\n"


def save_report_to_file(report: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    return output_path


def _get_latest_backtest_for_ticker(
    connection: sqlite3.Connection,
    ticker: str,
) -> sqlite3.Row | None:
    if not _table_exists(connection, "backtest_results"):
        return None

    return connection.execute(
        """
        SELECT
            ticker,
            setup_name,
            sample_size,
            win_rate_20d,
            avg_return_20d,
            avg_max_drawdown_20d
        FROM backtest_results
        WHERE ticker = ?
        ORDER BY run_at DESC, id DESC
        LIMIT 1;
        """,
        (ticker.upper(),),
    ).fetchone()


def _table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    row = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table' AND name = ?;
        """,
        (table_name,),
    ).fetchone()

    return row is not None


def _get_table_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name});").fetchall()
    return {str(row[1]) for row in rows}


def _select_expression(
    existing_columns: set[str],
    column_name: str,
    fallback_expression: str,
) -> str:
    if column_name in existing_columns:
        return f"{column_name} AS {column_name}"

    return f"{fallback_expression} AS {column_name}"


def _format_money(value: object) -> str:
    if value is None:
        return "n/a"

    return f"${float(value):.2f}"


def _format_number(value: object) -> str:
    if value is None:
        return "n/a"

    return f"{float(value):.2f}"


def _format_ratio(value: object) -> str:
    if value is None:
        return "n/a"

    return f"{float(value):.2f}x"


def _format_percent(value: object) -> str:
    if value is None:
        return "n/a"

    return f"{float(value):.2f}%"