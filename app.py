import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. SAYFA VE GENEL AYARLAR
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Crypto Fiyat Takip",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Kripto Fiyat Takip Sistemi (Global)")
st.info("ℹ️ Not: Streamlit sunucuları ABD'de olduğu için Binance verisi engellenmektedir. Veriler kesintisiz erişim için Yahoo Finance üzerinden çekilmektedir.")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. YAN PANEL (SIDEBAR) - KULLANICI GİRİŞLERİ
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Grafik Ayarları")

# Coin Seçimi
coin_list = ["BTC", "ETH", "SOL", "ADA", "XRP", "BNB"]
selected_coin = st.sidebar.selectbox("Coin Seçiniz:", coin_list, index=0)

# Zaman Dilimi Seçimi (Yahoo Formatı)
timeframe_map = {
    "5 Dakika": "5m",
    "15 Dakika": "15m",
    "1 Saat": "1h",
    "1 Gün": "1d"
}
selected_tf_label = st.sidebar.selectbox("Zaman Dilimi:", list(timeframe_map.keys()), index=2)
selected_tf_code = timeframe_map[selected_tf_label]

# Mum Sayısı (Periyot belirleme)
# Yahoo finance için periyot mantığı biraz farklıdır (Son 1 gün, Son 5 gün vb.)
period_map = {
    "5m": "1d",   # 5 dk'lık veri için son 1 günü getir
    "15m": "5d",  # 15 dk'lık veri için son 5 günü getir
    "1h": "1mo",  # 1 saatlik veri için son 1 ayı getir
    "1d": "1y"    # Günlük veri için son 1 yılı getir
}
period = period_map[selected_tf_code]

# Çizim Butonu
draw_button = st.sidebar.button("Grafiği Çiz", type="primary")

# -----------------------------------------------------------------------------
# 3. VERİ ÇEKME FONKSİYONU (Yahoo Finance)
# -----------------------------------------------------------------------------
def fetch_crypto_data(symbol, interval, period):
    """
    Yahoo Finance üzerinden veri çeker (VPN/Proxy gerekmez).
    """
    try:
        # Sembolü Yahoo formatına çevir (Örn: BTC -> BTC-USD)
        pair = f"{symbol}-USD"
        
        # Veriyi çek
        ticker = yf.Ticker(pair)
        df = ticker.history(period=period, interval=interval)
        
        if df.empty:
            return None, "Veri boş döndü."
            
        # DataFrame düzenleme
        df = df.reset_index()
        
        # Sütun isimlerini standartlaştır (Date -> timestamp)
        # Yahoo bazen 'Date', bazen 'Datetime' döndürür
        if 'Datetime' in df.columns:
            df = df.rename(columns={'Datetime': 'timestamp', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
        elif 'Date' in df.columns:
            df = df.rename(columns={'Date': 'timestamp', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'})
            
        # Zaman damgasını timezone'dan arındır (Plotly hatasını önlemek için)
        df['timestamp'] = pd.to_datetime(df['timestamp']).dt.tz_localize(None)
        
        return df, pair
    except Exception as e:
        return None, str(e)

# -----------------------------------------------------------------------------
# 4. ANA İŞLEYİŞ
# -----------------------------------------------------------------------------
if draw_button:
    with st.spinner(f'{selected_coin} verileri çekiliyor...'):
        # Veriyi getir
        df, result = fetch_crypto_data(selected_coin, selected_tf_code, period)
        
        if df is not None:
            # --- BAŞARILI İSE GRAFİĞİ ÇİZ ---
            
            last_price = df['close'].iloc[-1]
            st.metric(label=f"{result} Son Fiyat", value=f"${last_price:.2f}")
            
            # Plotly Mum Grafiği
            fig = go.Figure(data=[go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=result
            )])
            
            fig.update_layout(
                title=f'{result} - {selected_tf_label} Grafiği',
                yaxis_title='Fiyat (USD)',
                xaxis_title='Zaman',
                template='plotly_dark',
                height=600,
                xaxis_rangeslider_visible=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("Ham Verileri Görüntüle"):
                st.dataframe(df.sort_values(by='timestamp', ascending=False))
                
        else:
            st.error(f"Veri çekilemedi! Hata: {result}")

else:
    st.info("👈 Lütfen sol panelden seçim yapıp 'Grafiği Çiz' butonuna basın.")
