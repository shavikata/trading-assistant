import pandas as pd


def calculate_avg_volume(volume: pd.Series, period: int = 20) -> pd.Series:
    return volume.astype(float).rolling(period).mean().shift(1)


def calculate_volume_spike_ratio(volume: pd.Series, period: int = 20) -> pd.Series:
    avg_volume = calculate_avg_volume(volume, period=period)
    return volume.astype(float) / avg_volume.mask(avg_volume == 0)