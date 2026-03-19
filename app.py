import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go

# 1. Cấu hình giao diện rộng (Wide mode)
st.set_page_config(layout="wide", page_title="BTC AI PRO DASHBOARD")
st.title("🚀 BTC AI PRO - BẢNG ĐIỀU KHIỂN THÔNG MINH")

# 2. Lấy dữ liệu từ sàn OKX (Cho ổn định trên Cloud)
@st.cache_data(ttl=60) # Cập nhật dữ liệu mỗi 60 giây
def get_data():
    exchange = ccxt.okx()
    bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

try:
    df = get_data()
    
    # 3. Tính toán RSI (Bộ não AI)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))

    # 4. CHIA CỘT GIAO DIỆN
    col1, col2 = st.columns([1, 3]) # Cột 1 nhỏ (Chỉ số), Cột 2 to (Biểu đồ)

    with col1:
        st.subheader("🤖 Chỉ số AI")
        last_price = df['close'].iloc[-1]
        rsi_val = df['RSI'].iloc[-1]
        
        st.metric("Giá BTC (USDT)", f"${last_price:,.2f}")
        st.metric("Chỉ số RSI", f"{rsi_val:.2f}")
        
        if rsi_val < 35:
            st.success("🚀 TÍN HIỆU: MUA")
        elif rsi_val > 65:
            st.error("⚠️ TÍN HIỆU: BÁN")
        else:
            st.info("⏳ TRẠNG THÁI: CHỜ")

    with col2:
        st.subheader("📈 Biểu đồ nến BTC (1H)")
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open'], high=df['high'],
            low=df['low'], close=df['close']
        )])
        fig.update_layout(xaxis_rangeslider_visible=False, height=500, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Đang kết nối sàn dữ liệu... Vui lòng đợi 30s. Lỗi: {e}")

st.write("---")
st.caption("✅ Hệ thống AI tự động cập nhật dữ liệu từ sàn OKX mỗi phút.")
