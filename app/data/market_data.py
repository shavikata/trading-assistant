from typing import Any

import pandas as pd
import yfinance as yf


def _to_float(value: Any) -> float | None:
    if pd.isna(value):
        return None

    return float(value)


def _to_int(value: Any) -> int | None:
    if pd.isna(value):
        return None

    return int(value)


def normalize_ohlcv_frame(ticker: str, frame: pd.DataFrame) -> list[dict[str, object]]:
    if frame.empty:
        return []

    data = frame.copy()

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    date_column = "Date" if "Date" in data.columns else "Datetime"

    rows: list[dict[str, object]] = []

    for _, row in data.iterrows():
        close_price = row.get("Close")

        if pd.isna(close_price):
            continue

        date_value = row[date_column]

        rows.append(
            {
                "ticker": ticker.upper(),
                "date": date_value.date().isoformat(),
                "open": _to_float(row.get("Open")),
                "high": _to_float(row.get("High")),
                "low": _to_float(row.get("Low")),
                "close": _to_float(row.get("Close")),
                "adj_close": _to_float(row.get("Adj Close")),
                "volume": _to_int(row.get("Volume")),
            }
        )

    return rows


def download_ohlcv(
    ticker: str,
    period: str = "1y",
    interval: str = "1d",
) -> list[dict[str, object]]:
    frame = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False,
        threads=False,
    )

    return normalize_ohlcv_frame(ticker=ticker, frame=frame)