import pandas as pd
import numpy as np
from .portfolio import PortfolioState, Trade


class BacktestEngine:
    def __init__(
        self,
        initial_capital: float = 100_000.0,
        commission: float = 0.001,
        position_size_pct: float = 0.95,
    ):
        self.initial_capital = initial_capital
        self.commission = commission
        self.position_size_pct = position_size_pct

    def run(self, df: pd.DataFrame, signals: pd.Series, ticker: str) -> PortfolioState:
        portfolio = PortfolioState(cash=self.initial_capital)
        position = 0.0
        entry_price = 0.0
        entry_date = None

        for i in range(1, len(df)):
            date = df.index[i]
            price = df["Close"].iloc[i]
            sig = signals.iloc[i]
            prev_sig = signals.iloc[i - 1]

            if sig == 1 and prev_sig != 1 and position == 0:
                size = (portfolio.cash * self.position_size_pct) / price
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
