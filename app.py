import streamlit as st

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Binance Futures Scalp Engine",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚀 Binance Futures Scalp & Swing Engine")

# =====================================
# SESSION STATE INIT
# =====================================

if "selected_coins" not in st.session_state:
    st.session_state.selected_coins = []

# =====================================
# SIDEBAR – TRADING CONFIGURATION
# =====================================

st.sidebar.header("📊 Trade Configuration")

scalp_mode = st.sidebar.radio(
    "Scalp Mode",
    [
        "5 Minutes (High Frequency)",
        "15 Minutes (Balanced)",
        "1 Hour (Micro Swing)"
    ]
)

if "5" in scalp_mode:
    timeframe = "5m"
elif "15" in scalp_mode:
    timeframe = "15m"
else:
    timeframe = "1h"

# =====================================
# INVESTMENT SETUP
# =====================================

st.sidebar.header("💰 Investment Setup")

colA, colB = st.sidebar.columns(2)

with colA:
    investment_amount = st.number_input(
        "Investment Amount",
        min_value=10.0,
        value=500.0,
        step=10.0
    )

with colB:
    stablecoin_type = st.selectbox(
        "Base",
        ["USDT", "USDC"]
    )

# =====================================
# RISK PROFILE
# =====================================

st.sidebar.header("⚠ Risk Profile")

risk_level = st.sidebar.select_slider(
    "Risk Level",
    options=["Low", "Medium", "High"],
    value="Medium"
)

if risk_level == "Low":
    risk_percent = 0.5
    leverage_default = 3
elif risk_level == "Medium":
    risk_percent = 1.0
    leverage_default = 5
else:
    risk_percent = 2.0
    leverage_default = 8

leverage = st.sidebar.slider(
    "Leverage",
    min_value=1,
    max_value=20,
    value=leverage_default
)

auto_leverage = st.sidebar.checkbox("Auto Leverage (ATR Based)")

# =====================================
# SCAN SETTINGS
# =====================================

st.sidebar.header("🔎 Scan Settings")

coin_count = st.sidebar.slider(
    "Number of Coins to Select",
    min_value=1,
    max_value=50,
    value=20
)

min_volume = st.sidebar.number_input(
    f"Minimum 24h Volume ({stablecoin_type})",
    min_value=10000.0,
    value=500000.0,
    step=50000.0
)

volume_spike_multiplier = st.sidebar.slider(
    "Volume Spike Multiplier",
    min_value=1.0,
    max_value=3.0,
    value=1.8
)

direction_mode = st.sidebar.multiselect(
    "Allowed Directions",
    ["Long", "Short"],
    default=["Long", "Short"]
)

# =====================================
# MAIN DASHBOARD
# =====================================

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 Scan Results")

    if st.session_state.selected_coins:
        st.dataframe(st.session_state.selected_coins)
    else:
        st.info(f"Scanning {timeframe} timeframe futures markets...")

with col2:
    st.subheader("📌 Trade Setup Preview")

    st.metric("Investment", f"{investment_amount} {stablecoin_type}")
    st.metric("Risk %", f"{risk_percent}%")
    st.metric("Leverage", f"{leverage}x")
    st.metric("Timeframe", timeframe)

# =====================================
# ACTION BUTTONS
# =====================================

st.divider()

colA, colB, colC = st.columns(3)

with colA:
    scan_button = st.button("🔎 Run Scan")

with colB:
    paper_trade_button = st.button("📝 Paper Trade")

with colC:
    live_trade_button = st.button("⚡ Execute Live Trade")

# =====================================
# SCAN LOGIC (MOCK FOR NOW)
# =====================================

if scan_button:

    st.info("Scanning Binance Futures markets...")

    # Geçici mock liste (gerçek API entegrasyonu sonraki aşama)
    mock_market = [
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT",
        "AVAXUSDT", "DOGEUSDT", "BNBUSDT", "ADAUSDT",
        "LINKUSDT", "LTCUSDT", "APTUSDT", "ARBUSDT",
        "OPUSDT", "MATICUSDT", "INJUSDT", "NEARUSDT",
        "FILUSDT", "ATOMUSDT", "SUIUSDT", "TIAUSDT",
        "TRXUSDT", "ETCUSDT", "AAVEUSDT", "UNIUSDT",
        "ICPUSDT", "HBARUSDT", "FTMUSDT", "EGLDUSDT"
    ]

    selected = mock_market[:coin_count]

    st.session_state.selected_coins = selected

    st.success(f"{len(selected)} coins selected.")

# =====================================
# STATUS PANEL
# =====================================

st.divider()

st.subheader("📡 System Status")

if st.session_state.selected_coins:
    st.success("Scan completed successfully.")
else:
    st.success("System Ready")
