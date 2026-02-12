import streamlit as st
import ccxt
import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go
from datetime import datetime

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Gemini Futures Analyzer", layout="wide")
st.title("📊 Crypto Futures Technical Analyzer")
st.sidebar.header("Ayarlar")

# --- PARAMETRELER (Side Bar) ---
symbol = st.sidebar.selectbox("Parite Seçin", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT"], index=0)
timeframe = st.sidebar.selectbox("Zaman Dilimi", ["1m", "5m", "15m", "1h", "4h", "1d"], index=3)
period = st.sidebar.slider("Mum Sayısı", 50, 500, 100)

# --- BINANCE BAĞLANTISI ---
@st.cache_data(ttl=30)  # 30 saniyede bir veriyi yeniler
def fetch_data(symbol, timeframe, limit):
    try:
        exchange = ccxt.binance({'options': {'defaultType': 'future'}})
        bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Veri çekme hatası: {e}")
        return None

# --- ANALİZ MODÜLÜ ---
def add_indicators(df):
    # RSI
    df['RSI'] = ta.rsi(df['close'], length=14)
    # Bollinger Bands
    bbands = ta.bbands(df['close'], length=20, std=2)
    df['BBL'] = bbands['BBL_20_2.0']
    df['BBM'] = bbands['BBM_20_2.0']
    df['BBU'] = bbands['BBU_20_2.0']
    # EMA
    df['EMA_20'] = ta.ema(df['close'], length=20)
    df['EMA_50'] = ta.ema(df['close'], length=50)
    return df

# --- ANA DÖNGÜ ---
df = fetch_data(symbol, timeframe, period)

if df is not None:
    df = add_indicators(df)
    last_row = df.iloc[-1]

    # --- METRİKLER (Üst Panel) ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Son Fiyat", f"${last_row['close']:.2f}")
    col2.metric("RSI (14)", f"{last_row['RSI']:.2f}")
    col3.metric("Üst Bant", f"${last_row['BBU']:.2f}")
    col4.metric("Alt Bant", f"${last_row['BBL']:.2f}")

    # --- GRAFİK TASARIMI (Plotly) ---
    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df['timestamp'], open=df['open'], high=df['high'],
        low=df['low'], close=df['close'], name='Fiyat'
    ))

    # Bollinger Bantları (Görselleştirme)
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BBU'], line=dict(color='rgba(173, 216, 230, 0.5)'), name='Üst Bant'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['BBL'], line=dict(color='rgba(173, 216, 230, 0.5)'), fill='tonexty', name='Alt Bant'))
    
    # EMA
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['EMA_20'], line=dict(color='orange', width=1), name='EMA 20'))

    fig.update_layout(title=f"{symbol} Teknik Görünüm", xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)

    # --- SİNYAL DURUMU ---
    st.subheader("🤖 Strateji Durum Raporu")
    
    # Analiz Mantığı
    status = "Nötr"
    color = "white"
    
    if last_row['RSI'] < 30 and last_row['close'] <= last_row['BBL']:
        status = "GÜÇLÜ AL (Aşırı Satım + Bollinger Alt Bant)"
        color = "green"
    elif last_row['RSI'] > 70 and last_row['close'] >= last_row['BBU']:
        status = "GÜÇLÜ SAT (Aşırı Alım + Bollinger Üst Bant)"
        color = "red"
    elif last_row['close'] > last_row['EMA_20']:
        status = "Yükseliş Trendi (EMA Üstü)"
        color = "blue"
    else:
        status = "Beklemede - Net Sinyal Yok"

    st.markdown(f"### Durum: :{color}[{status}]")

    # Veri Tablosu
    with st.expander("Ham Verileri Gör"):
        st.dataframe(df.tail(20))

else:
    st.warning("Veri yüklenemiyor, lütfen ayarları kontrol edin.")
