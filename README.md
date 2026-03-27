# 📈 Stock Market Dashboard

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Plotly Dash](https://img.shields.io/badge/Plotly_Dash-3F4F75?style=flat-square&logo=plotly&logoColor=white)](https://dash.plotly.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

An interactive financial analytics dashboard that pulls **live stock data** and visualizes price history, technical indicators, and volatility metrics. Supports multi-ticker comparison, date range selection, and price forecasting with Facebook Prophet.

---

## ✨ Features

- **Live data** via `yfinance` — OHLCV data for any ticker on Yahoo Finance
- **Candlestick charts** with volume overlay
- **Technical indicators** — SMA (20/50/200), EMA, Bollinger Bands, RSI, MACD
- **30-day price forecast** using Facebook Prophet with confidence intervals
- **Multi-ticker comparison** — normalized performance across multiple stocks
- **Volatility analysis** — rolling standard deviation and annualized volatility
- **Exportable charts** — download any chart as PNG or CSV

---

## 🚀 Quick Start

```bash
git clone https://github.com/TheCromazone/stock-dashboard.git
cd stock-dashboard
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:8050` in your browser.

---

## 🏗️ Project Structure

```
stock-dashboard/
├── app.py              # Dash application entry point
├── data/
│   ├── fetcher.py      # yfinance data loading + caching
│   └── indicators.py   # Technical indicator calculations
├── components/
│   ├── charts.py       # Reusable Plotly chart builders
│   └── layout.py       # Dash layout components
├── forecast/
│   └── prophet_model.py  # Prophet forecasting wrapper
├── requirements.txt
└── README.md
```

---

## 📊 Technical Indicators

| Indicator | Description |
|---|---|
| SMA 20/50/200 | Simple Moving Averages |
| EMA 12/26 | Exponential Moving Averages |
| Bollinger Bands | ±2σ price channel |
| RSI (14) | Relative Strength Index |
| MACD | Moving Average Convergence Divergence |
| ATR | Average True Range (volatility) |

---

## 🔮 Forecasting

Uses [Facebook Prophet](https://facebook.github.io/prophet/) to generate a 30-day forward price forecast. The model accounts for weekly/yearly seasonality and produces 80% and 95% confidence intervals.

> **Disclaimer**: This is for educational and visualization purposes only. Nothing here constitutes financial advice.

---

## 🛠️ Tech Stack

- `yfinance` — live market data
- `plotly` / `dash` — interactive charting and web UI
- `prophet` — time series forecasting
- `pandas` — data manipulation
- `numpy` — numerical computations
- `ta` — techical analysis library

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
