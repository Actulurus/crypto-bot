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

# def get_candle_body(candle):
#     return candle[1] - candle[4]
# def get_candle_size(candle):
#     return abs(get_candle_body(candle))
# def get_candle_direction(candle):
#     if get_candle_body(candle) > 0:
#         return 1
#     elif get_candle_body(candle) < 0:
#         return -1
#     else:
#         return 0

# def get_lower_wick(candle):
#     if get_candle_direction(candle) > 0:
#         return candle[1] - candle[3]
#     elif get_candle_direction(candle) < 0:
#         return candle[4] - candle[3]

# def get_upper_wick(candle):
#     if get_candle_direction(candle) > 0:
#         return candle[2] - candle[4]
#     elif get_candle_direction(candle) < 0:
#         return candle[2] - candle[1]

# def get_length_of_opposite_wick(candle):
#     if get_candle_body(candle) > 0:
#         return get_lower_wick(candle)
#     elif get_candle_body(candle) < 0:
#         return get_upper_wick(candle)
#     else:
#         return 0
# def is_opposite_wick_short_enough(candle):
#     return get_length_of_opposite_wick(candle) < 0.05

# def is_doji(candle):
#     avg_wick = (get_lower_wick(candle) - get_upper_wick(candle)) / 2
#     are_wicks_long_enough = get_lower_wick(candle) > get_candle_size(candle) * 0.9 and get_upper_wick(candle) > get_candle_size(candle) * 0.9
#     is_body_small = get_candle_size(candle) < avg_wick * 1.1

#     return are_wicks_long_enough and is_body_small 

# new functions
def is_green_no_lower_wick(candle):
    return candle[1] < candle[4] and abs(candle[1] - candle[3]) < 0.05

def is_red_no_upper_wick(candle):
    return candle[1] > candle[4] and abs(candle[2] - candle[1]) < 0.05

def _is_doji(candle):
    w1, w2 = 0, 0
    if candle[1] > candle[4]:
        w1 = candle[2] - candle[1]
        w2 = candle[4] - candle[3]
    elif candle[1] < candle[4]:
        w1 = candle[4] - candle[3]
        w2 = candle[2] - candle[1]
    print(w1, w2)
    # checks whether body is smaller than the average wick size and whether the difference between the wicks is smaller than the size of the body
    return abs(candle[1] - candle[4]) < (w1 + w2) / 2 and abs(w1 - w2) < abs(candle[1] - candle[4])
##### end

def is_doji(candle):
    return abs(candle[1] - candle[4]) < 0.01

while True:
    # Fetch the latest candlestick data
    candles = calculate_heikin_ashi(exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=3))
    dont_take_action = False
    print(candles[0], candles[1], candles[2], candles[3])
    for i in range(0, 2):
        is_green = is_green_no_lower_wick(candles[i])
        is_red = is_red_no_upper_wick(candles[i])
        doji = is_doji(candles[i])

        if doji:
            print(i + 1, "is doji")
        elif is_green:
            print(i + 1, "is green")
        elif is_red:
            print(i + 1, "is red")
        
        print("------------------")

    # if not is_green and not is_red:
    #     dont_take_action = True
    #     print("1st candle is not green or red")

    # for i in range(0, 1):
    #     green = is_green_no_lower_wick(candles[i])
    #     red = is_red_no_upper_wick(candles[i])

    #     if not (green and is_green) and not (red and is_red):
    #         dont_take_action = True
    #         print(i + 1, "doesnt match other candle")
    #     elif is_doji(candles[i]):
    #         dont_take_action = True
    #         print(i + 1, "must not be doji")

    # if not is_doji(candles[2]):
    #     dont_take_action = True
    #     print("3rd candle is not doji")

    # if not dont_take_action:
    #     for i in range(1, 10): # Just to make it more visible
    #         print("BUY" if is_green else "SELL")
    