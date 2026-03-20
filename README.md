# Backtesting Avanzado — 7 Magníficas & Industriales

## Proyecto de Investigación Aplicada en Mercados Financieros
**Tecnológico de Monterrey — Escuela de Ingeniería y Ciencias**
**Primavera 2026 | Equipo 1**

---

## Descripción

Sistema modular y reproducible de backtesting en Python aplicado a acciones de alta capitalización ("7 Magníficas") y empresas industriales seleccionadas, complementado con validación en TradingView y paper trading en Alpaca.

**Periodo de análisis:** 1 enero 2022 — presente (actualización dinámica).

## Universo de Análisis

| Categoría | Tickers |
|-----------|---------|
| 7 Magníficas | NVDA, AAPL, MSFT, META, GOOGL, TSLA, AMZN |
| Industriales | GE, HD |

## Estructura del Repositorio

```
backtesting-project/
├── README.md
├── requirements.txt
├── backtesting_engine.py          # Entry point principal
├── config/
│   └── settings.json              # Parámetros globales
├── data/
│   └── raw/                       # Datos descargados (gitignore)
├── indicators/
│   ├── __init__.py
│   ├── trend.py                   # SMA, EMA
│   ├── momentum.py                # RSI, MACD
│   └── volatility.py              # Bollinger Bands
├── strategies/
│   ├── __init__.py
│   ├── sma_crossover.py
│   ├── rsi_reversion.py
│   ├── macd_crossover.py
│   ├── bollinger_bounce.py
│   ├── bollinger_squeeze.py
│   ├── combined_macd_rsi.py
│   ├── combined_sma_bb.py
│   └── combined_triple.py
├── engine/
│   ├── __init__.py
│   ├── backtest.py                # Motor de simulación
│   ├── portfolio.py               # Estado del portafolio
│   └── metrics.py                 # Sharpe, Sortino, Drawdown
├── reports/
│   ├── __init__.py
│   └── generator.py               # JSON, CSV, consola
├── notebooks/
│   └── exploratory.ipynb          # Análisis exploratorio
├── results/
│   ├── metrics/                   # JSON con métricas
│   └── trades/                    # CSV de operaciones
├── evidence/
│   ├── tradingview_account.png
│   ├── tradingview_paper.png
│   ├── alpaca_account.png
│   └── alpaca_paper.png
└── docs/
    ├── entregable1_arquitectura.pdf
    ├── entregable2_notebook.pdf
    └── entregable3_estrategias.pdf
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

## Uso

```bash
# Ejecutar backtesting completo (8 estrategias × 9 tickers)
python backtesting_engine.py

# Los resultados se exportan a results/
```

## Estrategias Implementadas

### Individuales
1. **SMA Crossover** — Cruce de SMA(20) / SMA(50)
2. **RSI Mean Reversion** — Sobreventa (<30) / Sobrecompra (>70)
3. **MACD Crossover** — Cruce MACD / Signal line
4. **Bollinger Bounce** — Reversión desde bandas exteriores
5. **Bollinger Squeeze** — Breakout tras compresión de volatilidad

### Combinadas
6. **MACD + RSI** — Momentum filtrado por RSI
7. **SMA + Bollinger** — Tendencia + pullback en bandas
8. **Triple Confluence** — SMA + MACD + RSI simultáneos

## Métricas Calculadas

- Total Return, Annualized Return, Annualized Volatility
- Sharpe Ratio, Sortino Ratio
- Max Drawdown
- Win Rate, Avg Win/Loss, Profit Factor

## Herramientas

- **Python** — Backtesting programático
- **TradingView** — Validación visual + Pine Script + Paper Trading
- **Alpaca** — Paper Trading API (Fase 3+)

## Equipo

Equipo 1 — Tecnológico de Monterrey, Primavera 2026
