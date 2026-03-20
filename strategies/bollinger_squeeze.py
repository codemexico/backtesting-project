import pandas as pd
from indicators import bollinger_bands


def signal_bollinger_squeeze(
    df: pd.DataFrame,
    window: int = 20,
    num_std: float = 2.0,
    squeeze_lookback: int = 120,
) -> pd.Series:
    upper, _, lower, _, bandwidth = bollinger_bands(df["Close"], window, num_std)
    width_threshold = bandwidth.rolling(squeeze_lookback).mean()
    squeeze = bandwidth < width_threshold

    signal = pd.Series(0, index=df.index, dtype=int)
    breakout_up = squeeze.shift(1).fillna(False) & (df["Close"] > upper)
    breakout_down = squeeze.shift(1).fillna(False) & (df["Close"] < lower)
    signal[breakout_up] = 1
    signal[breakout_down] = -1
    return signal
