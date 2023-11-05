import os
import ccxt
import time
import talib
import numpy as np
from datetime import datetime

# Replace these with your own Crypto.com API key and secret
# api_key = 'PvUo7vMTTBJcTmZJQBwctu'
# api_secret = 'Z8vMidbeAxr8hZyy7FPkCN'

# Create an instance of the Crypto.com exchange
exchange = ccxt.binance()

# Set your API credentials
# exchange.apiKey = api_key
# exchange.secret = api_secret

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
    
    print_candle_time(last_three_candles[0])
    print(is_doji(last_three_candles[0]))

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
    open_price, high_price, low_price, close_price = candle[1:5]
    
    body_size = abs(open_price - close_price)
    wicks_size = high_price - max(open_price, close_price, key=lambda x: abs(x - high_price))
    
    return body_size < wicks_size and wicks_size > 0

def is_red_doji(candle):
    return candle[4] < candle[1] and is_doji(candle)

def print_candle_time(candle):
    unix_timestamp = candle[0] / 1000

    try:
        # Convert the Unix timestamp to a datetime object
        dt_object = datetime.fromtimestamp(unix_timestamp)

        # Format the datetime as a string in a human-readable format
        human_readable_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")

        print(f"On {human_readable_time}")
    except Exception as e:
        print(f"Error: {e}")

# Main loop
while True:
    # Fetch the latest candlestick data
    candles = exchange.fetch_ohlcv(symbol, timeframe, limit=3)

    # Check the Heikin-Ashi strategy
    signal = check_heikin_ashi_strategy(candles)
    if signal:
        print(f"Signal: {signal}")
    
    time.sleep(1)
    
