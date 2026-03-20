from .sma_crossover import signal_sma_crossover
from .rsi_reversion import signal_rsi_reversion
from .macd_crossover import signal_macd_crossover
from .bollinger_bounce import signal_bollinger_bounce
from .bollinger_squeeze import signal_bollinger_squeeze
from .combined_macd_rsi import signal_combined_macd_rsi
from .combined_sma_bb import signal_combined_sma_bb
from .combined_triple import signal_combined_triple

STRATEGY_REGISTRY = {
    "SMA_Crossover": signal_sma_crossover,
    "RSI_MeanReversion": signal_rsi_reversion,
    "MACD_Crossover": signal_macd_crossover,
    "Bollinger_Bounce": signal_bollinger_bounce,
    "Bollinger_Squeeze": signal_bollinger_squeeze,
    "Combined_MACD_RSI": signal_combined_macd_rsi,
    "Combined_SMA_BB": signal_combined_sma_bb,
    "Combined_Triple": signal_combined_triple,
}
