import pandas as pd

from app.data.market_data import normalize_ohlcv_frame


def test_normalize_ohlcv_frame_returns_expected_row() -> None:
    frame = pd.DataFrame(
        {
            "Open": [10.0],
            "High": [11.0],
            "Low": [9.5],
            "Close": [10.5],
            "Adj Close": [10.4],
            "Volume": [1000],
        },
        index=pd.to_datetime(["2024-01-02"]),
    )
    frame.index.name = "Date"

    rows = normalize_ohlcv_frame("TEST", frame)

    assert rows == [
        {
            "ticker": "TEST",
            "date": "2024-01-02",
            "open": 10.0,
            "high": 11.0,
            "low": 9.5,
            "close": 10.5,
            "adj_close": 10.4,
            "volume": 1000,
        }
    ]