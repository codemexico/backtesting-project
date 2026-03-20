import yfinance as yf
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from datetime import datetime
import os
import json


@dataclass
class Trade:
    ticker: str
    entry_date: datetime
    entry_price: float
    direction: str
    size: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_pct: Optional[float] = None


@dataclass
class PortfolioState:
    cash: float
    positions: Dict[str, float] = field(default_factory=dict)
    equity_curve: List[float] = field(default_factory=list)
    trades: List[Trade] = field(default_factory=list)


class DataLoader:
    def __init__(self, tickers: List[str], start: str, end: str):
        self.tickers = tickers
        self.start = start
        self.end = end
        self.data: Dict[str, pd.DataFrame] = {}

    def fetch(self) -> Dict[str, pd.DataFrame]:
        for ticker in self.tickers:
            df = yf.download(ticker, start=self.start, end=self.end, progress=False)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
            df.dropna(inplace=True)
            self.data[ticker] = df
        return self.data

    def get(self, ticker: str) -> pd.DataFrame:
        return self.data.get(ticker, pd.DataFrame())


class Indicators:
    @staticmethod
    def sma(series: pd.Series, window: int) -> pd.Series:
        return series.rolling(window=window).mean()

    @staticmethod
    def ema(series: pd.Series, span: int) -> pd.Series:
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def rsi(series: pd.Series, period: int = 14) -> pd.Series:
        delta = series.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
        avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        ema_fast = series.ewm(span=fast, adjust=False).mean()
        ema_slow = series.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram

    @staticmethod
    def bollinger_bands(series: pd.Series, window: int = 20, num_std: float = 2.0):
        sma = series.rolling(window=window).mean()
        std = series.rolling(window=window).std()
        upper = sma + num_std * std
        lower = sma - num_std * std
        return upper, sma, lower


class SignalGenerator:
    def __init__(self):
        self.strategies: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        self.strategies[name] = func

    def generate(self, name: str, df: pd.DataFrame, **kwargs) -> pd.Series:
        if name not in self.strategies:
            raise ValueError(f"Strategy '{name}' not registered.")
        return self.strategies[name](df, **kwargs)


