"""Module for configuration settings."""
from dataclasses import dataclass
import pandas as pd
import yfinance as yf


@dataclass(frozen=True)
class BaseSettings:
    """Settings common to both prod and dev runs."""


@dataclass(frozen=True)
class DevSettings(BaseSettings):
    """Developer settings"""
    df = pd.read_csv(r"C:\Users\gianm\OneDrive\Desktop\ticker.csv")
    live_price = 8.3240


@dataclass(frozen=True)
class ProdSettings(BaseSettings):
    """Production settings"""
    ticker = 'STLAM.MI'
    period = "1mo"
    interval = "30m"
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    df.reset_index(inplace=True)
    live_price = yf.Ticker(ticker).fast_info["lastPrice"]
