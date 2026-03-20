from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


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
