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

def get_heikin_ashi(raw_candles):
    # Extract the OHLC data from the raw candles
    open_prices = np.array([candle[1] for candle in raw_candles], dtype=float)
    high_prices = np.array([candle[2] for candle in raw_candles], dtype=float)
    low_prices = np.array([candle[3] for candle in raw_candles], dtype=float)
    close_prices = np.array([candle[4] for candle in raw_candles], dtype=float)

    # Calculate Heikin-Ashi candles using TA-Lib
    heikin_ashi = talib.CDLHEIKINASHI(open_prices, high_prices, low_prices, close_prices)

    # Create a list of Heikin-Ashi candles
    heikin_ashi_candles = list(zip(*[raw_candles, heikin_ashi]))

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
    candles = get_hk(exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=3))

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
    