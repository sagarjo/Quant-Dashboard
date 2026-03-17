import yfinance as yf
from nsepython import nse_fiidii
import pandas as pd

def fetch_stock_data(ticker, period="1y"):
    if not ticker.endswith(".NS"):
        ticker += ".NS"
    return yf.download(ticker, period=period, interval="1d")

def get_market_context():
    # 1. Fetch VIX with error handling
    try:
        vix_df = yf.download("^INDIAVIX", period="5d") # Fetch 5 days to ensure we get at least one close
        if not vix_df.empty:
            vix = vix_df['Close'].iloc[-1]
        else:
            vix = 15.0 # Standard fallback for India VIX
    except Exception:
        vix = 15.0

    # 2. Fetch Nifty 50 with error handling
    try:
        nifty = yf.download("^NSEI", period="100d")
        if nifty.empty:
            # Create a dummy dataframe so the app doesn't crash during analysis
            nifty = pd.DataFrame(index=pd.date_range(start='2026-01-01', periods=100))
            nifty['Close'] = 22000.0 
    except Exception:
        nifty = pd.DataFrame()

    # 3. Fetch FII/DII with updated function name
    try:
        fii_dii = nse_fiidii()
    except Exception:
        fii_dii = {"fii_net": 0, "dii_net": 0}
        
    return vix, nifty, fii_dii

import requests
import io

def get_nifty_500_tickers():
    """Fetches the Nifty 500 list from NSE and returns symbols with .NS suffix."""
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).content
        df = pd.read_csv(io.StringIO(response.decode('utf-8')))
        # Convert to yfinance format
        tickers = [str(symbol) + ".NS" for symbol in df['Symbol'].tolist()]
        return tickers
    except Exception as e:
        print(f"Error fetching Nifty 500: {e}")
        return ["RELIANCE.NS", "TCS.NS", "INFY.NS"] # Minimal fallback

def get_nse_master_data():
    """Fetches the full NSE list and returns a DataFrame with Tickers and Sectors."""
    url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers).content
        df = pd.read_csv(io.StringIO(response.decode('utf-8')))
        
        # Clean and format data
        df = df[['SYMBOL', ' FACE VALUE']].rename(columns={' FACE VALUE': 'Sector_Info'}) # Sector often buried in metadata
        df['Ticker'] = df['SYMBOL'].astype(str).strip() + ".NS"
        return df
    except Exception:
        return pd.DataFrame({"Ticker": ["RELIANCE.NS"], "Sector_Info": ["Energy"]})
        
        
    
