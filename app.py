import streamlit as st
import ccxt
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime

# 1. Cấu hình giao diện và Bộ nhớ giao dịch
st.set_page_config(layout="wide", page_title="BTC AI PRO MAX")

# Khởi tạo bộ nhớ tạm để lưu lệnh trade mẫu
if 'trades' not in st.session_state: st.session_state.trades = []
if 'current_order' not in st.session_state: st.session_state.current_order = None

# --- PHẦN 1: CÁC HÀM LẤY DỮ LIỆU ---
exchange = ccxt.okx()
symbol = 'BTC/USDT'

def get_data(tf='1h'):
    bars = exchange.fetch_ohlcv(symbol, timeframe=tf, limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time_dt'] = pd.to_datetime(df['time'], unit='ms')
    delta = df['close'].diff()
    df['RSI'] = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))
    df['ATR'] = (df['high'] - df['low']).rolling(14).mean()
    df['MA20'] = df['close'].rolling(20).mean()
    return df

def get_fear_greed():
    try:
        r = requests.get('https://alternative.me').json()
        return int(r['data'][0]['value']), r['data'][0]['value_classification']
    except: return 50, "Neutral"

# --- PHẦN 2: HIỂN THỊ TÂM LÝ & ĐA KHUNG GIỜ ---
st.title("🚀 BTC AI PRO MAX - TRADING TERMINAL")
fng_val, fng_text = get_fear_greed()
st.subheader(f"🧠 Tâm lý: {fng_text} ({fng_val}/100)")
st.progress(fng_val/100)

st.write("---")
st.subheader("📊 Xu hướng đa khung thời gian (Trend Analysis)")
tfs = ['1d', '4h', '1h']
cols_tf = st.columns(3)
for i, tf in enumerate(tfs):
    d = get_data(tf)
    last_d = d.iloc[-1]
    with cols_tf[i]:
        st.info(f"**Khung {tf.upper()}**")
        st.metric("Giá", f"${last_d['close']:,.1f}")
        if last_d['close'] > last_d['MA20']: st.success("🔥 TĂNG")
        else: st.error("❄️ GIẢM")

st.write("---")

# --- PHẦN 3: TRADE MẪU & THÔNG BÁO NHẤP NHÁY ---
df = get_data('1h')
last = df.iloc[-1]
price, rsi, atr = last['close'], last['RSI'], last['ATR']

# Hiệu ứng nhấp nháy khi có lệnh
if st.session_state.current_order:
    st.markdown("""
        <style>
        @keyframes blink { 0% { opacity: 1; } 50% { opacity: 0; } 100% { opacity: 1; } }
        .blink { animation: blink 1s linear infinite; color: #fff; background: #FF4B4B; font-weight: bold; padding: 15px; border-radius: 10px; text-align: center; font-size: 20px; }
        </style>
        <div class="blink">📢 AI ĐANG VÀO LỆNH: THEO DÕI BIẾN ĐỘNG THỰC TẾ!</div>
        """, unsafe_allow_html=True)

col_trade, col_chart = st.columns([1, 2])

with col_trade:
    st.subheader("📋 Trạng thái lệnh")
    
    # Logic AI tự vào lệnh mẫu (Paper Trade)
    if not st.session_state.current_order:
        if rsi < 35: # Tín hiệu Mua
            st.session_state.current_order = {'side': 'BUY (LONG)', 'entry': price, 'tp': price + (atr * 2), 'sl': price - (atr * 1.5), 'time': datetime.now()}
        elif rsi > 65: # Tín hiệu Bán
            st.session_state.current_order = {'side': 'SELL (SHORT)', 'entry': price, 'tp': price - (atr * 2), 'sl': price + (atr * 1.5), 'time': datetime.now()}
    
    # Hiển thị lệnh đang chạy
    if st.session_state.current_order:
        o = st.session_state.current_order
        st.warning(f"**Vị thế:** {o['side']}")
        st.code(f"ENTRY: {o['entry']:,.1f}\nTP:    {o['tp']:,.1f}\nSL:    {o['sl']:,.1f}")
        
        # Check đóng lệnh mẫu
        if (o['side'] == 'BUY (LONG)' and (price >= o['tp'] or price <= o['sl'])) or \
           (o['side'] == 'SELL (SHORT)' and (price <= o['tp'] or price >= o['sl'])):
            res = "THẮNG ✅" if (o['side'] == 'BUY (LONG)' and price >= o['tp']) or (o['side'] == 'SELL (SHORT)' and price <= o['tp']) else "THUA ❌"
            st.session_state.trades.append({'time': datetime.now().strftime('%H:%M'), 'side': o['side'], 'result': res, 'pnl': f"{((price/o['entry'])-1)*100:.2f}%"})
            st.session_state.current_order = None
            st.balloons() if "THẮNG" in res else st.snow()
    else:
        st.info("⏳ AI đang soi kèo... Đợi RSI chạm 35 hoặc 65.")

with col_chart:
    fig = go.Figure(data=[go.Candlestick(x=df['time_dt'], open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    if st.session_state.current_order:
        fig.add_hline(y=st.session_state.current_order['entry'], line_dash="dash", line_color="yellow")
    fig.update_layout(xaxis_rangeslider_visible=False, height=500, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

st.write("---")

# --- PHẦN 4: NHẬT KÝ & ĐÚC KẾT KINH NGHIỆM ---
st.subheader("📜 Nhật ký Trade & Đúc kết kinh nghiệm AI")
if st.session_state.trades:
    hist_df = pd.DataFrame(st.session_state.trades)
    st.table(hist_df.tail(5))
    
    win_rate = (len(hist_df[hist_df['result'] == "THẮNG ✅"]) / len(hist_df)) * 100
    st.metric("Tỉ lệ thắng thực tế", f"{win_rate:.1f}%")
    
    if win_rate >= 60: st.success("💡 **Kinh nghiệm:** Chiến thuật RSI kết hợp ATR đang khớp nhịp thị trường. Tiếp tục duy trì!")
    else: st.warning("💡 **Kinh nghiệm:** Thị trường biến động quá nhanh (High Volatility). AI khuyên nên nới SL rộng hơn 2.0 ATR.")
else:
    st.write("Đang chờ lệnh đầu tiên để đúc kết kinh nghiệm...")

st.caption(f"Dữ liệu cập nhật lúc: {datetime.now().strftime('%H:%M:%S')}")