def strategy_sma_crossover(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> pd.Series:
    sma_fast = Indicators.sma(df["Close"], fast)
    sma_slow = Indicators.sma(df["Close"], slow)
    signal = pd.Series(0, index=df.index)
    signal[sma_fast > sma_slow] = 1
    signal[sma_fast < sma_slow] = -1
    return signal


def strategy_rsi_mean_reversion(df: pd.DataFrame, period: int = 14, oversold: float = 30, overbought: float = 70) -> pd.Series:
    rsi = Indicators.rsi(df["Close"], period)
    signal = pd.Series(0, index=df.index)
    signal[rsi < oversold] = 1
    signal[rsi > overbought] = -1
    return signal


def strategy_macd_crossover(df: pd.DataFrame, fast: int = 12, slow: int = 26, sig: int = 9) -> pd.Series:
    macd_line, signal_line, _ = Indicators.macd(df["Close"], fast, slow, sig)
    signal = pd.Series(0, index=df.index)
    signal[macd_line > signal_line] = 1
    signal[macd_line < signal_line] = -1
    return signal


class BacktestEngine:
    def __init__(self, initial_capital: float = 100_000.0, commission: float = 0.001):
        self.initial_capital = initial_capital
        self.commission = commission

    def run(self, df: pd.DataFrame, signals: pd.Series, ticker: str) -> PortfolioState:
        portfolio = PortfolioState(cash=self.initial_capital)
        position = 0
        entry_price = 0.0
        entry_date = None

        for i in range(1, len(df)):
            date = df.index[i]
            price = df["Close"].iloc[i]
            sig = signals.iloc[i]
            prev_sig = signals.iloc[i - 1]

            if sig == 1 and prev_sig != 1 and position == 0:
                size = (portfolio.cash * 0.95) / price
                cost = size * price * (1 + self.commission)
                if cost <= portfolio.cash:
                    position = size
                    entry_price = price
                    entry_date = date
                    portfolio.cash -= cost

            elif sig == -1 and position > 0:
                revenue = position * price * (1 - self.commission)
                portfolio.cash += revenue
                trade = Trade(
                    ticker=ticker,
                    entry_date=entry_date,
                    entry_price=entry_price,
                    direction="LONG",
                    size=position,
                    exit_date=date,
                    exit_price=price,
                    pnl=revenue - (position * entry_price),
                    pnl_pct=(price - entry_price) / entry_price * 100,
                )
                portfolio.trades.append(trade)
                position = 0

            equity = portfolio.cash + position * price
            portfolio.equity_curve.append(equity)

        return portfolio


class Metrics:
    @staticmethod
    def compute(portfolio: PortfolioState, risk_free_rate: float = 0.04) -> Dict:
        equity = np.array(portfolio.equity_curve)
        if len(equity) < 2:
            return {}

        returns = np.diff(equity) / equity[:-1]
        total_return = (equity[-1] - equity[0]) / equity[0] * 100
        n_days = len(returns)
        annual_factor = 252

        ann_return = (1 + total_return / 100) ** (annual_factor / n_days) - 1
        ann_vol = np.std(returns) * np.sqrt(annual_factor)
        sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0

        downside = returns[returns < 0]
        downside_vol = np.std(downside) * np.sqrt(annual_factor) if len(downside) > 0 else 0
        sortino = (ann_return - risk_free_rate) / downside_vol if downside_vol > 0 else 0

        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak
        max_dd = np.min(drawdown) * 100

        wins = [t for t in portfolio.trades if t.pnl and t.pnl > 0]
        losses = [t for t in portfolio.trades if t.pnl and t.pnl <= 0]
        win_rate = len(wins) / len(portfolio.trades) * 100 if portfolio.trades else 0

        return {
            "total_return_pct": round(total_return, 2),
            "annualized_return_pct": round(ann_return * 100, 2),
            "annualized_volatility_pct": round(ann_vol * 100, 2),
            "sharpe_ratio": round(sharpe, 4),
            "sortino_ratio": round(sortino, 4),
            "max_drawdown_pct": round(max_dd, 2),
            "total_trades": len(portfolio.trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate_pct": round(win_rate, 2),
            "final_equity": round(equity[-1], 2),
        }


class ReportGenerator:
    @staticmethod
    def summary(metrics: Dict, ticker: str, strategy: str) -> str:
        lines = [
            f"{'='*60}",
            f"  Backtest Report: {ticker} | Strategy: {strategy}",
            f"{'='*60}",
        ]
        for key, val in metrics.items():
            label = key.replace("_", " ").title()
            lines.append(f"  {label:<35} {val}")
        lines.append(f"{'='*60}")
        return "\n".join(lines)

    @staticmethod
    def to_json(metrics: Dict, path: str):
        with open(path, "w") as f:
            json.dump(metrics, f, indent=2)

    @staticmethod
    def trades_to_csv(trades: List[Trade], path: str):
        rows = []
        for t in trades:
            rows.append({
                "ticker": t.ticker,
                "entry_date": str(t.entry_date),
                "entry_price": t.entry_price,
                "exit_date": str(t.exit_date),
                "exit_price": t.exit_price,
                "direction": t.direction,
                "size": t.size,
                "pnl": t.pnl,
                "pnl_pct": t.pnl_pct,
            })
        pd.DataFrame(rows).to_csv(path, index=False)


MAGNIFICENT_7 = ["NVDA", "AAPL", "MSFT", "META", "GOOGL", "TSLA", "AMZN"]
INDUSTRIALS = ["GE", "HD"]
ALL_TICKERS = MAGNIFICENT_7 + INDUSTRIALS

START_DATE = "2022-01-01"
END_DATE = datetime.now().strftime("%Y-%m-%d")

OUTPUT_DIR = "results"


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    loader = DataLoader(ALL_TICKERS, START_DATE, END_DATE)
    data = loader.fetch()

    signal_gen = SignalGenerator()
    signal_gen.register("SMA_Crossover", strategy_sma_crossover)
    signal_gen.register("RSI_MeanReversion", strategy_rsi_mean_reversion)
    signal_gen.register("MACD_Crossover", strategy_macd_crossover)

    engine = BacktestEngine(initial_capital=100_000.0, commission=0.001)

    all_results = {}

    for ticker in ALL_TICKERS:
        df = loader.get(ticker)
        if df.empty:
            continue

        all_results[ticker] = {}

        for strategy_name in signal_gen.strategies:
            signals = signal_gen.generate(strategy_name, df)
            portfolio = engine.run(df, signals, ticker)
            metrics = Metrics.compute(portfolio)

            all_results[ticker][strategy_name] = metrics

            print(ReportGenerator.summary(metrics, ticker, strategy_name))
            print()

            safe_name = f"{ticker}_{strategy_name}".replace(" ", "_")
            ReportGenerator.to_json(metrics, os.path.join(OUTPUT_DIR, f"{safe_name}_metrics.json"))
            ReportGenerator.trades_to_csv(portfolio.trades, os.path.join(OUTPUT_DIR, f"{safe_name}_trades.csv"))

    summary_rows = []
    for ticker, strats in all_results.items():
        for strat, m in strats.items():
            row = {"ticker": ticker, "strategy": strat}
            row.update(m)
            summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(OUTPUT_DIR, "summary_all.csv"), index=False)
    print(f"\nResultados exportados en '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()
