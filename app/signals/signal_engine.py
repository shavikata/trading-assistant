from __future__ import annotations

import pandas as pd

from app.config.settings import settings
from app.indicators.atr import calculate_atr
from app.indicators.rsi import calculate_rsi
from app.indicators.volume import calculate_avg_volume, calculate_volume_spike_ratio
from app.signals.signal_models import SignalCandidate


def generate_signal_for_ticker(
    ticker: str,
    price_rows: list[object],
) -> SignalCandidate | None:
    frame = _build_frame(price_rows)

    if len(frame) < 60:
        return None

    frame["rsi_14"] = calculate_rsi(frame["close"], period=14)
    frame["atr_14"] = calculate_atr(
        frame["high"],
        frame["low"],
        frame["close"],
        period=14,
    )
    frame["avg_volume_20"] = calculate_avg_volume(frame["volume"], period=20)
    frame["volume_spike_ratio"] = calculate_volume_spike_ratio(frame["volume"], period=20)

    frame["high_52w"] = frame["high"].rolling(252, min_periods=60).max()
    frame["distance_from_52w_high_pct"] = (frame["close"] / frame["high_52w"] - 1) * 100

    frame["atr_14_prev"] = frame["atr_14"].shift(settings.atr_compression_lookback)
    frame["atr_compression_ratio"] = frame["atr_14"] / frame["atr_14_prev"].mask(
        frame["atr_14_prev"] == 0
    )

    latest = frame.iloc[-1]

    volume_spike_ratio = _safe_float(latest["volume_spike_ratio"])
    atr_compression_ratio = _safe_float(latest["atr_compression_ratio"])
    rsi_14 = _safe_float(latest["rsi_14"])
    distance_from_high = _safe_float(latest["distance_from_52w_high_pct"])
    atr_14 = _safe_float(latest["atr_14"])

    required_values = [
        volume_spike_ratio,
        atr_compression_ratio,
        rsi_14,
        distance_from_high,
        atr_14,
    ]

    if any(value is None for value in required_values):
        return None

    score = 0
    reasons: list[str] = []

    if volume_spike_ratio >= settings.volume_spike_multiplier:
        score += 30
        reasons.append(f"volume spike {volume_spike_ratio:.2f}x")

    if settings.rsi_min <= rsi_14 <= settings.rsi_max:
        score += 25
        reasons.append(f"RSI setup zone {rsi_14:.1f}")

    if atr_compression_ratio <= 1.0:
        score += 20
        reasons.append(f"ATR compression {atr_compression_ratio:.2f}")

    if distance_from_high >= -20:
        score += 15
        reasons.append(f"near 52w high {distance_from_high:.1f}%")

    recent_close_mean = frame["close"].tail(5).mean()
    prior_close_mean = frame["close"].tail(20).head(15).mean()

    if recent_close_mean > prior_close_mean:
        score += 10
        reasons.append("short-term price strength")

    if score < 60:
        return None

    close_price = float(latest["close"])
    entry_price = round(close_price * 1.01, 2)
    stop_loss = round(close_price - float(atr_14) * 1.5, 2)
    target_1 = round(close_price + float(atr_14) * 2, 2)
    target_2 = round(close_price + float(atr_14) * 3, 2)

    return SignalCandidate(
        ticker=ticker.upper(),
        signal_date=pd.Timestamp(latest["date"]).date().isoformat(),
        close_price=round(close_price, 2),
        volume=_safe_int(latest["volume"]),
        avg_volume_20=_safe_float(latest["avg_volume_20"], digits=2),
        volume_spike_ratio=volume_spike_ratio,
        atr_14=atr_14,
        atr_14_prev=_safe_float(latest["atr_14_prev"]),
        atr_compression_ratio=atr_compression_ratio,
        rsi_14=rsi_14,
        high_52w=_safe_float(latest["high_52w"], digits=2),
        distance_from_52w_high_pct=distance_from_high,
        entry_price=entry_price,
        stop_loss=stop_loss,
        target_1=target_1,
        target_2=target_2,
        score=score,
        reason="; ".join(reasons),
    )


def _build_frame(price_rows: list[object]) -> pd.DataFrame:
    data = pd.DataFrame([dict(row) for row in price_rows])

    if data.empty:
        return data

    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values("date").reset_index(drop=True)

    numeric_columns = ["open", "high", "low", "close", "adj_close", "volume"]

    for column in numeric_columns:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["high", "low", "close", "volume"])

    return data


def _safe_float(value: object, digits: int = 4) -> float | None:
    if pd.isna(value):
        return None

    return round(float(value), digits)


def _safe_int(value: object) -> int | None:
    if pd.isna(value):
        return None

    return int(value)