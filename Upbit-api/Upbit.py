import ccxt
import config
import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import time

#Api
upbit = ccxt.upbit({
    'enbaleRateLimit' : True,
    'apiKey': config.Ubpit_ApiKey,
    'secret': config.Ubpit_SecretKey,
})

def balance():
    balance_info = upbit.fetch_balance()
    krw_balance = balance_info['total']['KRW']

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Current KRW Balance: {krw_balance} KRW\n")

    # Display total balance
    display_total_balance(balance_info)


def buy():
    try: 
        market = market_var.get() 
        amount_to_buy = float(amount_entry.get())
        

        ticker = upbit.fetch_ticker(market)
        last_price = ticker['close']
        
        total_cost = amount_to_buy * last_price
        if total_cost < 5000: #UP minimum num order 5000 KRW
            result_text.insert(tk.END, f"Total cost ({total_cost} KRW) is below the minimum order amount of 5000 KRW.\n")
            return
        
        order = upbit.create_limit_buy_order(market, amount_to_buy, last_price)
        handle_order_result(order, "Buy")

    except ccxt.NetworkError as e:
        result_text.insert(tk.END, f"Network error: {e}\n")
    except ccxt.ExchangeError as e:
        result_text.insert(tk.END, f"Exchange error: {e}\n")
    except Exception as e:
        result_text.insert(tk.END, f"An unexpected error occurred: {e}\n")


def sell():
    try: 
        market = market_var.get() 
        amount_to_sell = float(amount_entry.get())

        ticker = upbit.fetch_ticker(market)
        last_price = ticker['close']

        order = upbit.create_market_sell_order(market, amount_to_sell)
        handle_order_result(order, "Sell")

    except ccxt.NetworkError as e:
        result_text.insert(tk.END, f"Network error: {e}\n")
    except ccxt.ExchangeError as e:
        result_text.insert(tk.END, f"Exchange error: {e}\n")
    except Exception as e:
        result_text.insert(tk.END, f"An unexpected error occurred: {e}\n")

def handle_order_result(order, order_type):
    if 'info' in order:
        result_text.insert(tk.END, f"{order_type} order successful: {order['info']}\n")
    else:
        result_text.insert(tk.END, f"Failed to create {order_type.lower()} order: {order}\n")

def display_total_balance(balance_info):
    total_krw_value = 0
    for currency, amount in balance_info['total'].items():
        if currency != 'KRW' and amount > 0:
            try:
                market_price = upbit.fetch_ticker(f'{currency}/KRW')['close']
                currency_krw_value = amount * market_price
                total_krw_value += currency_krw_value

                result_text.insert(tk.END, f"{currency}: {amount} {currency} (Market Price: {market_price} KRW) - Value: {currency_krw_value:.2f} KRW\n")
            except ccxt.NetworkError as e:
                handle_error(f"Network error while fetching data for {currency}: {e}\n")
            except ccxt.ExchangeError as e:
                handle_error(f"Exchange error while fetching data for {currency}: {e}\n")
            except Exception as e:
                handle_error(f"An error occurred for {currency}: {e}\n")

    update_balance_text(f"Total KRW Value: {total_krw_value:.2f} KRW\nCurrent KRW Balance: {balance_info['total']['KRW']:.2f} KRW")

def update_balance_text(text):
    balance_text.config(state=tk.NORMAL)
    balance_text.delete(1.0, tk.END)
    balance_text.insert(tk.END, text)
    balance_text.config(state=tk.DISABLED)

def handle_error(error_message):
    result_text.insert(tk.END, error_message)

