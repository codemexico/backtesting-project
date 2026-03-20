import pandas as pd
from indicators import sma, bollinger_bands


def signal_combined_sma_bb(
    df: pd.DataFrame,
    sma_fast: int = 20,
    sma_slow: int = 50,
    bb_window: int = 20,
    bb_std: float = 2.0,
    pctb_buy: float = 0.3,
    pctb_sell: float = 0.7,
) -> pd.Series:
    sma_f = sma(df["Close"], sma_fast)
    sma_s = sma(df["Close"], sma_slow)
    _, _, _, pct_b, _ = bollinger_bands(df["Close"], bb_window, bb_std)

    sma_bull = sma_f > sma_s
    sma_bear = sma_f < sma_s

    signal = pd.Series(0, index=df.index, dtype=int)
    signal[sma_bull & (pct_b < pctb_buy)] = 1
    signal[sma_bear & (pct_b > pctb_sell)] = -1
    return signal
