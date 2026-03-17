import pandas as pd
import pandas_ta as ta
import sqlite3
from fpdf import FPDF

class MacroMapper:
    def __init__(self, api_key):
        self.api_key = api_key

    def score_headlines(self, headlines):
        """Placeholder for LLM Analysis Logic."""
        # In production: response = openai.ChatCompletion.create(...)
        # Returning dummy scores for logic flow
        return {"Fed": 0.5, "Crude": -0.2, "USDINR": -0.1}

class PortfolioManager:
    def __init__(self, db_path="portfolio.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS logs (date TEXT, nav REAL)")

    def categorize_style(self, ticker):
        """Categorizes based on simple P/E and Growth metrics."""
        stock = yf.Ticker(ticker + ".NS")
        info = stock.info
        pe = info.get('trailingPE', 25)
        # Value if PE < 20, else Growth
        return "Value" if pe < 20 else "Growth"

    def get_action(self, rsi, mmi_score):
        if mmi_score < 30 and rsi < 35: return "Strong Buy"
        if mmi_score > 70 and rsi > 65: return "Sell/Trim"
        return "Hold"

def calculate_mmi(vix, nifty_df, fii_flow):
    """
    MMI Engine: Calculates Market Mood.
    Logic: Low VIX + High Momentum + FII Buy = Extreme Greed.
    """
    nifty_df['30EMA'] = ta.ema(nifty_df['Close'], length=30)
    nifty_df['90EMA'] = ta.ema(nifty_df['Close'], length=90)
    
    momentum = 1 if nifty_df['30EMA'].iloc[-1] > nifty_df['90EMA'].iloc[-1] else -1
    vix_score = 100 - (vix * 2) # Normalizing VIX
    
    mmi = (vix_score * 0.4) + (momentum * 30) + (30 if float(fii_flow) > 0 else 0)
    return max(min(mmi, 100), 0)

