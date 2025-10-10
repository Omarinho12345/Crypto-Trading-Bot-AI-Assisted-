import os
import time
import csv
import pandas as pd
import ccxt
import requests
from dotenv import load_dotenv
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator

# Load environment variables from .env (don't commit .env to git)
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("ERROR: TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set in the .env file.")
    print("Edit the .env file and add your values, then run the bot again.")
    raise SystemExit(1)

print("Bot starting... (simulated trading mode)")

# CONFIG
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'
TRADE_AMOUNT = 0.001
RSI_PERIOD = 14
SMA_PERIOD = 200
STOP_LOSS_PCT = -0.02
TAKE_PROFIT_PCT = 0.04

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code != 200:
            print(f"[Telegram] non-200 response: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[Telegram Error] {e}")

# State (simulated)
balance = {'USDT': 10000.0, 'BTC': 0.0}
open_trade = None # format: {'price': float, 'side': 'buy'/'sell'}
trade_history = []

exchange = ccxt.binance({'enableRateLimit': True})

def fetch_ohlcv():
    data = exchange.fetch_ohlcv(SYMBOL, TIMEFRAME)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    return df

def generate_signal(df):
    close = df['close']
    rsi = RSIIndicator(close, RSI_PERIOD).rsi()
    macd = MACD(close).macd()
    signal = MACD(close).macd_signal()
    sma = SMAIndicator(close, SMA_PERIOD).sma_indicator()

    df['rsi'] = rsi
    df['macd'] = macd
    df['macd_signal'] = signal
    df['sma'] = sma

    # Simple signal logic (same as original)
    if (
        rsi.iloc[-1] < 30 and
        macd.iloc[-2] < signal.iloc[-2] and
        macd.iloc[-1] > signal.iloc[-1] and
        close.iloc[-1] > sma.iloc[-1]
    ):
        return 'buy'
    elif (
        rsi.iloc[-1] > 70 and
        macd.iloc[-2] > signal.iloc[-2] and
        macd.iloc[-1] < signal.iloc[-1] and
        close.iloc[-1] < sma.iloc[-1]
    ):
        return 'sell'
    return 'hold'

def simulate_trade(signal, price):
    global balance, open_trade, trade_history

    if signal == 'buy' and balance['USDT'] >= price * TRADE_AMOUNT and open_trade is None:
        balance['USDT'] -= price * TRADE_AMOUNT
        balance['BTC'] += TRADE_AMOUNT
        open_trade = {'price': price, 'side': 'buy'}
        log_trade('buy', price)
        send_telegram(f"📈 Simulated BUY at ${price:.2f}")
    elif signal == 'sell' and balance['BTC'] >= TRADE_AMOUNT and open_trade is None:
        balance['USDT'] += price * TRADE_AMOUNT
        balance['BTC'] -= TRADE_AMOUNT
        open_trade = {'price': price, 'side': 'sell'}
        log_trade('sell', price)
        send_telegram(f"📉 Simulated SELL at ${price:.2f}")

def check_exit(price):
    global open_trade, balance

    if open_trade is None:
        return

    entry_price = open_trade['price']
    side = open_trade['side']
    pnl = 0

    if side == 'buy':
        pnl_pct = (price - entry_price) / entry_price
        if pnl_pct >= TAKE_PROFIT_PCT or pnl_pct <= STOP_LOSS_PCT:
            balance['USDT'] += price * TRADE_AMOUNT
            balance['BTC'] -= TRADE_AMOUNT
            pnl = pnl_pct * 100
            log_trade('sell (exit)', price, pnl)
            send_telegram(f"✅ CLOSED BUY @ ${price:.2f} | PnL: {pnl:.2f}%")
            open_trade = None
    elif side == 'sell':
        pnl_pct = (entry_price - price) / entry_price
        if pnl_pct >= TAKE_PROFIT_PCT or pnl_pct <= STOP_LOSS_PCT:
            balance['USDT'] -= price * TRADE_AMOUNT
            balance['BTC'] += TRADE_AMOUNT
            pnl = pnl_pct * 100
            log_trade('buy (exit)', price, pnl)
            send_telegram(f"✅ CLOSED SELL @ ${price:.2f} | PnL: {pnl:.2f}%")
            open_trade = None

def log_trade(action, price, pnl=None):
    global trade_history
    trade = {
        'time': pd.Timestamp.now(),
        'action': action,
        'price': price,
        'pnl': pnl
    }
    trade_history.append(trade)
    write_trade_to_csv(trade)

def write_trade_to_csv(trade):
    file_exists = os.path.isfile('trades.csv')
    with open('trades.csv', 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=trade.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade)

def run_bot():
    while True:
        try:
            df = fetch_ohlcv()
            signal = generate_signal(df)
            price = df['close'].iloc[-1]

            print(f"[{pd.to_datetime(df['timestamp'].iloc[-1], unit='ms')}] Signal: {signal} | Price: {price:.2f}")
            check_exit(price) # Check for TP/SL before opening new trades

            if open_trade is None:
                simulate_trade(signal, price)

            print(f"Balance: {balance}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(60 * 60) # Run every hour

if __name__ == '__main__':
    run_bot()
