import os
import ccxt
import time
import talib
import numpy as np

# Replace these with your own Crypto.com API key and secret
api_key = 'PvUo7vMTTBJcTmZJQBwctu'
api_secret = 'Z8vMidbeAxr8hZyy7FPkCN'

# Create an instance of the Crypto.com exchange
exchange = ccxt.cryptocom()

# Set your API credentials
exchange.apiKey = api_key
exchange.secret = api_secret

# Define the trading pair and timeframe
symbol = 'SOL/USD'  # Replace with your desired trading pair
timeframe = '1m'  # Adjust to the desired timeframe (e.g., 1h, 4h, 1d)

last_candle = None

print("Running...")

def check_heikin_ashi_strategy(candles):
    if len(candles) < 3:
        return None

    # Calculate Heikin-Ashi data
    ha_candles = get_heikin_ashi(candles)

    # Get the last three candles
    last_three_candles = ha_candles[-3:]

    # Check for Doji candle
    if is_doji(last_three_candles[0]):
        # Check for two consecutive candles without lower wicks
        if (last_three_candles[1][2] == last_three_candles[1][3]) and (last_three_candles[2][2] == last_three_candles[2][3]):
            return "Buy"  # Buy signal

    # Check for Doji candle (preferably red)
    if is_red_doji(last_three_candles[0]):
        # Check for two consecutive candles without upper wicks
        if (last_three_candles[1][1] == last_three_candles[1][4]) and (last_three_candles[2][1] == last_three_candles[2][4]):
            return "Sell"  # Sell signal

    return None  # No signal

def get_heikin_ashi(candles):
    heikin_ashi_candles = []
    for candle in candles:
        if len(heikin_ashi_candles) == 0:
            ha_close = (candle[1] + candle[2] + candle[3] + candle[4]) / 4.0
            ha_open = (candle[1] + candle[4]) / 2.0
        else:
            ha_close = (candle[1] + candle[2] + candle[3] + candle[4]) / 4.0
            ha_open = (heikin_ashi_candles[-1][1] + heikin_ashi_candles[-1][4]) / 2.0
        ha_high = max(candle[2], ha_open, ha_close)
        ha_low = min(candle[3], ha_open, ha_close)
        heikin_ashi_candles.append([candle[0], ha_open, ha_high, ha_low, ha_close, candle[5]])
    return heikin_ashi_candles

def is_doji(candle):
    return abs(candle[1] - candle[4]) <= (candle[2] - candle[3]) * 0.1

def is_red_doji(candle):
    return candle[4] < candle[1] and is_doji(candle)

# Main loop
while True:
    # Fetch the latest candlestick data
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=3)

    # Check the Heikin-Ashi strategy
    signal = check_heikin_ashi_strategy(candles)
    if signal:
        print(f"Signal: {signal}")
    
    time.sleep(5)
    