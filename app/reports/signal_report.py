from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SignalReport:
    ticker: str
    signal_date: str
    text: str


def build_latest_signal_reports(
    connection: sqlite3.Connection,
    limit: int = 5,
    ticker: str | None = None,
) -> list[SignalReport]:
    if not _table_exists(connection, "signals"):
        return []

    signal_rows = _load_latest_signals(
        connection=connection,
        limit=limit,
        ticker=ticker,
    )

    if not signal_rows:
        return []

    tickers = [str(row["ticker"]) for row in signal_rows]
    backtests = _load_latest_backtests_by_ticker(connection, tickers)

    reports: list[SignalReport] = []

    for row in signal_rows:
        signal = dict(row)
        ticker_value = str(signal["ticker"])
        backtest = backtests.get(ticker_value)

        reports.append(
            SignalReport(
                ticker=ticker_value,
                signal_date=str(signal["signal_date"]),
                text=format_signal_report(signal=signal, backtest=backtest),
            )
        )

    return reports


def format_signal_report(
    signal: dict[str, Any],
    backtest: dict[str, Any] | None = None,
) -> str:
    ticker = signal.get("ticker", "N/A")
    signal_date = signal.get("signal_date", "N/A")
    score = signal.get("score", "N/A")
    status = signal.get("status", "open")

    close_price = _money(signal.get("close_price"))
    entry_price = _money(signal.get("entry_price"))
    stop_loss = _money(signal.get("stop_loss"))
    target_1 = _money(signal.get("target_1"))
    target_2 = _money(signal.get("target_2"))

    volume = _number(signal.get("volume"))
    avg_volume_20 = _number(signal.get("avg_volume_20"))
    volume_spike_ratio = _ratio(signal.get("volume_spike_ratio"))
    rsi_14 = _decimal(signal.get("rsi_14"))
    atr_14 = _money(signal.get("atr_14"))
    atr_compression_ratio = _ratio(signal.get("atr_compression_ratio"))
    high_52w = _money(signal.get("high_52w"))
    distance_from_52w_high_pct = _pct(signal.get("distance_from_52w_high_pct"))

    reasons = _format_reasons(signal.get("reason"))

    lines = [
        f"🚨 Signal: {ticker}",
        "",
        f"Date: {signal_date}",
        f"Status: {status}",
        f"Setup score: {score}/100",
        "",
        "Price levels",
        f"- Close: {close_price}",
        f"- Entry: {entry_price}",
        f"- Stop loss: {stop_loss}",
        f"- Target 1: {target_1}",
        f"- Target 2: {target_2}",
        "",
        "Setup data",
        f"- Volume: {volume}",
        f"- 20D avg volume: {avg_volume_20}",
        f"- Volume spike: {volume_spike_ratio}",
        f"- RSI 14: {rsi_14}",
        f"- ATR 14: {atr_14}",
        f"- ATR compression: {atr_compression_ratio}",
        f"- 52W high: {high_52w}",
        f"- Distance from 52W high: {distance_from_52w_high_pct}",
        "",
        "Why this signal",
        *reasons,
    ]

    if backtest:
        lines.extend(
            [
                "",
                "Historical setup context",
                f"- Sample size: {_number(backtest.get('sample_size'))}",
                f"- 5D win rate: {_pct(backtest.get('win_rate_5d'))}",
                f"- 5D avg return: {_pct(backtest.get('avg_return_5d'))}",
                f"- 10D win rate: {_pct(backtest.get('win_rate_10d'))}",
                f"- 10D avg return: {_pct(backtest.get('avg_return_10d'))}",
                f"- 20D win rate: {_pct(backtest.get('win_rate_20d'))}",
                f"- 20D avg return: {_pct(backtest.get('avg_return_20d'))}",
                f"- Avg 20D max drawdown: {_pct(backtest.get('avg_max_drawdown_20d'))}",
                f"- Best 20D return: {_pct(backtest.get('best_return_20d'))}",
                f"- Worst 20D return: {_pct(backtest.get('worst_return_20d'))}",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "Historical setup context",
                "- No backtest data found yet for this ticker.",
            ]
        )

    lines.extend(
        [
            "",
            "Note: This is data-backed market analysis, not financial advice.",
        ]
    )

    return "\n".join(lines)


def _load_latest_signals(
    connection: sqlite3.Connection,
    limit: int,
    ticker: str | None = None,
) -> list[sqlite3.Row]:
    if ticker:
        return connection.execute(
            """
            SELECT *
            FROM signals
            WHERE ticker = ?
            ORDER BY signal_date DESC, id DESC
            LIMIT ?;
            """,
            (ticker.upper(), limit),
        ).fetchall()

    return connection.execute(
        """
        SELECT *
        FROM signals
        ORDER BY signal_date DESC, id DESC
        LIMIT ?;
        """,
        (limit,),
    ).fetchall()


def _load_latest_backtests_by_ticker(
    connection: sqlite3.Connection,
    tickers: list[str],
) -> dict[str, dict[str, Any]]:
    if not tickers or not _table_exists(connection, "backtest_results"):
        return {}

    placeholders = ", ".join("?" for _ in tickers)

    rows = connection.execute(
        f"""
        SELECT b.*
        FROM backtest_results b
        INNER JOIN (
            SELECT ticker, MAX(id) AS latest_id
            FROM backtest_results
            WHERE ticker IN ({placeholders})
            GROUP BY ticker
        ) latest
            ON b.id = latest.latest_id
        ORDER BY b.ticker ASC;
        """,
        tickers,
    ).fetchall()

    return {str(row["ticker"]): dict(row) for row in rows}


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


def _format_reasons(raw_reason: object) -> list[str]:
    if raw_reason is None:
        return ["- No reason stored."]

    reasons = [part.strip() for part in str(raw_reason).split(";") if part.strip()]

    if not reasons:
        return ["- No reason stored."]

    return [f"- {reason}" for reason in reasons]


def _money(value: object) -> str:
    number = _to_float(value)
    if number is None:
        return "N/A"
    return f"${number:,.2f}"


def _pct(value: object) -> str:
    number = _to_float(value)
    if number is None:
        return "N/A"
    return f"{number:.2f}%"


def _ratio(value: object) -> str:
    number = _to_float(value)
    if number is None:
        return "N/A"
    return f"{number:.2f}x"


def _decimal(value: object) -> str:
    number = _to_float(value)
    if number is None:
        return "N/A"
    return f"{number:.2f}"


def _number(value: object) -> str:
    number = _to_float(value)
    if number is None:
        return "N/A"

    if number.is_integer():
        return f"{int(number):,}"

    return f"{number:,.2f}"


def _to_float(value: object) -> float | None:
    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None