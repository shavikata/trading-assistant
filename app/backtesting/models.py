from dataclasses import dataclass


@dataclass(frozen=True)
class BacktestSummary:
    ticker: str
    setup_name: str
    sample_size: int
    win_rate_5d: float | None
    avg_return_5d: float | None
    win_rate_10d: float | None
    avg_return_10d: float | None
    win_rate_20d: float | None
    avg_return_20d: float | None
    avg_max_drawdown_20d: float | None
    best_return_20d: float | None
    worst_return_20d: float | None

    def to_db_row(self) -> dict[str, object]:
        return self.__dict__.copy()