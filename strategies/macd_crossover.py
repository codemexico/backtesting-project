import pandas as pd
from indicators import macd


def signal_macd_crossover(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    sig: int = 9,
) -> pd.Series:
    macd_line, signal_line, _ = macd(df["Close"], fast, slow, sig)
    signal = pd.Series(0, index=df.index, dtype=int)
    signal[macd_line > signal_line] = 1
    signal[macd_line < signal_line] = -1
    return signal
