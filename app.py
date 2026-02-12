import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# -----------------------------------------------------------------------------
# 1. SAYFA VE GENEL AYARLAR
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Binance Futures Grafiği",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📈 Binance Futures - Fiyat Takip Sistemi")
st.markdown("---")

# -----------------------------------------------------------------------------
# 2. YAN PANEL (SIDEBAR) - KULLANICI GİRİŞLERİ
# -----------------------------------------------------------------------------
st.sidebar.header("⚙️ Grafik Ayarları")

# Coin Seçimi (Listeyi senin isteğine göre sabitledim)
coin_list = ["BTC", "ETH", "SOL", "ADA", "XRP", "BNB"]
selected_coin = st.sidebar.selectbox("Coin Seçiniz:", coin_list, index=0)

# Zaman Dilimi Seçimi (Kullanıcı dostu isimler -> API kodları)
timeframe_map = {
    "5 Dakika": "5m",
    "15 Dakika": "15m",
    "1 Saat": "1h",
    "4 Saat": "4h",
    "1 Gün": "1d"
}
selected_tf_label = st.sidebar.selectbox("Zaman Dilimi:", list(timeframe_map.keys()), index=2)
selected_tf_code = timeframe_map[selected_tf_label]

# Mum Sayısı (Varsayılan 100, istersen artırabilirsin)
limit = st.sidebar.slider("Gösterilecek Mum Sayısı:", 50, 500, 100)

# Çizim Butonu
draw_button = st.sidebar.button("Grafiği Çiz", type="primary")

# -----------------------------------------------------------------------------
# 3. VERİ ÇEKME FONKSİYONU (Binance Futures)
# -----------------------------------------------------------------------------
def fetch_futures_data(symbol, timeframe, limit):
    """
    Binance Vadeli İşlemlerden (Futures) veri çeker.
    API Key gerektirmez (Public Data).
    """
    try:
        # Binance Futures bağlantısı
        exchange = ccxt.binance({
            'options': {
                'defaultType': 'future',  # Spot değil Vadeli veri
            }
        })
        
        # Sembolü API formatına çevir (Örn: BTC -> BTC/USDT)
        pair = f"{symbol}/USDT"
        
        # Veriyi çek
        ohlcv = exchange.fetch_ohlcv(pair, timeframe, limit=limit)
        
        # Veriyi DataFrame'e çevir
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df, pair
    except Exception as e:
        return None, str(e)

# -----------------------------------------------------------------------------
# 4. ANA İŞLEYİŞ (BUTONA BASILINCA)
# -----------------------------------------------------------------------------
if draw_button:
    with st.spinner(f'{selected_coin} verileri çekiliyor...'):
        # Veriyi getir
        df, result = fetch_futures_data(selected_coin, selected_tf_code, limit)
        
        if df is not None:
            # --- BAŞARILI İSE GRAFİĞİ ÇİZ ---
            
            # Son fiyat bilgisi
            last_price = df['close'].iloc[-1]
            st.metric(label=f"{result} Son Fiyat", value=f"${last_price:.2f}")
            
            # Plotly ile Mum Grafiği (Candlestick)
            fig = go.Figure(data=[go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name=result
            )])
            
            # Grafik Görsel Ayarları
            fig.update_layout(
                title=f'{result} - {selected_tf_label} Grafiği',
                yaxis_title='Fiyat (USDT)',
                xaxis_title='Zaman',
                template='plotly_dark', # Koyu tema
                height=600,
                xaxis_rangeslider_visible=False # Alt kısımdaki kaydırma çubuğunu gizle
            )
            
            # Ekrana bas
            st.plotly_chart(fig, use_container_width=True)
            
            # İsteğe bağlı: Tablo olarak veriyi göster
            with st.expander("Ham Verileri Görüntüle"):
                st.dataframe(df.sort_values(by='timestamp', ascending=False))
                
        else:
            # --- HATA VARSA ---
            st.error(f"Veri çekilemedi! Hata Detayı: {result}")

else:
    # Henüz butona basılmadıysa başlangıç ekranı
    st.info("👈 Lütfen sol panelden Coin ve Süre seçip 'Grafiği Çiz' butonuna basın.")
