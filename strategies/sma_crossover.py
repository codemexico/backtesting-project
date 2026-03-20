import pandas as pd
from indicators import sma


def signal_sma_crossover(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.Series:
    sma_fast = sma(df["Close"], fast)
    sma_slow = sma(df["Close"], slow)
    signal = pd.Series(0, index=df.index, dtype=int)
    signal[sma_fast > sma_slow] = 1
    signal[sma_fast < sma_slow] = -1
    return signal