# Trading strategy functions
def breakout_trading(symbol, timeframe='1h', breakout_percentage=1.0):
    breakout_percentage /= 100.0
    while True:
        try:
            candles = get_recent_candle(symbol, timeframe)

            support, resistance = calculate_support_resistance(candles)
            last_close = candles[-1][4]

            if last_close > resistance:
                print(f"Buy Signal: {symbol} Breakout Above Resistance ({last_close} > {resistance})")
                # Implement your buy order logic here

            elif last_close < support:
                print(f"Sell Signal: {symbol} Breakout Below Support ({last_close} < {support})")
                # Implement your sell order logic here
            time.sleep(60)

        except ccxt.NetworkError as e:
            print(f"Network error: {e}")
        except ccxt.ExchangeError as e:
            print(f"Exchange error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def get_all_trading_pairs():
    markets = upbit.fetch_markets()
    return [market['symbol'] for market in markets if market['active']]

def get_recent_candle(symbol, timeframe='1h', limit=10):
    candles = upbit.fetch_ohlcv(symbol, timeframe, limit=limit)
    return candles
def calculate_support_resistance(candles):
    closes = [candle[4] for candle in candles]
    support = min(closes)
    resistance = max(closes)
    return support, resistance

def choose_trading_pair(trading_pairs):
    return trading_pairs[0]

# GUI functions
def fetch_initial_balance():
    balance_thread = threading.Thread(target=update_balance)
    balance_thread.start()

def update_balance():
    try:
        while True:
            balance_info = upbit.fetch_balance()
            krw_balance = balance_info['total']['KRW']
            display_total_balance(balance_info)
            time.sleep(60)

    except Exception as e:
        update_balance_text(f"An error occurred while updating balance: {e}\n")
def start_breakout_trading(symbol):
    breakout_thread = threading.Thread(target=breakout_trading, args=(symbol,))
    breakout_thread.start()
    
def get_gui():
    global amount_entry, result_text, market_var, balance_text  # Declare the variables as global before using them
    result_text = None  # Add this line to declare result_text

    app = tk.Tk()
    app.title("Balance")

    total_balance_button = tk.Button(app, text="Total Balance", command=balance)
    total_balance_button.pack(side=tk.TOP, anchor=tk.N, pady=10)

    button_frame = tk.Frame(app)
    button_frame.pack(side=tk.TOP, pady=10)
    breakout_button_frame = tk.Frame(app)
    breakout_button_frame.pack(side=tk.TOP, pady=10)

    breakout_symbol_label = tk.Label(breakout_button_frame, text="Symbol for Breakout Trading:")
    breakout_symbol_label.pack(side=tk.LEFT, padx=10)

    breakout_symbols = get_all_trading_pairs()

    breakout_symbol_var = tk.StringVar(app)
    breakout_symbol_dropdown = ttk.Combobox(breakout_button_frame, textvariable=breakout_symbol_var, values=breakout_symbols)
    breakout_symbol_dropdown.pack(side=tk.LEFT, padx=10)
    breakout_symbol_dropdown.set(breakout_symbols[0])

    breakout_button = tk.Button(breakout_button_frame, text="Start Breakout Trading", command=lambda: start_breakout_trading(breakout_symbol_var.get()))
    breakout_button.pack(side=tk.LEFT, padx=10)

    amount_label = tk.Label(button_frame, text="Amount:")
    amount_label.pack(side=tk.LEFT, padx=10)
    amount_entry = tk.Entry(button_frame)
    amount_entry.pack(side=tk.LEFT, padx=10)

    market_label = tk.Label(button_frame, text="Market:")
    market_label.pack(side=tk.LEFT, padx=10)

    markets = [market['symbol'] for market in upbit.fetch_markets() if market['active']]

    market_var = tk.StringVar(app)
    
    market_var = tk.StringVar(app)
    market_dropdown = ttk.Combobox(button_frame, textvariable=market_var, values=markets)
    market_dropdown.pack(side=tk.LEFT, padx=10)
    market_dropdown.set(markets[0])

    buy_button = tk.Button(button_frame, text="Buy Currency", command=buy)
    buy_button.pack(side=tk.LEFT, padx=10)

    sell_button = tk.Button(button_frame, text="Sell Currency", command=sell)
    sell_button.pack(side=tk.LEFT, padx=10)

    result_text = scrolledtext.ScrolledText(app, width=80, height=20)
    result_text.pack(padx=100, pady=20)

    balance_text = tk.Text(app, height=2, state=tk.DISABLED)
    balance_text.pack(pady=10)

    fetch_initial_balance()
    app.mainloop()

if __name__ == "__main__":
    all_trading_pairs = get_all_trading_pairs()
    selected_symbol = choose_trading_pair(all_trading_pairs)
    breakout_thread = threading.Thread(target=breakout_trading, args=(selected_symbol,))
    breakout_thread.start()
    get_gui()