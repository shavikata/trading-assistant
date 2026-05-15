from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv


load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_env: str = os.getenv("APP_ENV", "development")
    database_path: Path = BASE_DIR / os.getenv("DATABASE_PATH", "data/market_data.db")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    min_market_cap: int = int(os.getenv("MIN_MARKET_CAP", "300000000"))
    max_market_cap: int = int(os.getenv("MAX_MARKET_CAP", "2000000000"))

    volume_spike_multiplier: float = float(os.getenv("VOLUME_SPIKE_MULTIPLIER", "2.0"))
    rsi_min: float = float(os.getenv("RSI_MIN", "30"))
    rsi_max: float = float(os.getenv("RSI_MAX", "50"))
    atr_compression_lookback: int = int(os.getenv("ATR_COMPRESSION_LOOKBACK", "5"))
    min_avg_dollar_volume: float = float(os.getenv("MIN_AVG_DOLLAR_VOLUME", "1000000"))


settings = Settings()