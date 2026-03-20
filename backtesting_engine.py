import sys
import os
import json
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from indicators import sma, ema, rsi, macd, bollinger_bands
from strategies import STRATEGY_REGISTRY
from engine import BacktestEngine, compute_metrics
from reports import ReportGenerator


def load_settings(path="config/settings.json"):
    with open(path, "r") as f:
        return json.load(f)


def fetch_data(tickers, start, end):
    data = {}
    for ticker in tickers:
        df = yf.download(ticker, start=start, end=end, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df[["Open", "High", "Low", "Close", "Volume"]].copy()
        df.dropna(inplace=True)
        data[ticker] = df
    return data


def compute_all_indicators(df, cfg):
    close = df["Close"]
    ind = pd.DataFrame(index=df.index)
    ind["Close"] = close
    ind["Open"] = df["Open"]
    ind["High"] = df["High"]
    ind["Low"] = df["Low"]
    ind["Volume"] = df["Volume"]
    ind["SMA_20"] = sma(close, cfg["sma_fast"])
    ind["SMA_50"] = sma(close, cfg["sma_slow"])
    ind["EMA_12"] = ema(close, cfg["ema_fast"])
    ind["EMA_26"] = ema(close, cfg["ema_slow"])
    ind["RSI_14"] = rsi(close, cfg["rsi_period"])
    ind["MACD"], ind["MACD_Signal"], ind["MACD_Hist"] = macd(
        close, cfg["macd_fast"], cfg["macd_slow"], cfg["macd_signal"]
    )
    ind["BB_Upper"], ind["BB_Mid"], ind["BB_Lower"], ind["BB_PctB"], ind["BB_Width"] = bollinger_bands(
        close, cfg["bb_window"], cfg["bb_num_std"]
    )
    return ind


def main():
    settings = load_settings()

    tickers = settings["tickers"]["magnificent_7"] + settings["tickers"]["industrials"]
    start = settings["data"]["start_date"]
    end = datetime.now().strftime("%Y-%m-%d") if settings["data"]["end_date"] == "auto" else settings["data"]["end_date"]
    bt_cfg = settings["backtest"]
    ind_cfg = settings["indicators"]

    results_dir = settings["output"]["results_dir"]
    metrics_dir = os.path.join(results_dir, settings["output"]["metrics_subdir"])
    trades_dir = os.path.join(results_dir, settings["output"]["trades_subdir"])
    plots_dir = os.path.join(results_dir, "plots")
    os.makedirs(metrics_dir, exist_ok=True)
    os.makedirs(trades_dir, exist_ok=True)
    os.makedirs(plots_dir, exist_ok=True)

    print(f"Descargando datos para {len(tickers)} tickers ({start} -> {end})...")
    data = fetch_data(tickers, start, end)

    engine = BacktestEngine(
        initial_capital=bt_cfg["initial_capital"],
        commission=bt_cfg["commission"],
        position_size_pct=bt_cfg["position_size_pct"],
    )
    reporter = ReportGenerator()

    all_metrics = {}
    all_rows = []

    for ticker in tickers:
        df = data.get(ticker)
        if df is None or df.empty:
            print(f"  {ticker}: sin datos, saltando.")
            continue

        print(f"\n{'=' * 60}")
        print(f"  {ticker}")
        print(f"{'=' * 60}")

        indicators = compute_all_indicators(df, ind_cfg)
        equity_curves = {}

        all_metrics[ticker] = {}

        for strat_name, strat_func in STRATEGY_REGISTRY.items():
            signals = strat_func(df)
            portfolio = engine.run(df, signals, ticker)
            eq_array = np.array(portfolio.equity_curve)
            metrics = compute_metrics(eq_array, portfolio.trades, bt_cfg["risk_free_rate"])

            all_metrics[ticker][strat_name] = metrics
            equity_curves[strat_name] = eq_array

            row = {"ticker": ticker, "strategy": strat_name}
            row.update(metrics)
            all_rows.append(row)

            print(reporter.summary(metrics, ticker, strat_name))

            safe = f"{ticker}_{strat_name}"
            reporter.to_json(metrics, os.path.join(metrics_dir, f"{safe}_metrics.json"))
            reporter.trades_to_csv(portfolio.trades, os.path.join(trades_dir, f"{safe}_trades.csv"))

        reporter.plot_equity_comparison(equity_curves, ticker, os.path.join(plots_dir, f"{ticker}_equity.png"), bt_cfg["initial_capital"])
        reporter.plot_indicator_panel(df, indicators, ticker, os.path.join(plots_dir, f"{ticker}_indicators.png"))

    reporter.plot_metrics_heatmap(
        all_metrics,
        list(STRATEGY_REGISTRY.keys()),
        tickers,
        os.path.join(plots_dir, "metrics_heatmap.png"),
    )

    summary_df = pd.DataFrame(all_rows)
    summary_df.to_csv(os.path.join(results_dir, "summary_all.csv"), index=False)

    with open(os.path.join(metrics_dir, "all_metrics.json"), "w") as f:
        json.dump(all_metrics, f, indent=2)

    print(f"\n{'=' * 60}")
    print("  TOP 15 — RANKING GLOBAL POR SHARPE RATIO")
    print(f"{'=' * 60}")
    ranking = summary_df.sort_values("sharpe_ratio", ascending=False).head(15)
    for i, (_, r) in enumerate(ranking.iterrows(), 1):
        print(f"  {i:>2}. {r['ticker']:<6} {r['strategy']:<25} Sharpe: {r['sharpe_ratio']:>8}  Return: {r['total_return_pct']:>8}%")
    print(f"{'=' * 60}")
    print(f"\nResultados exportados en: {results_dir}/")


if __name__ == "__main__":
    main()
