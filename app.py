import streamlit as st
import ccxt
import pandas as pd
from streamlit_lightweight_charts import renderLightweightCharts

# 1. Cấu hình giao diện chuẩn Binance
st.set_page_config(layout="wide", page_title="BTC AI PRO - TRADING TERMINAL")
st.title("📊 BTC AI PRO - HỆ THỐNG TƯ VẤN GIAO DỊCH")

# 2. Lấy dữ liệu đa khung thời gian
symbol = 'BTC/USDT'
exchange = ccxt.okx()

def get_ai_data():
    bars = exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100)
    df = pd.DataFrame(bars, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = df['time'] / 1000 # Chuẩn hóa thời gian cho biểu đồ
    
    # Tính toán AI: RSI + ATR (Đo độ biến động để đặt TP/SL)
    delta = df['close'].diff()
    df['RSI'] = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))
    df['ATR'] = (df['high'] - df['low']).rolling(window=14).mean()
    return df

try:
    df = get_ai_data()
    last = df.iloc[-1]
    
    # --- PHẦN 1: BẢNG TƯ VẤN AI (BÊN TRÁI) ---
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("🤖 AI ADVISOR")
        price = last['close']
        rsi = last['RSI']
        atr = last['ATR']
        
        # LOGIC TƯ VẤN CHI TIẾT
        if rsi < 35:
            advice = "🚀 NÊN MUA (LONG)"
            entry = price
            tp = price + (atr * 2.5) # Chốt lời theo biên độ biến động
            sl = price - (atr * 1.5) # Cắt lỗ an toàn
            st.success(advice)
        elif rsi > 65:
            advice = "⚠️ NÊN BÁN (SHORT)"
            entry = price
            tp = price - (atr * 2.5)
            sl = price + (atr * 1.5)
            st.error(advice)
        else:
            advice = "⏳ CHỜ TÍN HIỆU"
            st.warning(advice)
        
        st.write(f"**Giá hiện tại:** `{price:,.2f}`")
        if advice != "⏳ CHỜ TÍN HIỆU":
            st.info(f"📍 **Vùng vào:** {entry:,.1f}\n\n🎯 **Chốt lời:** {tp:,.1f}\n\n🛡️ **Cắt lỗ:** {sl:,.1f}")
        
        st.write(f"**Sức mạnh (RSI):** {rsi:.2f}")

    # --- PHẦN 2: BIỂU ĐỒ CHUẨN TRADINGVIEW (BÊN PHẢI) ---
    with col2:
        chart_data = df[['time', 'open', 'high', 'low', 'close']].to_dict('records')
        chart_options = {
            "layout": {"backgroundColor": "#000000", "textColor": "#FFFFFF"},
            "grid": {"vertLines": {"color": "#1f1f1f"}, "horzLines": {"color": "#1f1f1f"}},
            "timeScale": {"timeVisible": True, "secondsVisible": False}
        }
        renderLightweightCharts([{"type": "Candlestick", "data": chart_data}], chart_options)

except Exception as e:
    st.error(f"Đang đồng bộ dữ liệu với sàn... Vui lòng chờ 10 giây.")
