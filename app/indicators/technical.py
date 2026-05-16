from __future__ import annotations

import pandas as pd


def add_technical_indicators(price_data: pd.DataFrame) -> pd.DataFrame:
    if price_data.empty:
        return price_data.copy()

    data = price_data.copy()
    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values(["ticker", "date"]).reset_index(drop=True)

    grouped = data.groupby("ticker", group_keys=False)

    data["avg_volume_20"] = grouped["volume"].transform(
        lambda series: series.rolling(window=20, min_periods=20).mean()
    )

    data["volume_spike_ratio"] = data["volume"] / data["avg_volume_20"]

    previous_close = grouped["close"].shift(1)

    high_low = data["high"] - data["low"]
    high_previous_close = (data["high"] - previous_close).abs()
    low_previous_close = (data["low"] - previous_close).abs()

    true_range = pd.concat(
        [high_low, high_previous_close, low_previous_close],
        axis=1,
    ).max(axis=1)

    data["atr_14"] = true_range.groupby(data["ticker"]).transform(
        lambda series: series.rolling(window=14, min_periods=14).mean()
    )

    data["atr_14_prev"] = grouped["atr_14"].shift(1)

    data["atr_compression_ratio"] = data["atr_14"] / data["atr_14_prev"]

    data["rsi_14"] = grouped["close"].transform(_calculate_rsi)

    data["high_52w"] = grouped["high"].transform(
        lambda series: series.rolling(window=252, min_periods=20).max()
    )

    data["distance_from_52w_high_pct"] = (
        (data["close"] - data["high_52w"]) / data["high_52w"]
    ) * 100

    return data


def _calculate_rsi(close_prices: pd.Series, period: int = 14) -> pd.Series:
    delta = close_prices.diff()

    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.rolling(window=period, min_periods=period).mean()
    avg_loss = losses.rolling(window=period, min_periods=period).mean()

    relative_strength = avg_gain / avg_loss

    rsi = 100 - (100 / (1 + relative_strength))

    return rsi