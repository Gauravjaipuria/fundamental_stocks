import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

st.title('Stock Dashboard')
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker, start=start_date, end=end_date)

fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
st.plotly_chart(fig)

pricing_data, fundamental_data, news, openai1 = st.tabs([
    "Pricing Data", "Fundamental Data", "Top 10 News", "OpenAI ChatGPT"
])

with pricing_data:
    st.header('Price Movements')
    data2 = data.copy()
    data2['% Change'] = data['Adj Close'] / data['Adj Close'].shift(1) - 1
    data2.dropna(inplace=True)
    st.write(data2)
    annual_return = data2['% Change'].mean() * 252 * 100
    st.write('Annual Return is ', annual_return, '%')
    stdev = np.std(data2['% Change']) * np.sqrt(252)
    st.write('Standard Deviation is ', stdev * 100, '%')
    st.write('Risk Adj. Return is ', annual_return / (stdev * 100))

# Add your logic for fundamental_data, news, and openai1 tabs here
from alpha_vantage.fundamentaldata import FundamentalData
import streamlit as st

key = 'OW1639L63B5UCYYL'
fd = FundamentalData(key, output_format = 'pandas')

with fundamental_data:
    st.subheader('Balance Sheet')
    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)

    st.subheader('Income Statement')
    income_statement = fd.get_income_statement_annual(ticker)[0]
    is1 = income_statement.T[2:]
    is1.columns = list(income_statement.T.iloc[0])
    st.write(is1)

    st.subheader('Cash Flow Statement')
    cash_flow = fd.get_cash_flow_annual(ticker)[0]
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)
from stocknews import StockNews

with news:
    st.header(f'News of {ticker}')
    sn = StockNews(ticker, save_news=False)
    df_news = sn.read_rss()
    for i in range(10):
        st.subheader(f'News {i+1}')
        st.write(df_news['published'][i])
        st.write(df_news['title'][i])
        st.write(df_news['summary'][i])
        title_sentiment = df_news['sentiment_title'][i]
        st.write(f'Title Sentiment {title_sentiment}')
        news_sentiment = df_news['sentiment_summary'][i]
        st.write(f'News Sentiment {news_sentiment}')

from pyChatGPT import ChatGPT

session_token = 'your_session_token_here'
api2 = ChatGPT(session_token)
buy = api2.send_message(f'3 Reasons to buy {ticker} stock')
sell = api2.send_message(f'3 Reasons to sell {ticker} stock')
swot = api2.send_message(f'SWOT analysis of {ticker} stock')

with openai1:
    buy_reason, sell_reason, swot_analysis = st.tabs([
        '3 Reasons to buy', '3 Reasons to sell', 'SWOT analysis'
    ])
    with buy_reason:
        st.write(buy)
    with sell_reason:
        st.write(sell)
    with swot_analysis:
        st.write(swot)
