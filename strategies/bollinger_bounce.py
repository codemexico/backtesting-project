import pandas as pd
from indicators import bollinger_bands


def signal_bollinger_bounce(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.Series:
    _, _, _, pct_b, _ = bollinger_bands(df["Close"], window, num_std)
    signal = pd.Series(0, index=df.index, dtype=int)
    signal[pct_b < 0.0] = 1
    signal[pct_b > 1.0] = -1
    return signal
