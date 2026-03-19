import ccxt
import pandas as pd

def run_bot():
    exchange = ccxt.binance()
    # Lấy dữ liệu 100 nến 1h
    bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Tính RSI đơn giản
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))
    
    last = df.iloc[-1]
    print(f"--- KẾT QUẢ AI SOI KÈO ---")
    print(f"Giá BTC hiện tại: {last['close']}")
    print(f"Chỉ số RSI: {last['RSI']:.2f}")
    
    if last['RSI'] < 35:
        print("🚀 TÍN HIỆU: VÙNG MUA ĐẸP!")
    elif last['RSI'] > 65:
        print("⚠️ TÍN HIỆU: VÙNG QUÁ MUA - CẨN THẬN!")
    else:
        print("⏳ AI nói: Chưa có kèo ngon, tiếp tục quan sát.")

if __name__ == "__main__":
    run_bot()
