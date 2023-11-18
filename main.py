import ccxt
import pandas as pd
import json
import time

from colorama import Fore, Back, Style

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

symbol = config['symbol']
timeframe = config['timeframe']
short_window = config['short_window']
long_window = config['long_window']

api_key = config['api_key']
api_secret = config['api_secret']

exchange = ccxt.cryptocom({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

last_action = "None"
last_balance = 0

balance_usd = 100
balance_crypto = 0

initial_balance = balance_usd

print(Fore.YELLOW + "------------------------")
print("Running...")
print("------------------------")

def order(action):
    global last_action
    global balance_usd
    global balance_crypto
    global initial_balance

    if action != last_action:
        last_action = action

        if action == "Buy":
            if balance_usd == 0:
                return
            
            initial_balance = get_total_balance()

            balance_crypto = balance_usd / df['close'].iloc[-1]
            balance_usd = 0

            print(Fore.GREEN + "-----------------[BUY]-----------------")
        elif action == "Sell":
            if balance_crypto == 0:
                return
            
            balance_usd = balance_crypto * df['close'].iloc[-1]
            balance_crypto = 0

            print(Fore.RED + "-----------------[SELL]-----------------")
            print(Fore.BLUE + "Profit: " + str(get_total_balance() - initial_balance) + " USD (" + str((get_total_balance() - initial_balance) / initial_balance * 100) + "%)")

def get_total_balance():
    return balance_usd + balance_crypto * df['close'].iloc[-1]

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
    action = "None"

    for index, row in df.iterrows():
        if row['short_mavg'] > row['long_mavg'] and not in_position:
            action = "Buy"
            # exchange.create_market_buy_order('BTC/USDT', amount)
            in_position = True
        elif row['short_mavg'] < row['long_mavg'] and in_position:
            action = "Sell"
            # exchange.create_market_sell_order('BTC/USDT', amount)
            in_position = False

    order(action)

while True:
    try:
        df = fetch_ohlcv(symbol, timeframe)
        df = calculate_moving_averages(df, short_window, long_window)

        execute_orders(df)

        current = get_total_balance()

        if current != last_balance:
            last_balance = current
            print(Fore.WHITE + "Current balance: " + str(get_total_balance()))
    except Exception as e:
        print(Fore.YELLOW + "Error: " + str(e))

    time.sleep(1)