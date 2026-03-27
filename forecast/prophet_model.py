"""
prophet_model.py — 30-day stock price forecasting with Facebook Prophet.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from prophet import Prophet


class ProphetForecaster:
    """
    Wraps Facebook Prophet for stock price forecasting.

    Notes:
      - Uses daily closing prices as the target variable.
      - Accounts for weekly seasonality; yearly seasonality is inferred from data length.
      - Outputs 80% and 95% prediction intervals.
    """

    def __init__(self, uncertainty_samples: int = 1000) -> None:
        self._uncertainty_samples = uncertainty_samples

    def fit_predict(self, df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
        """
        Fit Prophet on historical close prices and forecast `periods` days ahead.

        Args:
            df:      DataFrame with DatetimeIndex and a 'Close' column.
            periods: Number of calendar days to forecast.

        Returns:
            Prophet forecast DataFrame (ds, yhat, yhat_lower, yhat_upper, etc.)
        """
        prophet_df = df[["Close"]].reset_index().rename(
            columns={"Date": "ds", "Close": "y"}
        )
        prophet_df["ds"] = pd.to_datetime(prophet_df["ds"]).dt.tz_localize(None)

        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=(len(prophet_df) > 365),
            interval_width=0.80,
            uncertainty_samples=self._uncertainty_samples,
            changepoint_prior_scale=0.1,
        )
        model.fit(prophet_df)

        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        return forecast

    def plot(self, forecast: pd.DataFrame, ticker: str) -> go.Figure:
        """Build a Plotly figure showing the Prophet forecast."""
        historical = forecast[forecast["ds"] <= forecast["ds"].max() - pd.Timedelta(days=30)]
        future = forecast.tail(30)

        fig = go.Figure()

        # Historical fitted values
        fig.add_trace(go.Scatter(
            x=historical["ds"], y=historical["yhat"],
            mode="lines", name="Historical Fit",
            line=dict(color="#2563EB", width=1.5),
        ))

        # Forecast line
        fig.add_trace(go.Scatter(
            x=future["ds"], y=future["yhat"],
            mode="lines", name="Forecast",
            line=dict(color="#F59E0B", width=2, dash="dash"),
        ))

        # Confidence interval
        fig.add_trace(go.Scatter(
            x=pd.concat([future["ds"], future["ds"][::-1]]),
            y=pd.concat([future["yhat_upper"], future["yhat_lower"][::-1]]),
            fill="toself",
            fillcolor="rgba(245,158,11,0.15)",
            line=dict(color="rgba(0,0,0,0)"),
            name="80% Confidence Interval",
        ))

        fig.update_layout(
            title=f"{ticker} — 30-Day Prophet Forecast",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            margin=dict(l=40, r=20, t=50, b=40),
        )
        return fig
