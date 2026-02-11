import streamlit as st
import requests
import ccxt
import pandas as pd
import numpy as np
import ta
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

BASE_URL = "https://api.binance.us"
exchange = ccxt.binanceus()

st.set_page_config(layout="wide")
st.title("📊 Binance.US Professional Momentum Scanner")

# SIDEBAR
st.sidebar.header("⚙️ Ayarlar")

min_volume = st.sidebar.number_input("Minimum 24h Hacim", value=1000000)
top_n = st.sidebar.slider("Kaç Coin Analiz Edilsin?", 5, 20, 10)

start = st.sidebar.button("Taramayı Başlat")

# OHLCV
def fetch_ohlcv(symbol, timeframe, limit=500):
    s = symbol.replace("USDT","/USDT")
    data = exchange.fetch_ohlcv(s, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp','open','high','low','close','volume'])
    return df

def trade_plan_15m(df):
    df['ema20'] = ta.trend.EMAIndicator(df['close'],20).ema_indicator()
    df['ema50'] = ta.trend.EMAIndicator(df['close'],50).ema_indicator()
    df['rsi'] = ta.momentum.RSIIndicator(df['close'],14).rsi()
    df['atr'] = ta.volatility.AverageTrueRange(df['high'],df['low'],df['close'],14).average_true_range()

    price = df['close'].iloc[-1]
    ema20 = df['ema20'].iloc[-1]
    ema50 = df['ema50'].iloc[-1]
    rsi = df['rsi'].iloc[-1]
    atr = df['atr'].iloc[-1]

    if ema20 > ema50 and rsi > 55:
        direction = "LONG"
        sl = price - 1.5*atr
        tp = price + 2*atr
    else:
        direction = "SHORT"
        sl = price + 1.5*atr
        tp = price - 2*atr

    return direction, price, sl, tp

if start:

    st.subheader("🔎 Tarama Sonuçları")

    resp = requests.get(BASE_URL + "/api/v3/ticker/24hr")
    data = resp.json()
    df = pd.DataFrame(data)

    df = df[df['symbol'].str.endswith("USDT")]
    df['quoteVolume'] = pd.to_numeric(df['quoteVolume'], errors='coerce')
    df['priceChangePercent'] = pd.to_numeric(df['priceChangePercent'], errors='coerce')
    df = df[df['quoteVolume'] > min_volume]

    df = df.sort_values("priceChangePercent", ascending=False).head(top_n)

    st.dataframe(df[['symbol','priceChangePercent','quoteVolume']])

    selected = st.selectbox("Grafik için Coin Seç", df['symbol'])

    df_daily = fetch_ohlcv(selected,'1d',limit=365)
    df_15m = fetch_ohlcv(selected,'15m',limit=500)

    direction, entry, sl, tp = trade_plan_15m(df_15m)

    st.markdown("### 📌 15M Trade Planı")
    st.write("Yön:", direction)
    st.write("Giriş:", round(entry,6))
    st.write("Stop:", round(sl,6))
    st.write("Take Profit:", round(tp,6))

    # Grafik
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(df_daily['close'])
    ax.axhline(entry, linestyle="--")
    ax.axhline(sl)
    ax.axhline(tp)

    st.pyplot(fig)
