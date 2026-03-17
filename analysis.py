import pandas as pd
import pandas_ta as ta
import sqlite3
import yfinance as yf

class MacroMapper:
    def __init__(self, api_key=None):
        self.api_key = api_key

    def get_macro_sentiment(self):
        """Rule-based sentiment scoring: -1 (Bearish) to +1 (Bullish)"""
        # Crude logic: Higher prices are worse for Indian markets
        crude_score = -0.5 # Placeholder for logic
        usd_inr_score = -0.2
        avg_score = (crude_score + usd_inr_score) / 2
        return round(avg_score, 2)

class PortfolioManager:
    def __init__(self, db_path="portfolio.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        self.conn.execute("CREATE TABLE IF NOT EXISTS logs (date TEXT, nav REAL)")
        self.conn.commit()

    def categorize_style(self, ticker):
        try:
            # Suffix handling for Indian stocks
            symbol = ticker if ticker.endswith((".NS", ".BO")) else ticker + ".NS"
            stock = yf.Ticker(symbol)
            pe = stock.info.get('trailingPE', 25)
            return "Value" if pe < 20 else "Growth"
        except:
            return "Growth"

    def get_action(self, rsi, mmi_score):
        if mmi_score < 30 and rsi < 35: return "Strong Buy"
        if mmi_score > 70 and rsi > 65: return "Sell/Trim"
        return "Hold"

def calculate_mmi(vix, nifty_df, fii_flow):
    if nifty_df is None or nifty_df.empty or len(nifty_df) < 90:
        return 50.0

    nifty_df['30EMA'] = ta.ema(nifty_df['Close'], length=30)
    nifty_df['90EMA'] = ta.ema(nifty_df['Close'], length=90)
    
    ema_30 = nifty_df['30EMA'].iloc[-1]
    ema_90 = nifty_df['90EMA'].iloc[-1]
    
    momentum = 1 if (not pd.isna(ema_30) and ema_30 > ema_90) else -1
    
    # FIX: Use .item() or float() on a scalar to avoid the Series Warning
    vix_val = vix.item() if hasattr(vix, 'item') else float(vix)
    vix_score = max(min(100 - (vix_val * 2), 100), 0)
    
    try:
        fii_bonus = 30 if float(fii_flow) > 0 else 0
    except:
        fii_bonus = 0

    mmi = (vix_score * 0.4) + (momentum * 30) + fii_bonus
    return max(min(mmi, 100), 0)

def run_swing_scanner(tickers, macro_score):
    """Filters top stocks and includes raw technical data."""
    results = []
    for ticker in tickers[:40]:
        try:
            data = yf.download(ticker, period="100d", progress=False)
            if data.empty: continue
            
            # Calculate Technicals
            current_price = round(data['Close'].iloc[-1].item(), 2)
            ma50 = round(ta.sma(data['Close'], length=50).iloc[-1].item(), 2)
            rsi = round(ta.rsi(data['Close'], length=14).iloc[-1].item(), 2)
            
            # Logic for Signal
            if macro_score > 0 and current_price > ma50:
                signal = "High RS Buy"
                style = "Growth"
            elif macro_score <= 0 and current_price < ma50:
                signal = "Mean Reversion"
                style = "Value"
            else:
                continue # Skip if it doesn't meet the primary swing criteria
                
            results.append({
                "Ticker": ticker, 
                "Price": current_price,
                "50DMA": ma50, 
                "RSI": rsi,
                "Style": style, 
                "Signal": signal
            })
            
            if len(results) >= 5: break 
        except: continue
    return pd.DataFrame(results)
