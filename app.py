# app.py
import streamlit as st
import pandas as pd
import time
import plotly.graph_objs as go
from datetime import datetime
import random

# --- PAGE CONFIG ---
st.set_page_config(page_title="BTC AI PRO", layout="wide", page_icon=":moneybag:")

# --- CSS THEME ---
st.markdown("""
<style>
body {background-color: #0b0e11; color: #ffffff;}
.stButton>button {height: 60px; width: 120px; font-size: 20px; font-weight: bold;}
.stDataFrame {color: #ffffff; background-color: #1f2937;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "logs" not in st.session_state:
    st.session_state.logs = []

if "alerts" not in st.session_state:
    st.session_state.alerts = []

# --- SIDEBAR ---
st.sidebar.title("BTC AI PRO Settings")
pair = st.sidebar.selectbox("Select Pair", ["BTC/USDT", "ETH/USDT", "BNB/USDT"])
timeframe = st.sidebar.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h"])
ai_level = st.sidebar.selectbox("AI Level", ["Level 1", "Level 2", "Level 3"])
st.sidebar.markdown("---")
start_bot = st.sidebar.button("START BOT")
stop_bot = st.sidebar.button("STOP BOT")

# --- ALERT FUNCTION ---
def show_alert(message):
    alert_placeholder = st.empty()
    alert_placeholder.warning(message)
    time.sleep(5)
    alert_placeholder.empty()

# --- SIMULATE PRICE DATA ---
def get_fake_price():
    return round(50000 + random.uniform(-1000, 1000), 2)

price_history = [get_fake_price() for _ in range(50)]

# --- BUY / SELL ACTION ---
col1, col2 = st.columns(2)
with col1:
    if st.button("BUY"):
        entry_price = price_history[-1]
        tp = round(entry_price * 1.01, 2)
        sl = round(entry_price * 0.99, 2)
        st.session_state.logs.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Action": "BUY",
            "Price": entry_price,
            "TP": tp,
            "SL": sl
        })
        show_alert(f"AI BUY at {entry_price} → TP {tp} / SL {sl}")
with col2:
    if st.button("SELL"):
        entry_price = price_history[-1]
        tp = round(entry_price * 0.99, 2)
        sl = round(entry_price * 1.01, 2)
        st.session_state.logs.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Action": "SELL",
            "Price": entry_price,
            "TP": tp,
            "SL": sl
        })
        show_alert(f"AI SELL at {entry_price} → TP {tp} / SL {sl}")

# --- SIMULATE AI ENTRY ---
if start_bot:
    action = random.choice(["BUY", "SELL"])
    entry_price = price_history[-1]
    if action == "BUY":
        tp = round(entry_price * 1.01, 2)
        sl = round(entry_price * 0.99, 2)
    else:
        tp = round(entry_price * 0.99, 2)
        sl = round(entry_price * 1.01, 2)
    st.session_state.logs.append({
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Action": f"AI {action}",
        "Price": entry_price,
        "TP": tp,
        "SL": sl
    })
    show_alert(f"AI {action} at {entry_price} → TP {tp} / SL {sl}")

# --- DISPLAY PRICE CHART ---
fig = go.Figure()
fig.add_trace(go.Scatter(y=price_history, mode='lines+markers', name='Price', line=dict(color='cyan')))
fig.update_layout(
    plot_bgcolor="#0b0e11",
    paper_bgcolor="#0b0e11",
    font=dict(color="white"),
    title=f"{pair} Price Chart ({timeframe})",
    xaxis_title="Time",
    yaxis_title="Price"
)
st.plotly_chart(fig, use_container_width=True)

# --- DISPLAY LOG TABLE ---
st.subheader("Trade Log")
if st.session_state.logs:
    df_logs = pd.DataFrame(st.session_state.logs)
    st.dataframe(df_logs)
else:
    st.write("No trades yet.")