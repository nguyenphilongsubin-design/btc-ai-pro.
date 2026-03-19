import ccxt
import pandas as pd

def run_bot():
    # Đổi sang OKX để GitHub không bị chặn
    exchange = ccxt.okx() 
    bars = exchange.fetch_ohlcv('BTC/USDT', timeframe='1h', limit=100)
    df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    
    # Tính RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain/loss)))
    
    last = df.iloc[-1]
    print(f"--- KẾT QUẢ AI SOI KÈO (DỮ LIỆU OKX) ---")
    print(f"Giá BTC: {last['close']} | RSI: {last['RSI']:.2f}")

if __name__ == "__main__":
    run_bot()
