from dataclasses import dataclass


@dataclass(frozen=True)
class SignalCandidate:
    ticker: str
    signal_date: str
    close_price: float
    volume: int | None
    avg_volume_20: float | None
    volume_spike_ratio: float | None
    atr_14: float | None
    atr_14_prev: float | None
    atr_compression_ratio: float | None
    rsi_14: float | None
    high_52w: float | None
    distance_from_52w_high_pct: float | None
    entry_price: float
    stop_loss: float
    target_1: float
    target_2: float
    score: int
    reason: str
    status: str = "open"

    def to_signal_table_row(self) -> dict[str, object]:
        return {
            "ticker": self.ticker,
            "signal_date": self.signal_date,
            "close_price": self.close_price,
            "volume": self.volume,
            "avg_volume_20": self.avg_volume_20,
            "volume_spike_ratio": self.volume_spike_ratio,
            "atr_14": self.atr_14,
            "atr_14_prev": self.atr_14_prev,
            "atr_compression_ratio": self.atr_compression_ratio,
            "rsi_14": self.rsi_14,
            "high_52w": self.high_52w,
            "distance_from_52w_high_pct": self.distance_from_52w_high_pct,
            "entry_price": self.entry_price,
            "stop_loss": self.stop_loss,
            "target_1": self.target_1,
            "target_2": self.target_2,
            "status": self.status,
        }