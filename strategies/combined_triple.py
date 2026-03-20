import pandas as pd
from indicators import sma, macd, rsi


def signal_combined_triple(
    df: pd.DataFrame,
    sma_fast: int = 20,
    sma_slow: int = 50,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_sig: int = 9,
    rsi_period: int = 14,
    rsi_buy_cap: float = 70,
    rsi_sell_floor: float = 30,
) -> pd.Series:
    sma_f = sma(df["Close"], sma_fast)
    sma_s = sma(df["Close"], sma_slow)
    macd_line, signal_line, _ = macd(df["Close"], macd_fast, macd_slow, macd_sig)
    rsi_val = rsi(df["Close"], rsi_period)

    signal = pd.Series(0, index=df.index, dtype=int)
    signal[(sma_f > sma_s) & (macd_line > signal_line) & (rsi_val < rsi_buy_cap)] = 1
    signal[(sma_f < sma_s) & (macd_line < signal_line) & (rsi_val > rsi_sell_floor)] = -1
    return signal
