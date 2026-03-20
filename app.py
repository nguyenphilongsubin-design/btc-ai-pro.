import streamlit as st
import pandas as pd
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("🚀 BTC AI PRO - ULTRA STABLE BOT")

st_autorefresh(interval=5000, key="refresh")

# ===== STATE =====
if "position" not in st.session_state:
    st.session_state.position = None

if "history" not in st.session_state:
    st.session_state.history = []

# ===== LOAD DATA =====
@st.cache_data(ttl=60)
def get_data():
    try:
        df5 = yf.download("BTC-USD", interval="5m", period="2d")
        df15 = yf.download("BTC-USD", interval="15m", period="3d")
        df1h = yf.download("BTC-USD", interval="1h", period="7d")
        return df5, df15, df1h
    except:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

df5, df15, df1h = get_data()

def valid(df):
    return df is not None and not df.empty and len(df) > 50

if not (valid(df5) and valid(df15) and valid(df1h)):
    st.warning("⚠️ Đang load dữ liệu... chờ 5-10s")
    st.stop()

price = float(df5['Close'].iloc[-1])

# ===== EMA =====
def add_ema(df):
    df['ema50'] = df['Close'].ewm(span=50).mean()
    df['ema200'] = df['Close'].ewm(span=200).mean()
    return df

df5 = add_ema(df5)
df15 = add_ema(df15)
df1h = add_ema(df1h)

# ===== TREND =====
def trend(df):
    try:
        ema50 = float(df['ema50'].iloc[-1])
        ema200 = float(df['ema200'].iloc[-1])
        return "UP" if ema50 > ema200 else "DOWN"
    except:
        return "WAIT"

trend5 = trend(df5)
trend15 = trend(df15)
trend1h = trend(df1h)

# ===== RSI (FIX CỨNG 100%) =====
def rsi(df):
    try:
        close = df['Close'].astype(float)

        if len(close) < 20:
            return 50.0

        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = -delta.clip(upper=0).rolling(14).mean()

        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))

        val = rsi_series.iloc[-1]

        val = float(val)

        if val != val:  # NaN check
            return 50.0

        return val
    except:
        return 50.0

rsi5 = rsi(df5)

# ===== SMART MONEY =====
def fake_breakout(df):
    try:
        if len(df) < 20:
            return "WAIT"

        high = df['High'].astype(float)
        low = df['Low'].astype(float)
        close = df['Close'].astype(float)

        rh = float(high.iloc[-10:-1].max())
        rl = float(low.iloc[-10:-1].min())
        c = float(close.iloc[-1])
        p = float(close.iloc[-2])

        if c > rh and p < rh:
            return "FAKE_UP"
        elif c < rl and p > rl:
            return "FAKE_DOWN"
        return "NORMAL"
    except:
        return "WAIT"

fake = fake_breakout(df5)

# ===== VOLUME =====
def volume_spike(df):
    try:
        vol = df['Volume'].astype(float)
        if len(vol) < 20:
            return "LOW"
        return "HIGH" if float(vol.iloc[-1]) > float(vol.iloc[-20:].mean()) * 2 else "LOW"
    except:
        return "LOW"

volume = volume_spike(df5)

# ===== SCORE =====
score = 0

if trend5 == trend15 == trend1h and trend5 != "WAIT":
    score += 40

if rsi5 < 35 or rsi5 > 65:
    score += 15

if volume == "HIGH":
    score += 15

if fake == "NORMAL":
    score += 15
elif fake != "WAIT":
    score -= 10

# ===== SIGNAL =====
signal = "NO TRADE"
tp = 0
sl = 0

if score >= 70:
    if trend5 == "UP":
        signal = "BUY"
        tp = price * 1.01
        sl = price * 0.995
    elif trend5 == "DOWN":
        signal = "SELL"
        tp = price * 0.99
        sl = price * 1.005

# ===== OPEN POSITION =====
if signal != "NO TRADE" and st.session_state.position is None:
    st.session_state.position = {
        "type": signal,
        "entry": price,
        "tp": tp,
        "sl": sl,
        "trend": f"{trend5}/{trend15}/{trend1h}",
        "score": score
    }

position = st.session_state.position

# ===== UI =====
col1, col2 = st.columns([3,1])

with col1:
    st.subheader("📊 BTC Chart")
    st.line_chart(df5['Close'])

with col2:
    st.subheader("🤖 AI PANEL")

    st.metric("💰 Price", f"{price:.2f}")
    st.metric("📈 Trend 5m", trend5)
    st.metric("📊 Trend 15m", trend15)
    st.metric("📊 Trend 1H", trend1h)
    st.metric("🧠 RSI", f"{rsi5:.2f}")
    st.metric("🐋 Volume", volume)
    st.metric("🪤 Fake", fake)

    st.write("---")
    st.metric("🧠 Score", score)
    st.metric("⚡ Signal", signal)

    if position:
        pnl = price - position["entry"] if position["type"]=="BUY" else position["entry"]-price

        st.subheader("📌 OPEN POSITION")
        st.write(position)
        st.write(f"PnL: {pnl:.2f}")

        # AUTO CLOSE
        if (position["type"]=="BUY" and (price>=position["tp"] or price<=position["sl"])) or \
           (position["type"]=="SELL" and (price<=position["tp"] or price>=position["sl"])):

            result = "WIN" if pnl > 0 else "LOSS"

            st.session_state.history.append({
                "type": position["type"],
                "entry": position["entry"],
                "exit": price,
                "pnl": pnl,
                "result": result,
                "score": position["score"]
            })

            st.session_state.position = None

# ===== STATS =====
history = pd.DataFrame(st.session_state.history)

st.write("----")

if not history.empty:
    winrate = (history["result"]=="WIN").mean()*100
    total_pnl = history["pnl"].sum()

    st.subheader("📊 PERFORMANCE")
    st.write(f"Winrate: {winrate:.2f}%")
    st.write(f"Total PnL: {total_pnl:.2f}")
    st.dataframe(history)