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

# This function must be OUTSIDE the class and properly indented to be imported by app.py
def calculate_mmi(vix, nifty_df, fii_flow):
    """
    Optimized MMI with proper indentation and safety gates.
    """
    # Safety gate: Ensure DataFrame has enough data for 90-day indicators
    if nifty_df is None or nifty_df.empty or len(nifty_df) < 95:
        return 50.0

    try:
        # 1. Trend Momentum (90-day SMA)
        nifty_df['90SMA'] = nifty_df['Close'].rolling(window=90).mean()
        curr_price = nifty_df['Close'].iloc[-1].item()
        sma_90 = nifty_df['90SMA'].iloc[-1].item()
        momentum_score = 100 if curr_price > sma_90 else 0

        # 2. Volatility (VIX Mean Reversion)
        vix_val = vix.item() if hasattr(vix, 'item') else float(vix)
        # Scaled VIX score based on Indian market norms (12-25 range)
        vix_score = max(min(100 - ((vix_val - 12) * 6.5), 100), 0)

        # 3. Market Demand (RSI) with Safety Gate
        rsi_series = ta.rsi(nifty_df['Close'], length=14)
        
        if rsi_series is not None and not rsi_series.dropna().empty:
            demand_score = rsi_series.dropna().iloc[-1].item()
        else:
            demand_score = 50.0

        # 4. FII Influence
        fii_score = 100 if float(fii_flow) > 0 else 0

        # Final Weighted Calculation based on professional MMI models
        mmi = (vix_score * 0.3) + (momentum_score * 0.3) + (demand_score * 0.2) + (fii_score * 0.2)
        return round(max(min(mmi, 100), 0), 2)
        
    except Exception as e:
        # Catch-all to prevent app crashes if data fetch fails or is limited
        print(f"MMI Error: {e}")
        return 50.0

def run_swing_scanner(tickers, macro_score):
    """Filters top stocks and includes raw technical data for dashboard display."""
    results = []
    # Scan limit to prevent hitting Yahoo Finance rate limits on Streamlit servers
    for ticker in tickers[:40]:
        try:
            data = yf.download(ticker, period="100d", progress=False)
            if data.empty: continue
            
            # Calculate Technicals for display
            current_price = round(data['Close'].iloc[-1].item(), 2)
            ma50 = round(ta.sma(data['Close'], length=50).iloc[-1].item(), 2)
            rsi = round(ta.rsi(data['Close'], length=14).iloc[-1].item(), 2)
            
            # Logic for Signal: Bullish vs Bearish Macro regimes
            if macro_score > 0 and current_price > ma50:
                signal = "High RS Buy"
                style = "Growth"
            elif macro_score <= 0 and current_price < ma50:
                signal = "Mean Reversion"
                style = "Value"
            else:
                continue # Skip if it doesn't meet specific swing criteria
                
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

def run_sector_scanner(tickers, macro_score, selected_sector=None):
    """Scans stocks within a specific sector to optimize API calls and focus analysis."""
    results = []
    
    # Processed in batches to respect API limits
    for ticker in tickers[:100]:
        try:
            data = yf.download(ticker, period="60d", progress=False)
            if data.empty: continue
            
            price = data['Close'].iloc[-1].item()
            ma50 = ta.sma(data['Close'], length=50).iloc[-1].item()
            rsi = ta.rsi(data['Close'], length=14).iloc[-1].item()
            
            # Filter logic matches the broader scanner but focused on the selected sector
            if macro_score > 0 and price > ma50:
                results.append({"Ticker": ticker, "Style": "Growth", "Signal": "High RS Buy", "RSI": round(rsi, 2)})
            elif macro_score <= 0 and price < ma50:
                results.append({"Ticker": ticker, "Style": "Value", "Signal": "Mean Reversion", "RSI": round(rsi, 2)})
                
            if len(results) >= 5: break 
        except: continue
    return pd.DataFrame(results)
    
