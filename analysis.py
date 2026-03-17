import pandas as pd
import pandas_ta as ta

def calculate_mmi(vix, nifty_df, fii_flow):
    """
    MMI Engine: Calculates Market Mood with safety checks.
    """
    # Ensure we have enough data for EMAs
    if nifty_df is None or len(nifty_df) < 90:
        return 50.0 # Neutral fallback

    # Calculate EMAs
    nifty_df['30EMA'] = ta.ema(nifty_df['Close'], length=30)
    nifty_df['90EMA'] = ta.ema(nifty_df['Close'], length=90)
    
    # Defensive check: Ensure the last values are not NaN
    ema_30 = nifty_df['30EMA'].iloc[-1]
    ema_90 = nifty_df['90EMA'].iloc[-1]
    
    if pd.isna(ema_30) or pd.isna(ema_90):
        momentum = 0 # Neutral if calculation fails
    else:
        momentum = 1 if ema_30 > ema_90 else -1
    
    # Normalize VIX Score (assuming VIX usually stays between 10-35)
    vix_score = 100 - (float(vix) * 2) 
    vix_score = max(min(vix_score, 100), 0)
    
    # Calculate final MMI
    try:
        fii_val = float(fii_flow)
        fii_bonus = 30 if fii_val > 0 else 0
    except (TypeError, ValueError):
        fii_bonus = 0

    mmi = (vix_score * 0.4) + (momentum * 30) + fii_bonus
    return max(min(mmi, 100), 0)
    
