import pandas as pd

from app.indicators.technical import add_technical_indicators


def test_add_technical_indicators_adds_expected_columns() -> None:
    frame = pd.DataFrame(
        {
            "ticker": ["TEST"] * 60,
            "date": pd.date_range("2024-01-01", periods=60).astype(str),
            "open": [10 + index for index in range(60)],
            "high": [11 + index for index in range(60)],
            "low": [9 + index for index in range(60)],
            "close": [10 + index for index in range(60)],
            "adj_close": [10 + index for index in range(60)],
            "volume": [1000 + (index * 10) for index in range(60)],
        }
    )

    result = add_technical_indicators(frame)

    expected_columns = {
        "avg_volume_20",
        "volume_spike_ratio",
        "atr_14",
        "atr_14_prev",
        "atr_compression_ratio",
        "rsi_14",
        "high_52w",
        "distance_from_52w_high_pct",
    }

    assert expected_columns.issubset(result.columns)
    assert result["avg_volume_20"].notna().sum() > 0
    assert result["atr_14"].notna().sum() > 0
    assert result["rsi_14"].notna().sum() > 0


def test_add_technical_indicators_returns_empty_frame_for_empty_input() -> None:
    frame = pd.DataFrame()

    result = add_technical_indicators(frame)

    assert result.empty