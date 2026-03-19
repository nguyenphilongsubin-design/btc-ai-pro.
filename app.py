import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
import requests

# 1. Cấu hình giao diện Terminal
st.set_page_config(layout="wide", page_title="BTC AI PRO - SENTIMENT & TREND")
st.title("🚀 BTC AI PRO - TÂM LÝ & XU HƯỚNG ĐA KHUNG GIỜ")

# --- HÀM LẤY CHỈ SỐ TÂM LÝ (FEAR & GREED) ---
def get_fear_greed():
    try:
        r = requests.get('https://alternative.me').json()
        val = int(r['data'][0]['value'])
        text = r['data'][0]['value_classification']
        return val, text
    except:
        return 50, "Neutral"

# --- HÀM LẤY XU HƯỚNG ---
exchange = ccxt.okx()
symbol = 'BTC/USDT'
timeframes = ['1d', '12h', '4h', '2h', '1h']

def get_trend_analysis(tf):
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        current_price = df['close'].iloc[-1]
        delta = df['close'].diff()
        rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean()))).iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        if current_price > ma20 and rsi > 52: trend = "🔥 TĂNG"
        elif current_price < ma20 and rsi < 48: trend = "❄️ GIẢM"
        else: trend = "⏳ SIDEWAY"
        return {"Price": current_price, "RSI": rsi, "Trend": trend}
    except: return None

# --- GIAO DIỆN 1: TÂM LÝ THỊ TRƯỜNG ---
fng_val, fng_text = get_fear_greed()
st.subheader(f"🧠 Tâm lý thị trường: {fng_text} ({fng_val}/100)")
st.progress(fng_val/100)
if fng_val > 70: st.warning("⚠️ Đám đông đang quá THAM LAM. Cẩn thận điều chỉnh!")
elif fng_val < 30: st.success("🚀 Đám đông đang SỢ HÃI. Cơ hội gom hàng giá tốt!")

st.write("---")

# --- GIAO DIỆN 2: BẢNG XU HƯỚNG ĐA KHUNG GIỜ ---
st.subheader("📊 Xu hướng đa khung thời gian (Trend Analysis)")
cols = st.columns(len(timeframes))
for i, tf in enumerate(timeframes):
    data = get_trend_analysis(tf)
    with cols[i]:
        if data:
            st.info(f"**Khung {tf.upper()}**")
            st.metric("Giá", f"${data['Price']:,.1f}")
            if "TĂNG" in data['Trend']: st.success(data['Trend'])
            elif "GIẢM" in data['Trend']: st.error(data['Trend'])
            else: st.warning(data['Trend'])

st.write("---")

# --- GIAO DIỆN 3: TƯ VẤN ENTRY/TP/SL (KHUNG 1H) ---
col_entry, col_chart = st.columns([1, 2])
df_1h = pd.DataFrame(exchange.fetch_ohlcv(symbol, '1h', limit=100), columns=['time', 'open', 'high', 'low', 'close', 'volume'])
last = df_1h.iloc[-1]
atr = (df_1h['high'] - df_1h['low']).rolling(14).mean().iloc[-1]

with col_entry:
    st.subheader("🤖 AI Advisor")
    price = last['close']
    # AI tính toán điểm vào dựa trên độ biến động thực tế
    tp_buy = price + (atr * 2.5)
    sl_buy = price - (atr * 1.5)
    tp_sell = price - (atr * 2.5)
    sl_sell = price + (atr * 1.5)
    
    st.write(f"**Giá hiện tại:** `{price:,.1f}`")
    st.markdown(f"""
    🟢 **MUA (LONG) NẾU:** Giá giữ vững {price:,.1f}
    - Chốt lời (TP): `{tp_buy:,.1f}`
    - Cắt lỗ (SL): `{sl_buy:,.1f}`
    
    🔴 **BÁN (SHORT) NẾU:** Giá thủng {price:,.1f}
    - Chốt lời (TP): `{tp_sell:,.1f}`
    - Cắt lỗ (SL): `{sl_sell:,.1f}`
    """)

with col_chart:
    df_1h['time'] = pd.to_datetime(df_1h['time'], unit='ms')
    fig = go.Figure(data=[go.Candlestick(x=df_1h['time'], open=df_1h['open'], high=df_1h['high'], low=df_1h['low'], close=df_1h['close'])])
    fig.update_layout(xaxis_rangeslider_visible=False, height=450, margin=dict(l=0, r=0, t=0, b=0), template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)
