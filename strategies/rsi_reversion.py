import pandas as pd
from indicators import rsi


def signal_rsi_reversion(
    df: pd.DataFrame,
    period: int = 14,
    oversold: float = 30,
    overbought: float = 70,
) -> pd.Series:
    rsi_vals = rsi(df["Close"], period)
    signal = pd.Series(0, index=df.index, dtype=int)
    signal[rsi_vals < oversold] = 1
    signal[rsi_vals > overbought] = -1
    return signal
