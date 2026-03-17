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

# --- 3. Top 300 / Full Market Scanner ---
st.divider()
st.subheader("🚀 Advanced Sector Scanner")

# Pre-defined sectors for the "Vibe" (You can expand this list)
sector_options = ["All", "Banking", "IT", "Energy", "Automobile", "Pharma", "FMCG"]
selected_sector = st.selectbox("Choose Sector to Scan", sector_options)

if st.button("Run Sector-Specific Scan"):
    with st.spinner(f"Scanning {selected_sector} stocks..."):
        from data_fetcher import get_nifty_500_tickers
        
        # For simplicity, we filter the Nifty 500 list by common sector keywords
        all_tickers = get_nifty_500_tickers()
        
        # Placeholder for sector filtering logic
        # In a real setup, you'd match the ticker against the NSE Master List
        
        macro_score = mapper.get_macro_sentiment()
        scanner_results = run_sector_scanner(all_tickers, macro_score)
        
        if not scanner_results.empty:
            st.table(scanner_results)
        else:
            st.warning(f"No {selected_sector} stocks currently meet the criteria.")


# 4. Portfolio Intelligence
st.sidebar.header("Portfolio Upload")
uploaded_file = st.sidebar.file_uploader("Upload Ticker CSV", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.dataframe(df)
  
