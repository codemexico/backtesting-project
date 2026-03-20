import pandas as pd
from indicators import macd, rsi


def signal_combined_macd_rsi(
    df: pd.DataFrame,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_sig: int = 9,
    rsi_period: int = 14,
    rsi_low: float = 40,
    rsi_high: float = 60,
) -> pd.Series:
    macd_line, signal_line, _ = macd(df["Close"], macd_fast, macd_slow, macd_sig)
    rsi_val = rsi(df["Close"], rsi_period)

    macd_bull = macd_line > signal_line
    macd_bear = macd_line < signal_line

    signal = pd.Series(0, index=df.index, dtype=int)
    signal[macd_bull & (rsi_val < rsi_high)] = 1
    signal[macd_bear & (rsi_val > rsi_low)] = -1
    return signal
