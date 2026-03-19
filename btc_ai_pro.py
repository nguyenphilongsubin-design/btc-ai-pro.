import ccxt
import pandas as pd

def run_bot():
    exchange = ccxt.binance()
    # 1. Lấy dữ liệu 100 nến 1h từ Binance
    bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # 2. Tính chỉ số RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))
    
    # 3. Lấy kết quả mới nhất
    last = df.iloc[-1]
    print(f"--- KẾT QUẢ AI SOI KÈO ---")
    print(f"Giá BTC hiện tại: {last['close']}")
    print(f"Chỉ số RSI: {last['RSI']:.2f}")
    
    # 4. Đưa ra tín hiệu
    if last['RSI'] < 35:
        print("🚀 TÍN HIỆU: VÙNG MUA ĐẸP!")
    elif last['RSI'] > 65:
        print("⚠️ TÍN HIỆU: VÙNG QUÁ MUA - CẨN THẬN!")
    else:
        print("⏳ AI nói: Chưa có kèo thơm, tiếp tục quan sát.")

if __name__ == "__main__":
    run_bot()
