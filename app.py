import streamlit as st
from analysis import calculate_mmi, PortfolioManager, MacroMapper
from data_fetcher import get_market_context
import pandas as pd

st.set_page_config(page_title="AlphaQuant India Dashboard", layout="wide")

st.title("🇮🇳 AlphaQuant: Indian Equity Dashboard")

# 1. Market Mood Section
vix, nifty, fii = get_market_context()
mmi = calculate_mmi(vix, nifty, 500) # Mock FII flow
st.metric("Market Mood Index (MMI)", f"{mmi:.2f}%", delta="Greed" if mmi > 50 else "Fear")

# 2. Global-to-India Macro
# with st.expander("Global Macro Analysis"):
   # st.info("LLM Scoring Headlines for Fed, Crude, and USD-INR...")
    # Mock LLM Output
   # st.write("Current Sentiment Score: **+0.4 (Bullish)**")


# --- 2. Global-to-India Macro ---
st.subheader("🌍 Macro Mapper")
mapper = MacroMapper()
sentiment = mapper.get_macro_sentiment()

if sentiment < -0.1:
    st.error(f"Global Sentiment: {sentiment} (Bearish for India)")
else:
    st.success(f"Global Sentiment: {sentiment} (Bullish/Neutral)")


# --- Sidebar Settings ---
st.sidebar.header("View Settings")
show_raw = st.sidebar.checkbox("Display Raw Technical Data (50DMA/RSI)")

# --- 3. Top 300 Swing Scanner ---
st.divider()
st.subheader("🚀 Top 300 Swing Scanner")

if st.button("Run Live Market Scan"):
    with st.spinner("Analyzing Market Data..."):
        from data_fetcher import get_nifty_500_tickers
        from analysis import run_swing_scanner
        
        tickers = get_nifty_500_tickers()
        macro_score = mapper.get_macro_sentiment()
        live_results = run_swing_scanner(tickers, macro_score)
        
        if not live_results.empty:
            # Conditional Column Filtering
            display_cols = ["Ticker", "Style", "Signal"]
            if show_raw:
                display_cols = ["Ticker", "Price", "50DMA", "RSI", "Style", "Signal"]
            
            st.table(live_results[display_cols])
        else:
            st.warning("No matches found. Market might be in a 'No-Trade' zone.")



# 4. Portfolio Intelligence
st.sidebar.header("Portfolio Upload")
uploaded_file = st.sidebar.file_uploader("Upload Ticker CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
  
