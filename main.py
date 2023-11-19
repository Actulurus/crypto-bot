import ccxt
import pandas as pd
import json
import time
import sys

from colorama import Fore, Back, Style

try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print(Fore.YELLOW + "config.json not found - created one for you. Please fill it out and restart the program.")
    print(Fore.WHITE)

    with open('config.json', 'w') as config_file:
        config = {
            "symbol": "BTC/USDT",
            "timeframe": "5m",
            "short_window": 10,
            "long_window": 30,
            "initial_balance": 100,
            "api_key": "Your api key here",
            "api_secret": "Your api secret here"
        }

        json.dump(config, config_file, indent=4)
    
    exit()

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

arg1 = sys.argv[1] if len(sys.argv) > 1 else None
arg2 = sys.argv[2] if len(sys.argv) > 2 else None
arg3 = sys.argv[3] if len(sys.argv) > 3 else None
arg4 = sys.argv[4] if len(sys.argv) > 4 else None

IS_TEST_MODE = (arg3 or "") == "True"
TEST_DURATION = int(arg4 or "0")

symbol = config['symbol']
timeframe = config['timeframe']
short_window = int(arg1 or config['short_window'])
long_window = int(arg2 or config['long_window'])

api_key = config['api_key']
api_secret = config['api_secret']

if " " in api_key or " " in api_secret:
    exit()

exchange = ccxt.cryptocom({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
})

runtime_start = time.time()

last_action = "None"
last_balance = 0

balance_usd = config["initial_balance"]
balance_crypto = 0

initial_balance = balance_usd

trades_completed = 0

print(Fore.YELLOW + "------------------------")
if IS_TEST_MODE:
    print("Running in TEST mode...")
else:
    print("Running in LIVE mode...")
print("------------------------")

def order(action):
    global last_action
    global balance_usd
    global balance_crypto
    global initial_balance
    global trades_completed

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

            trades_completed += 1

            print(Fore.RED + "-----------------[SELL]-----------------")
            print(Fore.BLUE + "Profit: " + str(get_total_balance() - initial_balance) + " USD (" + str((get_total_balance() - initial_balance) / initial_balance * 100) + "%)")

def get_total_balance():
    return balance_usd + balance_crypto * df['close'].iloc[-1]

def fetch_ohlcv(symbol, timeframe):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=60)
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
        if row['short_mavg'] > row['long_mavg']:
            action = "Buy"
            # exchange.create_market_buy_order('BTC/USDT', amount)
            in_position = True
        elif row['short_mavg'] < row['long_mavg']:
            action = "Sell"
            # exchange.create_market_sell_order('BTC/USDT', amount)
            in_position = False
    
    order(action)

while True:
    if IS_TEST_MODE:
        if time.time() - runtime_start >= TEST_DURATION:
            print(Fore.YELLOW + "Test duration reached - exiting...")

            # Write a log file
            with open('TestOutput/log_' + str(short_window) + '_' + str(long_window) + '_' + str(runtime_start) + '.txt', 'w') as log_file:
                log_file.write("Short window: " + str(short_window) + "\n")
                log_file.write("Long window: " + str(long_window) + "\n")
                log_file.write("Profit: " + str(get_total_balance() - initial_balance) + " USD (" + str(abs(get_total_balance() - initial_balance) / initial_balance * 100) + "%)\n")
                log_file.write("Trades completed: " + str(trades_completed) + "\n")
                log_file.write("Final balance: " + str(get_total_balance()) + "\n")

            exit()
    
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

    time.sleep(2)