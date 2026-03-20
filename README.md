
# Proyecto de Investigación Aplicada en Mercados Financieros  
## Backtesting Avanzado y Validación de Indicadores Técnicos en Python

Proyecto semestral desarrollado en el Tecnológico de Monterrey para el curso **Proyecto de Investigación Aplicada en Mercados Financieros (Primavera 2026)**. El objetivo del proyecto es construir un sistema modular en Python para:

- descargar datos históricos de mercado,
- calcular indicadores técnicos,
- generar señales de compra y venta,
- validar dichas señales contra TradingView,
- y sentar la base para backtesting comparativo de estrategias.  

El universo de análisis incluye las **7 Magníficas** y dos empresas industriales seleccionadas: **NVDA, AAPL, MSFT, META, GOOGL, TSLA, AMZN, GE y HD**

---

## Objetivos del proyecto

Este repositorio busca integrar en un solo flujo de trabajo:

1. **Arquitectura modular de backtesting**, con separación clara entre adquisición de datos, indicadores, generación de señales, simulación, métricas y reportes. 
2. **Implementación de indicadores técnicos estándar**:  
   - SMA  
   - EMA  
   - RSI  
   - MACD  
   - Bollinger Bands : 
3. **Generación de señales programáticas** mediante estrategias basadas en:
   - cruces SMA,
   - reversión a la media con RSI,
   - cruces MACD. :  
4. **Validación visual y comparativa con TradingView** para verificar coincidencia de señales y detectar discrepancias por ajustes, zona horaria o inicialización numérica. :  

---

## Estructura general del proyecto

La arquitectura propuesta en el Entregable 1 plantea una organización modular como la siguiente: : 

```text
backtesting-project/
│
├── README.md
├── requirements.txt
├── backtesting_engine.py
│
├── config/
│   └── settings.json
│
├── data/
│   └── raw/
│
├── indicators/
│   ├── __init__.py
│   ├── trend.py
│   ├── momentum.py
│   └── volatility.py
│
├── strategies/
│   ├── __init__.py
│   ├── sma_crossover.py
│   ├── rsi_reversion.py
│   └── macd_crossover.py
│
├── engine/
│   ├── __init__.py
│   ├── backtest.py
│   ├── portfolio.py
│   └── metrics.py
│
├── reports/
│   ├── __init__.py
│   └── generator.py
│
├── notebooks/
│   └── exploratory.ipynb
│
├── results/
│   ├── metrics/
│   └── trades/
│
├── evidence/
│   ├── tradingview_account.png
│   ├── tradingview_paper.png
│   ├── alpaca_account.png
│   └── alpaca_paper.png
│
└── docs/
    └── architecture.pdf
