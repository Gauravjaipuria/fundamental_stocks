import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

# Example: Download data for a demonstration
ticker = st.sidebar.text_input('Ticker', 'AAPL')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')
data = yf.download(ticker, start=start_date, end=end_date)

with st.expander('Technical Analysis Dashboard'):
    st.subheader('Technical Analysis Dashboard')
    df = data.copy()
    ind_list = ta.indicators()
    
    technical_indicator = st.selectbox('Tech Indicator', options=ind_list)
    method = technical_indicator
    
    # Prepare arguments required for most technical indicators
    ta_kwargs = {
        'close': data['Close'] if 'Close' in data else None,
        'open': data['Open'] if 'Open' in data else None,
        'high': data['High'] if 'High' in data else None,
        'low': data['Low'] if 'Low' in data else None,
        'volume': data['Volume'] if 'Volume' in data else None
    }
    # Remove None arguments
    ta_kwargs = {k: v for k, v in ta_kwargs.items() if v is not None}
    
    # Compute the selected indicator (handle errors for missing or wrong arguments)
    try:
        indicator_func = getattr(ta, method)
        indicator_val = indicator_func(**ta_kwargs)
        st.write(indicator_val)
    except Exception as e:
        st.error(f"Failed to compute indicator. Reason: {e}")
