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

def calculate_heikin_ashi(candles):
    heikin_ashi_candles = []
    for i in range(len(candles)):
        if i == 0:
            ha_close = candles[i][4]
            ha_open = (candles[i][1] + candles[i][4]) / 2.0
        else:
            ha_close = (candles[i][1] + candles[i][2] + candles[i][3] + candles[i][4]) / 4.0
            ha_open = (heikin_ashi_candles[i - 1][1] + heikin_ashi_candles[i - 1][4]) / 2.0

        ha_high = max(candles[i][2], ha_open, ha_close)
        ha_low = min(candles[i][3], ha_open, ha_close)

        heikin_ashi_candles.append([candles[i][0], ha_open, ha_high, ha_low, ha_close, candles[i][5]])

    return heikin_ashi_candles

def get_candle_body(candle):
    return candle[1] - candle[4]
def get_candle_size(candle):
    return abs(get_candle_body(candle))
def get_candle_direction(candle):
    if get_candle_body(candle) > 0:
        return 1
    elif get_candle_body(candle) < 0:
        return -1
    else:
        return 0

def get_lower_wick(candle):
    return candle[4] - candle[5]

def get_upper_wick(candle):
    return candle[2] - candle[1]

def get_length_of_opposite_wick(candle):
    if get_candle_body(candle) > 0:
        return get_lower_wick(candle)
    elif get_candle_body(candle) < 0:
        return get_upper_wick(candle)
    else:
        return 0
def is_opposite_wick_short_enough(candle):
    return get_length_of_opposite_wick(candle) < 0.05

def is_doji(candle):
    avg_wick = (get_lower_wick(candle) - get_upper_wick(candle)) / 2
    are_wicks_similar = abs(get_lower_wick(candle) - get_upper_wick(candle)) < avg_wick * 2 * 0.5
    is_body_small = get_candle_size(candle) < avg_wick * 1.1
    print("wicks similar", are_wicks_similar, "body small", is_body_small)
    return are_wicks_similar and is_body_small 

while True:
    # Fetch the latest candlestick data
    candles = calculate_heikin_ashi(exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=3))

    direction = get_candle_direction(candles[0])
    dont_take_action = False

    for i in range(0, 1):
        if get_candle_direction(candles[i]) != direction:
            dont_take_action = True
            print(i, "direction is not the same")
        elif not is_opposite_wick_short_enough(candles[i]):
            dont_take_action = True
            print(i, "opposite wick is too long")
        elif is_doji(candles[i]):
            dont_take_action = True
            print(i, "is doji, but only the last candle can be doji")
        elif direction == 0:
            dont_take_action = True
            print(i, "direction is 0")

    if not is_doji(candles[2]):
        dont_take_action = True
        print("3rd candle is not doji")

    if not dont_take_action:
        for i in range(1, 10): # Just to make it more visible
            print("BUY" if direction > 0 else "SELL")
    