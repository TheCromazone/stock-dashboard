"""
app.py — Stock Market Dashboard (Plotly Dash)
Author: Matthew Cromaz (TheCromazone)

Interactive financial analytics dashboard with live data, technical indicators,
and 30-day price forecasting.

Run: python app.py
"""

from __future__ import annotations

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from datetime import date, timedelta

from data.fetcher import StockDataFetcher
from data.indicators import TechincalIndicators
from components.charts import (
    build_candlestick_chart,
    build_volume_chart,
    build_rsi_chart,
    build_macd_chart,
    build_comparison_chart,
)
from forecast.prophet_model import ProphetForecaster

# ─── App Init ─────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="Stock Dashboard",
    suppress_callback_exceptions=True,
)

fetcher = StockDataFetcher(cache_ttl_minutes=5)
forecaster = ProphetForecaster()

# ─── Layout ───────────────────────────────────────────────────────────────────
app.layout = dbc.Container(
    fluid=True,
    children=[
        # ── Header ───────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col(html.H2("📈 Stock Market Dashboard", className="text-white my-3")),
        ]),

        # ── Controls ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                dbc.Label("Ticker Symbol(s)", className="text-white"),
                dcc.Input(
                    id="ticker-input",
                    type="text",
                    value="AAPL",
                    placeholder="e.g. AAPL, MSFT, TSLA",
                    debounce=True,
                    className="form-control",
                ),
            ], md=3),

            dbc.Col([
                dbc.Label("Date Range", className="text-white"),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=(date.today() - timedelta(days=365)).isoformat(),
                    end_date=date.today().isoformat(),
                    display_format="MMM D, YYYY",
                ),
            ], md=4),

            dbc.Col([
                dbc.Label("Indicators", className="text-white"),
                dcc.Dropdown(
                    id="indicator-select",
                    options=[
                        {"label": "SMA 20", "value": "sma20"},
                        {"label": "SMA 50", "value": "sma50"},
                        {"label": "SMA 200", "value": "sma200"},
                        {"label": "EMA 12", "value": "ema12"},
                        {"label": "Bollinger Bands", "value": "bb"},
                    ],
                    value=["sma20", "sma50"],
                    multi=True,
                    className="dark-dropdown",
                ),
            ], md=4),

            dbc.Col([
                dbc.Label(" ", className="text-white d-block"),
                dbc.Button("Update", id="update-btn", color="primary", n_clicks=0),
            ], md=1),
        ], className="mb-3"),

        # ── Summary Cards ─────────────────────────────────────────────────────
        dbc.Row(id="summary-cards", className="mb-3"),

        # ── Main Chart ────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col(dcc.Graph(id="candlestick-chart", style={"height": "500px"}), md=12),
        ]),

        # ── Volume + RSI + MACD ──────────────────────────────────────────────
        dbc.Row([
            dbc.Col(dcc.Graph(id="volume-chart", style={"height": "200px"}), md=12),
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id="rsi-chart", style={"height": "200px"}), md=6),
            dbc.Col(dcc.Graph(id="macd-chart", style={"height": "200px"}), md=6),
        ]),

        # ── Forecast ──────────────────────────────────────────────────────────
        dbc.Row([
            dbc.Col([
                html.H5("30-Day Price Forecast (Prophet)", className="text-white mt-4"),
                dcc.Graph(id="forecast-chart", style={"height": "350px"}),
                html.P(
                    "⚠️ Educational purposes only — not financial advice.",
                    className="text-muted small",
                ),
            ])
        ]),
    ],
)


# ─── Callbacks ────────────────────────────────────────────────────────────────
@callback(
    Output("candlestick-chart", "figure"),
    Output("volume-chart", "figure"),
    Output("rsi-chart", "figure"),
    Output("macd-chart", "figure"),
    Output("forecast-chart", "figure"),
    Output("summary-cards", "children"),
    Input("update-btn", "n_clicks"),
    State("ticker-input", "value"),
    State("date-range", "start_date"),
    State("date-range", "end_date"),
    State("indicator-select", "value"),
    prevent_initial_call=False,
)
def update_charts(n_clicks, tickers_raw, start_date, end_date, indicators):
    ticker = tickers_raw.split(",")[0].strip().upper()

    df = fetcher.fetch(ticker, start=start_date, end=end_date)
    df = TechnicalIndicators.add_all(df)

    candlestick_fig = build_candlestick_chart(df, ticker, indicators or [])
    volume_fig = build_volume_chart(df, ticker)
    rsi_fig = build_rsi_chart(df, ticker)
    macd_fig = build_macd_chart(df, ticker)

    # Forecast
    forecast_df = forecaster.fit_predict(df, periods=30)
    forecast_fig = forecaster.plot(forecast_df, ticker)

    # Summary cards
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    change = latest["Close"] - prev["Close"]
    pct_change = change / prev["Close"] * 100
    color = "success" if change >= 0 else "danger"
    arrow = "▲" if change >= 0 else "▼"

    cards = [
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Last Close", className="card-title text-muted"),
            html.H4(f"${latest['Close']:.2f}", className="card-text"),
            html.Small(f"{arrow} {abs(change):.2f} ({pct_change:+.2f}%)", className=f"text-{color}"),
        ])), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("Volume", className="card-title text-muted"),
            html.H4(f"{int(latest['Volume']):,}", className="card-text"),
        ])), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("52W High", className="card-title text-muted"),
            html.H4(f"${df['High'].tail(252).max():.2f}", className="card-text"),
        ])), md=3),
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6("52W Low", className="card-title text-muted"),
            html.H4(f"${df['Low'].tail(252).min():.2f}", className="card-text"),
        ])), md=3),
    ]

    return candlestick_fig, volume_fig, rsi_fig, macd_fig, forecast_fig, cards


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
