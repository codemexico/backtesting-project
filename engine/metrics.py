import numpy as np
from typing import Dict, List


def compute_metrics(
    equity_curve: np.ndarray,
    trades: List[Dict],
    risk_free_rate: float = 0.04,
) -> Dict:
    if len(equity_curve) < 2:
        return {}

    returns = np.diff(equity_curve) / equity_curve[:-1]
    total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100
    n_days = len(returns)
    annual_factor = 252

    ann_return = (1 + total_return / 100) ** (annual_factor / n_days) - 1
    ann_vol = np.std(returns) * np.sqrt(annual_factor)
    sharpe = (ann_return - risk_free_rate) / ann_vol if ann_vol > 0 else 0

    downside = returns[returns < 0]
    downside_vol = np.std(downside) * np.sqrt(annual_factor) if len(downside) > 0 else 0
    sortino = (ann_return - risk_free_rate) / downside_vol if downside_vol > 0 else 0

    peak = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - peak) / peak
    max_dd = np.min(drawdown) * 100

    wins = [t for t in trades if t.pnl and t.pnl > 0]
    losses = [t for t in trades if t.pnl and t.pnl <= 0]
    win_rate = len(wins) / len(trades) * 100 if trades else 0

    avg_win = np.mean([t.pnl_pct for t in wins]) if wins else 0
    avg_loss = np.mean([t.pnl_pct for t in losses]) if losses else 0

    gross_wins = sum(t.pnl for t in wins) if wins else 0
    gross_losses = abs(sum(t.pnl for t in losses)) if losses else 0
    profit_factor = gross_wins / gross_losses if gross_losses > 0 else float("inf")

    return {
        "total_return_pct": round(total_return, 2),
        "annualized_return_pct": round(ann_return * 100, 2),
        "annualized_volatility_pct": round(ann_vol * 100, 2),
        "sharpe_ratio": round(sharpe, 4),
        "sortino_ratio": round(sortino, 4),
        "max_drawdown_pct": round(max_dd, 2),
        "total_trades": len(trades),
        "winning_trades": len(wins),
        "losing_trades": len(losses),
        "win_rate_pct": round(win_rate, 2),
        "avg_win_pct": round(avg_win, 2),
        "avg_loss_pct": round(avg_loss, 2),
        "profit_factor": round(profit_factor, 4) if profit_factor != float("inf") else "inf",
        "final_equity": round(equity_curve[-1], 2),
    }
