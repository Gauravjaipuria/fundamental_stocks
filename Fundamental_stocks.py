import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta
import plotly.express as px

# Example data pulling (Adapt as needed for your dashboard)
ticker = st.sidebar.text_input('Ticker', 'AAPL')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')
data = yf.download(ticker, start=start_date, end=end_date)

with st.expander('Technical Analysis Dashboard'):
    st.subheader('Technical Analysis Dashboard')
    df = data.copy()
    
    # Get all callable TA functions for selection
    ind_list = [f for f in dir(ta) if not f.startswith("_") and callable(getattr(ta, f))]
    
    technical_indicator = st.selectbox('Tech Indicator', options=ind_list)
    method = technical_indicator

    # Prepare arguments for most indicators
    ta_kwargs = {
        'close': data['Close'] if 'Close' in data else None,
        'open': data['Open'] if 'Open' in data else None,
        'high': data['High'] if 'High' in data else None,
        'low': data['Low'] if 'Low' in data else None,
        'volume': data['Volume'] if 'Volume' in data else None
    }
    ta_kwargs = {k: v for k, v in ta_kwargs.items() if v is not None}
    
    # Compute the selected indicator
    try:
        indicator_func = getattr(ta, method)
        indicator = indicator_func(**ta_kwargs)
        result_df = pd.DataFrame(indicator)
        result_df['Close'] = data['Close']
        fig_ind_new = px.line(result_df)
        st.plotly_chart(fig_ind_new)
        st.write(result_df)
    except Exception as e:
        st.error(f"Failed to compute indicator. Reason: {e}")
