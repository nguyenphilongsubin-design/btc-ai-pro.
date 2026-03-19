import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
import time
from datetime import datetime

# 1. Cấu hình giao diện và Bộ nhớ tạm (Session State)
st.set_page_config(layout="wide", page_title="BTC AI LEARNING PRO")
if 'trades' not in st.session_state:
    st.session_state.trades = [] # Lưu lịch sử lệnh
if 'current_order' not in st.session_state:
    st.session_state.current_order = None # Lệnh đang chạy

st.title("🚀 BTC AI LEARNING PRO - HỆ THỐNG TRADE MẪU & TỰ HỌC")

# --- HÀM LẤY DỮ LIỆU ---
exchange = ccxt.okx()
symbol = 'BTC/USDT'

def get_data():
    bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time_dt'] = pd.to_datetime(df['time'], unit='ms')
    # Tính RSI và ATR (Độ biến động)
    delta = df['close'].diff()
    df['RSI'] = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))
    df['ATR'] = (df['high'] - df['low']).rolling(14).mean()
    return df

# --- LOGIC TRADE MẪU & THÔNG BÁO ---
df = get_data()
last = df.iloc[-1]
price = last['close']
rsi = last['RSI']
atr = last['ATR']

# Hiển thị thông báo nhấp nháy nếu có lệnh
if st.session_state.current_order:
    st.markdown("""
        <style>
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
        .blink { animation: blink 1s linear infinite; color: #FF4B4B; font-weight: bold; border: 2px solid #FF4B4B; padding: 10px; border-radius: 5px; text-align: center; }
        </style>
        <div class="blink">🔴 AI ĐANG TRONG LỆNH - ĐANG THEO DÕI BIẾN ĐỘNG...</div>
        """, unsafe_allow_stdio=True)

col_info, col_chart = st.columns([1, 2])

with col_info:
    st.subheader("📋 Trạng thái lệnh hiện tại")
    
    # Logic AI tự vào lệnh mẫu
    if not st.session_state.current_order:
        if rsi < 35: # Tín hiệu Mua
            st.session_state.current_order = {
                'side': 'BUY (LONG)', 'entry': price, 
                'tp': price + (atr * 2), 'sl': price - (atr * 1.5), 'time': datetime.now()
            }
        elif rsi > 65: # Tín hiệu Bán
            st.session_state.current_order = {
                'side': 'SELL (SHORT)', 'entry': price, 
                'tp': price - (atr * 2), 'sl': price + (atr * 1.5), 'time': datetime.now()
            }
    
    # Hiển thị thông tin lệnh đang chạy
    if st.session_state.current_order:
        order = st.session_state.current_order
        st.info(f"**Vị thế:** {order['side']}\n\n**Giá vào:** {order['entry']:,.1f}\n\n**Chốt lời (TP):** {order['tp']:,.1f}\n\n**Cắt lỗ (SL):** {order['sl']:,.1f}")
        
        # Giả lập đóng lệnh (Nếu giá chạm TP hoặc SL)
        if (order['side'] == 'BUY (LONG)' and (price >= order['tp'] or price <= order['sl'])) or \
           (order['side'] == 'SELL (SHORT)' and (price <= order['tp'] or price >= order['sl'])):
            
            pnl = "THẮNG ✅" if (order['side'] == 'BUY (LONG)' and price >= order['tp']) or (order['side'] == 'SELL (SHORT)' and price <= order['tp']) else "THUA ❌"
            st.session_state.trades.append({'side': order['side'], 'entry': order['entry'], 'exit': price, 'result': pnl})
            st.session_state.current_order = None
            st.balloons() if pnl == "THẮNG ✅" else st.snow()
    else:
        st.write("⏳ AI đang chờ vùng giá đẹp để vào lệnh mẫu...")

    # --- NHẬT KÝ VÀ ĐÚC KẾT ---
    st.write("---")
    st.subheader("📜 Nhật ký & Đúc kết")
    if st.session_state.trades:
        history_df = pd.DataFrame(st.session_state.trades)
        st.table(history_df.tail(5))
        
        # AI đúc kết kinh nghiệm
        win_rate = (len(history_df[history_df['result'] == "THẮNG ✅"]) / len(history_df)) * 100
        st.write(f"📈 Tỉ lệ thắng hiện tại: **{win_rate:.1f}%**")
        if win_rate > 60:
            st.success("💡 Đúc kết: Chiến thuật RSI + ATR đang hiệu quả. Giữ vững tâm lý!")
        else:
            st.warning("💡 Đúc kết: Thị trường nhiễu cao. AI khuyên nên nới rộng SL để tránh quét râu.")
    else:
        st.write("Chưa có dữ liệu giao dịch để đúc kết.")

with col_chart:
    st.subheader("📈 Biểu đồ thực tế")
    fig = go.Figure(data=[go.Candlestick(x=df['time_dt'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    # Vẽ đường Entry nếu đang có lệnh
    if st.session_state.current_order:
        fig.add_hline(y=st.session_state.current_order['entry'], line_dash="dash", line_color="yellow", annotation_text="ENTRY")
    fig.update_layout(xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.caption(f"Cập nhật lúc: {datetime.now().strftime('%H:%M:%S')} | Dữ liệu sàn OKX")
