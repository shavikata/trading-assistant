from __future__ import annotations

import sqlite3


def build_latest_telegram_signal_message(
    connection: sqlite3.Connection,
    limit: int = 5,
) -> str:
    if not _table_exists(connection, "signals"):
        return "📊 AI Stock Signals\n\nNo signals table found."

    signal_columns = _get_table_columns(connection, "signals")

    select_columns = [
        _select_expression(signal_columns, "ticker", "''"),
        _select_expression(signal_columns, "signal_date", "''"),
        _select_expression(signal_columns, "close_price", "NULL"),
        _select_expression(signal_columns, "volume_spike_ratio", "NULL"),
        _select_expression(signal_columns, "atr_compression_ratio", "NULL"),
        _select_expression(signal_columns, "rsi_14", "NULL"),
        _select_expression(signal_columns, "entry_price", "NULL"),
        _select_expression(signal_columns, "stop_loss", "NULL"),
        _select_expression(signal_columns, "target_1", "NULL"),
        _select_expression(signal_columns, "target_2", "NULL"),
        _select_expression(signal_columns, "score", "0"),
        _select_expression(signal_columns, "reason", "''"),
        _select_expression(signal_columns, "status", "'unknown'"),
    ]

    rows = connection.execute(
        f"""
        SELECT
            {", ".join(select_columns)}
        FROM signals
        ORDER BY signal_date DESC, score DESC, ticker ASC
        LIMIT ?;
        """,
        (limit,),
    ).fetchall()

    if not rows:
        return "📊 AI Stock Signals\n\nNo active signals found."

    lines = [
        "📊 AI Stock Signals",
        "Educational scan. Not financial advice.",
        "",
    ]

    for index, row in enumerate(rows, start=1):
        lines.extend(
            [
                f"{index}) {row['ticker']} | {row['signal_date']} | Score {row['score']}",
                (
                    f"Close: {_format_money(row['close_price'])} | "
                    f"Entry: {_format_money(row['entry_price'])} | "
                    f"Stop: {_format_money(row['stop_loss'])}"
                ),
                (
                    f"T1: {_format_money(row['target_1'])} | "
                    f"T2: {_format_money(row['target_2'])} | "
                    f"Status: {row['status']}"
                ),
                (
                    f"Vol: {_format_ratio(row['volume_spike_ratio'])} | "
                    f"ATR comp: {_format_ratio(row['atr_compression_ratio'])} | "
                    f"RSI: {_format_number(row['rsi_14'])}"
                ),
                f"Why: {row['reason'] or 'No reason stored.'}",
                "",
            ]
        )

    return "\n".join(lines).strip() + "\n"


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

    return f"{float(value):.1f}"


def _format_ratio(value: object) -> str:
    if value is None:
        return "n/a"

    return f"{float(value):.2f}x"