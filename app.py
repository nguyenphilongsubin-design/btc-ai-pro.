import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go

# 1. Cấu hình giao diện rộng
st.set_page_config(layout="wide", page_title="BTC AI PRO DASHBOARD")
st.title("🚀 BTC AI PRO - BẢNG ĐIỀU KHIỂN & BIỂU ĐỒ")

# 2. Lấy dữ liệu (Dùng OKX để không bị chặn)
exchange = ccxt.okx()
bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# 3. Tính toán RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
df['RSI'] = 100 - (100 / (1 + (gain/loss)))

# 4. CHIA CỘT GIAO DIỆN
col1, col2 = st.columns([1, 3]) # Cột 1 nhỏ (chỉ số), Cột 2 to (biểu đồ)

with col1:
    st.subheader("🤖 Chỉ số AI")
    gia_hien_tai = df['close'].iloc[-1]
    rsi_hien_tai = df['RSI'].iloc[-1]
    
    st.metric("Giá BTC (USDT)", f"${gia_hien_tai:,.2f}")
    st.metric("Chỉ số RSI", f"{rsi_hien_tai:.2f}")
    
    if rsi_hien_tai < 35:
        st.success("🚀 TÍN HIỆU: MUA")
    elif rsi_hien_tai > 65:
        st.error("⚠️ TÍN HIỆU: BÁN")
    else:
        st.warning("⏳ AI: CHỜ ĐỢI")

with col2:
    st.subheader("📈 Biểu đồ nến BTC (1H)")
    fig = go.Figure(data=[go.Candlestick(
        x=df['timestamp'],
        open=df['open'], high=df['high'],
        low=df['low'], close=df['close']
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=600)
    st.plotly_chart(fig, use_container_width=True)
