import pandas as pd
import pandas_ta as ta
import sqlite3
import yfinance as yf

class MacroMapper_API:
    def __init__(self, api_key="placeholder"):
        self.api_key = api_key

    def score_headlines(self, headlines=None):
        # Mock logic for the analyzer
        return {"Fed": 0.5, "Crude": -0.2, "USDINR": -0.1}


class MacroMapper:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_macro_sentiment(self):
        """
        Rule-based sentiment scoring without an LLM.
        Scoring: -1 (Very Bearish for India) to +1 (Very Bullish).
        """
        # Logic 1: Crude Oil (High prices hurt Indian Fiscal Deficit)
        # Mocking a crude check; in production, you'd fetch 'CL=F' from yfinance
        crude_price = 80 
        crude_score = -0.5 if crude_price > 75 else 0.3
        
        # Logic 2: USD-INR (Weak Rupee is bad for imports/inflation)
        usd_inr = 83.5
        currency_score = -0.4 if usd_inr > 83 else 0.2
        
        # Logic 3: US Fed (High rates lead to FII outflow from India)
        fed_stance = "Hawkish" # Mocked
        fed_score = -0.6 if fed_stance == "Hawkish" else 0.5
        
        total_score = (crude_score + currency_score + fed_score) / 3
        return round(total_score, 2)


class PortfolioManager:
    def __init__(self, db_path="portfolio.db"):
        # check_same_thread=False is required for SQLite on Streamlit
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS logs (date TEXT, nav REAL)")
        self.conn.commit()

    def categorize_style(self, ticker):
        try:
            stock = yf.Ticker(ticker if ticker.endswith(".NS") else ticker + ".NS")
            info = stock.info
            pe = info.get('trailingPE', 25)
            return "Value" if pe < 20 else "Growth"
        except:
            return "Growth"

    def get_action(self, rsi, mmi_score):
        if mmi_score < 30 and rsi < 35: return "Strong Buy"
        if mmi_score > 70 and rsi > 65: return "Sell/Trim"
        return "Hold"

def calculate_mmi(vix, nifty_df, fii_flow):
    """
    MMI Engine: Calculates Market Mood with safety checks.
    """
    if nifty_df is None or len(nifty_df) < 90:
        return 50.0

    # Calculate EMAs using pandas_ta
    nifty_df['30EMA'] = ta.ema(nifty_df['Close'], length=30)
    nifty_df['90EMA'] = ta.ema(nifty_df['Close'], length=90)
    
    ema_30 = nifty_df['30EMA'].iloc[-1]
    ema_90 = nifty_df['90EMA'].iloc[-1]
    
    if pd.isna(ema_30) or pd.isna(ema_90):
        momentum = 0
    else:
        momentum = 1 if ema_30 > ema_90 else -1
    
    vix_score = 100 - (float(vix) * 2) 
    vix_score = max(min(vix_score, 100), 0)
    
    try:
        fii_val = float(fii_flow)
        fii_bonus = 30 if fii_val > 0 else 0
    except:
        fii_bonus = 0

    mmi = (vix_score * 0.4) + (momentum * 30) + fii_bonus
    return max(min(mmi, 100), 0)
    
