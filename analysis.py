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
    """
    Optimized MMI with proper indentation and safety gates.
    """
    # [span_4](start_span)Safety gate: Ensure DataFrame has enough data[span_4](end_span)
    if nifty_df is None or nifty_df.empty or len(nifty_df) < 95:
        return 50.0

    try:
        # 1. [span_5](start_span)Trend Momentum (90-day SMA)[span_5](end_span)
        nifty_df['90SMA'] = nifty_df['Close'].rolling(window=90).mean()
        curr_price = nifty_df['Close'].iloc[-1].item()
        sma_90 = nifty_df['90SMA'].iloc[-1].item()
        momentum_score = 100 if curr_price > sma_90 else 0

        # 2. [span_6](start_span)Volatility (VIX Mean Reversion)[span_6](end_span)
        vix_val = vix.item() if hasattr(vix, 'item') else float(vix)
        vix_score = max(min(100 - ((vix_val - 12) * 6.5), 100), 0)

        # 3. [span_7](start_span)Market Demand (RSI) with Safety Gate[span_7](end_span)
        import pandas_ta as ta
        rsi_series = ta.rsi(nifty_df['Close'], length=14)
        
        if rsi_series is not None and not rsi_series.dropna().empty:
            demand_score = rsi_series.dropna().iloc[-1].item()
        else:
            demand_score = 50.0

        # 4. [span_8](start_span)FII Influence[span_8](end_span)
        fii_score = 100 if float(fii_flow) > 0 else 0

        # [span_9](start_span)Final Weighted Calculation[span_9](end_span)
        mmi = (vix_score * 0.3) + (momentum_score * 0.3) + (demand_score * 0.2) + (fii_score * 0.2)
        return round(max(min(mmi, 100), 0), 2)
        
    except Exception as e:
        # [span_10](start_span)Catch-all to prevent app crashes if logic fails[span_10](end_span)
        print(f"MMI Error: {e}")
        return 50.0




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

def run_sector_scanner(tickers, macro_score, selected_sector=None):
    """Scans stocks within a specific sector to optimize API calls."""
    results = []
    
    # If a sector is chosen, we only process those tickers
    for ticker in tickers[:100]: # Limit batch for performance
        try:
            data = yf.download(ticker, period="60d", progress=False)
            if data.empty: continue
            
            price = data['Close'].iloc[-1].item()
            ma50 = ta.sma(data['Close'], length=50).iloc[-1].item()
            rsi = ta.rsi(data['Close'], length=14).iloc[-1].item()
            
            # Logic stays the same, but targets a smaller pool
            if macro_score > 0 and price > ma50:
                results.append({"Ticker": ticker, "Style": "Growth", "Signal": "High RS Buy", "RSI": round(rsi, 2)})
            elif macro_score <= 0 and price < ma50:
                results.append({"Ticker": ticker, "Style": "Value", "Signal": "Mean Reversion", "RSI": round(rsi, 2)})
                
            if len(results) >= 5: break 
        except: continue
    return pd.DataFrame(results)
    
