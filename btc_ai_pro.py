from data_sources.binance import fetch_binance_ohlcv
from strategy import generate_signal
from database import insert_trade

def run_ai_trade():
    df = fetch_binance_ohlcv()
    signal = generate_signal(df)
    last_price = df['close'].iloc[-1]
    quantity = 0.001  # paper trade fixed
    if signal in ["BUY", "SELL"]:
        insert_trade("BTCUSDT", signal, last_price, quantity)
    return signal, last_price