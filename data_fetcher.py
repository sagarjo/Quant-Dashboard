import yfinance as yf
from nsepython import nse_fii_dii
import pandas as pd

def fetch_stock_data(ticker, period="1y"):
    """Fetches historical data with .NS suffix handling."""
    if not ticker.endswith(".NS"):
        ticker += ".NS"
    return yf.download(ticker, period=period, interval="1d")

def get_market_context():
    """Fetches India VIX and Nifty 50 for MMI calculation."""
    vix = yf.download("^INDIAVIX", period="1d")['Close'].iloc[-1]
    nifty = yf.download("^NSEI", period="100d")
    # Fetch FII/DII flow via nsepython
    fii_dii = nse_fii_dii()
    return vix, nifty, fii_dii
  
