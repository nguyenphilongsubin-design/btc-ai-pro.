import streamlit as st
import ccxt
import pandas as pd

# 1. Cấu hình giao diện
st.set_page_config(layout="wide", page_title="BTC AI PRO")
st.title("🚀 BTC AI PRO - BIỂU ĐỒ & CHỈ SỐ")

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

# 4. Hiển thị 2 cột
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("🤖 Chỉ số AI")
    last_price = df['close'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    st.metric("Giá BTC", f"${last_price:,.2f}")
    st.metric("RSI (1H)", f"{rsi:.2f}")
    if rsi < 35: st.success("🚀 MUA")
    elif rsi > 65: st.error("⚠️ BÁN")
    else: st.warning("⏳ CHỜ")

with col2:
    st.subheader("📈 Biểu đồ biến động giá")
    # Dùng biểu đồ mặc định của Streamlit để tránh lỗi Altair
    st.line_chart(df.set_index('timestamp')['close'])

st.write("✅ Dữ liệu cập nhật từ sàn OKX")
