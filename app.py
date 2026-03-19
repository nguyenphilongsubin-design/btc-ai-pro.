import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go

# 1. Cấu hình giao diện chuẩn Trading Terminal
st.set_page_config(layout="wide", page_title="BTC AI MULTI-TIME FRAME")
st.title("🚀 BTC AI PRO - PHÂN TÍCH ĐA KHUNG THỜI GIAN")

exchange = ccxt.okx()
symbol = 'BTC/USDT'
timeframes = ['1d', '12h', '4h', '2h', '1h'] # Các khung giờ anh yêu cầu

def get_trend_analysis(tf):
    """Hàm lấy dữ liệu và phân tích xu hướng cho từng khung giờ"""
    try:
        bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=50)
        df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
        
        # Tính RSI và MA20 để xác định xu hướng
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        current_price = df['close'].iloc[-1]
        
        # Xác định xu hướng
        if current_price > ma20 and rsi > 55: trend = "🔥 TĂNG (BULL)"
        elif current_price < ma20 and rsi < 45: trend = "❄️ GIẢM (BEAR)"
        else: trend = "⏳ ĐI NGANG (SIDEWAY)"
        
        return {"Price": current_price, "RSI": rsi, "Trend": trend}
    except:
        return None

# --- GIAO DIỆN CHÍNH ---
st.subheader("📊 BẢNG TỔNG HỢP XU HƯỚNG 24H - 1H")
cols = st.columns(len(timeframes))

for i, tf in enumerate(timeframes):
    data = get_trend_analysis(tf)
    with cols[i]:
        if data:
            st.info(f"**Khung {tf.upper()}**")
            st.metric("Giá", f"${data['Price']:,.1f}")
            st.write(f"RSI: **{data['RSI']:.1f}**")
            if "TĂNG" in data['Trend']: st.success(data['Trend'])
            elif "GIẢM" in data['Trend']: st.error(data['Trend'])
            else: st.warning(data['Trend'])

st.write("---")

# --- PHẦN TƯ VẤN THỰC CHIẾN (Dựa trên khung 1H) ---
st.subheader("🤖 CHIẾN THUẬT VÀO LỆNH (AI ADVISOR)")
df_1h = pd.DataFrame(exchange.fetch_ohlcv(symbol, '1h', limit=100), columns=['time', 'open', 'high', 'low', 'close', 'volume'])
last_1h = df_1h.iloc[-1]
atr = (df_1h['high'] - df_1h['low']).rolling(14).mean().iloc[-1]
rsi_1h = 100 - (100 / (1 + (df_1h['close'].diff().where(df_1h['close'].diff() > 0, 0).rolling(14).mean() / -df_1h['close'].diff().where(df_1h['close'].diff() < 0, 0).rolling(14).mean()))).iloc[-1]

col_entry, col_chart = st.columns([1, 2])

with col_entry:
    price = last_1h['close']
    if rsi_1h < 40:
        st.success(f"📍 **ENTRY MUA (LONG):** {price:,.1f}\n\n🎯 **TP:** {price+(atr*2):,.1f}\n\n🛡️ **SL:** {price-(atr*1.5):,.1f}")
    elif rsi_1h > 60:
        st.error(f"📍 **ENTRY BÁN (SHORT):** {price:,.1f}\n\n🎯 **TP:** {price-(atr*2):,.1f}\n\n🛡️ **SL:** {price+(atr*1.5):,.1f}")
    else:
        st.warning("⏳ AI khuyên anh nên đợi tín hiệu rõ ràng hơn ở khung 1H.")

with col_chart:
    df_1h['time'] = pd.to_datetime(df_1h['time'], unit='ms')
    fig = go.Figure(data=[go.Candlestick(x=df_1h['time'], open=df_1h['open'], high=df_1h['high'], low=df_1h['low'], close=df_1h['close'])])
    fig.update_layout(xaxis_rangeslider_visible=False, height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)
