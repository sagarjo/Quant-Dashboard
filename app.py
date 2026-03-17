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


# --- 3. Top 300 Swing Scanner (Live) ---
st.divider()
st.subheader("🚀 Top 300 Swing Scanner")

if st.button("Run Live Market Scan"):
    with st.spinner("Fetching Nifty 500 and analyzing top 300 stocks..."):
        from data_fetcher import get_nifty_500_tickers
        from analysis import run_swing_scanner
        
        # 1. Get Tickers
        all_tickers = get_nifty_500_tickers()
        
        # 2. Get Macro Sentiment
        mapper = MacroMapper()
        macro_score = mapper.get_macro_sentiment()
        
        # 3. Run Scanner
        scanner_results = run_swing_scanner(all_tickers, macro_score)
        
        if not scanner_results.empty:
            st.success(f"Scan complete based on {('Bullish' if macro_score > 0 else 'Bearish')} Macro.")
            st.table(scanner_results)
        else:
            st.warning("No stocks currently match the swing criteria.")
           


# 4. Portfolio Intelligence
st.sidebar.header("Portfolio Upload")
uploaded_file = st.sidebar.file_uploader("Upload Ticker CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
  
