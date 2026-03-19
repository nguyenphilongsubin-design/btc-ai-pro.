import ccxt
import pandas as pd
import time

# --- CẤU HÌNH ---
symbol = 'BTC/USDT'
timeframe = '1h'
exchange = ccxt.binance()

def fetch_data():
    """Lấy dữ liệu 100 nến gần nhất từ Binance"""
    bars = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def ai_brain_analysis(df):
    """Bộ não AI tính toán đa chỉ số: RSI, Bollinger Bands, Volume"""
    # 1. RSI (14) - Đo sức mạnh mua/bán
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))

    # 2. Bollinger Bands (20, 2) - Đo vùng nén giá
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['STD'] = df['close'].rolling(window=20).std()
    df['UPPER'] = df['MA20'] + (df['STD'] * 2)
    df['LOWER'] = df['MA20'] - (df['STD'] * 2)

    # 3. Volume Average - So sánh dòng tiền cá mập
    df['VOL_AVG'] = df['volume'].rolling(window=20).mean()
    return df

def phan_tich_tin_hieu(df):
    """Đưa ra quyết định thông minh"""
    last = df.iloc[-1]
    prev = df.iloc[-2]
    
    gia = last['close']
    rsi = last['RSI']
    upper = last['UPPER']
    lower = last['LOWER']
    vol = last['volume']
    vol_avg = last['VOL_AVG']

    print(f"\n[DỮ LIỆU]: Giá: {gia:.2f} | RSI: {rsi:.2f}")

    # CHIẾN THUẬT 1: MUA KHI GIÁ CHẠM ĐÁY + RSI THẤP + VOL TĂNG (Cá mập gom)
    if gia <= lower and rsi < 35 and vol > vol_avg:
        return "🚀 [TÍN HIỆU MUA]: Giá chạm đáy BB + RSI quá bán + Volume đột biến. CÁ MẬP ĐANG GOM!"

    # CHIẾN THUẬT 2: BÁN KHI GIÁ CHẠM ĐỈNH + RSI CAO (Quá mua)
    elif gia >= upper and rsi > 65:
        return "⚠️ [TÍN HIỆU BÁN]: Giá chạm đỉnh BB + RSI quá mua. RỦI RO ĐU ĐỈNH!"

    # CHIẾN THUẬT 3: CẢNH BÁO PHÂN KỲ (Giá tăng nhưng RSI giảm)
    elif gia > prev['close'] and rsi < prev['RSI'] and rsi > 60:
        return "📉 [CẢNH BÁO]: Phân kỳ âm! Giá tăng ảo, sức mua thực tế đang giảm."

    return "⏳ AI đang quét thị trường... Chưa có kèo thơm."

def run_bot():
    print("🤖 BTC AI PRO ĐANG KHỞI CHẠY (CHẾ ĐỘ 24/7)...")
    while True:
        try:
            df = fetch_data()
            df = ai_brain_analysis(df)
            signal = phan_tich_tin_hieu(df)
            print(signal)
            time.sleep(60) # Quét lại sau mỗi 1 phút
        except Exception as e:
            print(f"Lỗi: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
