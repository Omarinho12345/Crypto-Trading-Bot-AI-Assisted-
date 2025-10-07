import pandas as pd
import time
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
import ccxt
import csv
import os
import requests
print("bot is staring...")

# CONFIG
SYMBOL = 'BTC/USDT'
TIMEFRAME = '1h'
TRADE_AMOUNT = 0.001
RSI_PERIOD = 14
SMA_PERIOD = 200
STOP_LOSS_PCT = -0.02
TAKE_PROFIT_PCT = 0.04

# Telegram setup (optional)
TELEGRAM_TOKEN = '7945631332:AAFuF2wWOaLhhZrwvVeegIre14C_i4dvSVQ'
TELEGRAM_CHAT_ID = '5327701115'

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[Telegram Error] {e}")

# State
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

# Run it
run_bot()
