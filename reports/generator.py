import json
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, List
from engine.portfolio import Trade


class ReportGenerator:
    @staticmethod
    def summary(metrics: Dict, ticker: str, strategy: str) -> str:
        lines = [
            f"{'=' * 60}",
            f"  Backtest Report: {ticker} | Strategy: {strategy}",
            f"{'=' * 60}",
        ]
        for key, val in metrics.items():
            label = key.replace("_", " ").title()
            lines.append(f"  {label:<35} {val}")
        lines.append(f"{'=' * 60}")
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

    @staticmethod
    def plot_equity_comparison(
        equity_curves: Dict[str, np.ndarray],
        ticker: str,
        save_path: str,
        initial_capital: float = 100_000.0,
    ):
        fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1.5]})

        ax = axes[0]
        colors = plt.cm.Set2(np.linspace(0, 1, len(equity_curves)))
        for (name, curve), color in zip(equity_curves.items(), colors):
            ax.plot(range(len(curve)), curve, label=name, linewidth=0.9, color=color)
        ax.axhline(initial_capital, color="gray", linewidth=0.5, linestyle="--", alpha=0.7)
        ax.set_title(f"{ticker} — Equity Curves by Strategy", fontweight="bold")
        ax.set_ylabel("Equity (USD)")
        ax.legend(loc="upper left", ncol=2, fontsize=7, framealpha=0.9)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.grid(True, alpha=0.3)

        ax2 = axes[1]
        strategies = list(equity_curves.keys())
        final_returns = [(equity_curves[s][-1] - initial_capital) / initial_capital * 100 for s in strategies]
        bar_colors = ["#4CAF50" if r > 0 else "#F44336" for r in final_returns]
        bars = ax2.barh(range(len(strategies)), final_returns, color=bar_colors, alpha=0.8)
        ax2.set_yticks(range(len(strategies)))
        ax2.set_yticklabels(strategies, fontsize=7)
        ax2.set_xlabel("Total Return (%)")
        ax2.set_title("Total Return Comparison", fontweight="bold")
        ax2.axvline(0, color="gray", linewidth=0.5)
        ax2.grid(True, alpha=0.3)
        for bar, val in zip(bars, final_returns):
            ax2.text(
                bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=7,
            )

        plt.tight_layout()
        plt.savefig(save_path, bbox_inches="tight", dpi=200, facecolor="white")
        plt.close()

    @staticmethod
    def plot_metrics_heatmap(
        all_metrics: Dict[str, Dict[str, Dict]],
        strategies: List[str],
        tickers: List[str],
        save_path: str,
    ):
        metric_keys = ["sharpe_ratio", "sortino_ratio", "max_drawdown_pct", "win_rate_pct", "total_return_pct"]
        metric_labels = ["Sharpe", "Sortino", "Max DD (%)", "Win Rate (%)", "Total Return (%)"]

        fig, axes = plt.subplots(1, len(metric_keys), figsize=(22, 8), sharey=True)

        for ax, mkey, mlabel in zip(axes, metric_keys, metric_labels):
            matrix = []
            for ticker in tickers:
                row = []
                for strat in strategies:
                    val = all_metrics.get(ticker, {}).get(strat, {}).get(mkey, 0)
                    if val == "inf":
                        val = 0
                    row.append(float(val))
                matrix.append(row)

            matrix = np.array(matrix)
            cmap = "RdYlGn" if mkey != "max_drawdown_pct" else "RdYlGn_r"
            im = ax.imshow(matrix, aspect="auto", cmap=cmap, interpolation="nearest")
            ax.set_xticks(range(len(strategies)))
            ax.set_xticklabels([s.replace("_", "\n") for s in strategies], fontsize=6, rotation=45, ha="right")
            ax.set_yticks(range(len(tickers)))
            ax.set_yticklabels(tickers, fontsize=8)
            ax.set_title(mlabel, fontweight="bold", fontsize=10)

            for i in range(len(tickers)):
                for j in range(len(strategies)):
                    val = matrix[i, j]
                    text_color = "white" if abs(val) > np.max(abs(matrix)) * 0.6 else "black"
                    ax.text(j, i, f"{val:.1f}", ha="center", va="center", fontsize=5.5, color=text_color)

            fig.colorbar(im, ax=ax, shrink=0.6)

        fig.suptitle("Strategy Performance Heatmap (2022-Present)", fontweight="bold", fontsize=13)
        plt.tight_layout()
        plt.savefig(save_path, bbox_inches="tight", dpi=200, facecolor="white")
        plt.close()

    @staticmethod
    def plot_indicator_panel(df: pd.DataFrame, indicators: pd.DataFrame, ticker: str, save_path: str):
        fig, axes = plt.subplots(5, 1, figsize=(14, 16), gridspec_kw={"height_ratios": [3, 1.2, 1.2, 1.2, 1.2]})
        plt.subplots_adjust(hspace=0.25)

        ax = axes[0]
        ax.plot(indicators.index, indicators["Close"], color="black", linewidth=0.8, label="Close")
        ax.plot(indicators.index, indicators["SMA_20"], color="#2196F3", linewidth=0.7, label="SMA(20)")
        ax.plot(indicators.index, indicators["SMA_50"], color="#FF9800", linewidth=0.7, label="SMA(50)")
        ax.plot(indicators.index, indicators["EMA_12"], color="#4CAF50", linewidth=0.6, linestyle="--", label="EMA(12)")
        ax.plot(indicators.index, indicators["EMA_26"], color="#F44336", linewidth=0.6, linestyle="--", label="EMA(26)")
        ax.fill_between(indicators.index, indicators["BB_Upper"], indicators["BB_Lower"], alpha=0.08, color="purple")
        ax.plot(indicators.index, indicators["BB_Upper"], color="purple", linewidth=0.4, alpha=0.5)
        ax.plot(indicators.index, indicators["BB_Lower"], color="purple", linewidth=0.4, alpha=0.5)
        ax.set_title(f"{ticker} — Price + Indicators", fontweight="bold")
        ax.set_ylabel("Price (USD)")
        ax.legend(loc="upper left", ncol=4, framealpha=0.9, fontsize=7)
        ax.grid(True, alpha=0.3)

        ax = axes[1]
        colors_vol = ["#4CAF50" if df["Close"].iloc[i] >= df["Open"].iloc[i] else "#F44336" for i in range(len(df))]
        ax.bar(df.index, df["Volume"], color=colors_vol, alpha=0.6, width=1.5)
        ax.set_ylabel("Volume")
        ax.set_title("Volume", fontweight="bold")
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x / 1e6:.0f}M"))
        ax.grid(True, alpha=0.3)

        ax = axes[2]
        ax.plot(indicators.index, indicators["RSI_14"], color="#9C27B0", linewidth=0.8)
        ax.axhline(70, color="red", linewidth=0.5, linestyle="--", alpha=0.7)
        ax.axhline(30, color="green", linewidth=0.5, linestyle="--", alpha=0.7)
        ax.axhline(50, color="gray", linewidth=0.4, linestyle=":", alpha=0.5)
        ax.fill_between(indicators.index, 30, indicators["RSI_14"], where=indicators["RSI_14"] < 30, alpha=0.15, color="green")
        ax.fill_between(indicators.index, 70, indicators["RSI_14"], where=indicators["RSI_14"] > 70, alpha=0.15, color="red")
        ax.set_ylabel("RSI")
        ax.set_ylim(0, 100)
        ax.set_title("RSI (14)", fontweight="bold")
        ax.grid(True, alpha=0.3)

        ax = axes[3]
        ax.plot(indicators.index, indicators["MACD"], color="#2196F3", linewidth=0.8, label="MACD")
        ax.plot(indicators.index, indicators["MACD_Signal"], color="#FF9800", linewidth=0.8, label="Signal")
        hist = indicators["MACD_Hist"]
        colors_hist = ["#4CAF50" if v >= 0 else "#F44336" for v in hist]
        ax.bar(indicators.index, hist, color=colors_hist, alpha=0.5, width=1.5)
        ax.axhline(0, color="gray", linewidth=0.4)
        ax.set_ylabel("MACD")
        ax.set_title("MACD (12, 26, 9)", fontweight="bold")
        ax.legend(loc="upper left", framealpha=0.9, fontsize=7)
        ax.grid(True, alpha=0.3)

        ax = axes[4]
        ax.plot(indicators.index, indicators["BB_PctB"], color="#673AB7", linewidth=0.8)
        ax.axhline(1.0, color="red", linewidth=0.5, linestyle="--", alpha=0.7)
        ax.axhline(0.0, color="green", linewidth=0.5, linestyle="--", alpha=0.7)
        ax.axhline(0.5, color="gray", linewidth=0.4, linestyle=":", alpha=0.5)
        ax.set_ylabel("%B")
        ax.set_title("Bollinger %B", fontweight="bold")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.3)

        plt.savefig(save_path, bbox_inches="tight", dpi=200, facecolor="white")
        plt.close()
