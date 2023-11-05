import ccxt
import pandas as pd

# Replace these with your own Crypto.com API key and secret
api_key = 'PvUo7vMTTBJcTmZJQBwctu'
api_secret = 'Z8vMidbeAxr8hZyy7FPkCN'

exchange = ccxt.cryptocom({
    'apiKey': api_key,
    'secret': api_secret,,
    'enableRateLimit': True,
})

print("Running")

def fetch_ohlcv(symbol, timeframe):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def calculate_moving_averages(df, short_window, long_window):
    df['short_mavg'] = df['close'].rolling(window=short_window).mean()
    df['long_mavg'] = df['close'].rolling(window=long_window).mean()
    return df

def execute_orders(df):
    in_position = False

    for index, row in df.iterrows():
        if row['short_mavg'] > row['long_mavg'] and not in_position:
            print("Buy")
            # exchange.create_market_buy_order('BTC/USDT', amount)
            in_position = True
        elif row['short_mavg'] < row['long_mavg'] and in_position:
            print("Sell")
            # exchange.create_market_sell_order('BTC/USDT', amount)
            in_position = False


symbol = 'SOL/USD'
timeframe = '1m'
short_window = 50
long_window = 100

df = fetch_ohlcv(symbol, timeframe)
df = calculate_moving_averages(df, short_window, long_window)
execute_orders(df)