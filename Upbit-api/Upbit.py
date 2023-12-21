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

# Constants for breakout strategy
BREAKOUT_PERIODS = 20
def balance():
    balance_info = upbit.fetch_balance()
    krw_balance = balance_info['total']['KRW']

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Current KRW Balance: {krw_balance} KRW\n")

    # Display total balance
    display_total_balance(balance_info)

def check_breakout_conditions(market):
    try:
        # Fetch OHLCV (Open, High, Low, Close, Volume) data for the specified market
        ohlcv = upbit.fetch_ohlcv(market, timeframe='1h', limit=BREAKOUT_PERIODS)

        # Extract high and low prices from the last 'n' periods
        high_prices = ohlcv[:, 2]  # High prices are in the third column
        low_prices = ohlcv[:, 3]   # Low prices are in the fourth column

        # Calculate highest high and lowest low
        highest_high = max(high_prices)
        lowest_low = min(low_prices)

        # Fetch the current ticker for the market
        ticker = upbit.fetch_ticker(market)
        current_price = ticker['close']

        # Check breakout conditions
        if current_price > highest_high:
            return 'buy'
        elif current_price < lowest_low:
            return 'sell'
        else:
            return None

    except ccxt.NetworkError as e:
        handle_error(f"Network error while checking breakout conditions: {e}\n")
        return None
    except ccxt.ExchangeError as e:
        handle_error(f"Exchange error while checking breakout conditions: {e}\n")
        return None
    except Exception as e:
        handle_error(f"An error occurred while checking breakout conditions: {e}\n")
        return None
    
    
def auto_execute_breakout_strategy():
    while True:
        try:
            market = market_var.get()

            # Check breakout conditions
            breakout_signal = check_breakout_conditions(market)

            if breakout_signal == 'buy':
                # Implement buy logic here
                auto_buy()
            elif breakout_signal == 'sell':
                # Implement sell logic here if needed
                auto_sell()

            # Sleep for a period before checking breakout conditions again
            time.sleep(60)

        except ccxt.NetworkError as e:
            handle_error(f"Network error: {e}\n")
        except ccxt.ExchangeError as e:
            handle_error(f"Exchange error: {e}\n")
        except Exception as e:
            handle_error(f"An unexpected error occurred: {e}\n")

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

def auto_buy():
    try:
        market = market_var.get()

        balance_info = upbit.fetch_balance()
        available_krw_balance = balance_info['total']['KRW']

        ticker = upbit.fetch_ticker(market)
        last_price = ticker['close']

        amount_to_buy = available_krw_balance / last_price

        breakout_signal = check_breakout_conditions(market)
        if breakout_signal == 'buy':
            order = upbit.create_limit_buy_order(market, amount_to_buy, last_price)
            handle_order_result(order, "Auto Buy")

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
def auto_sell():
    try:
        market = market_var.get()

        base_currency = market.split('/')[0]

        balance_info = upbit.fetch_balance()
        if base_currency not in balance_info['total']:
            result_text.insert(tk.END, f"Error: Balance information for {base_currency} not available.\n")
            return
        currency_balance = balance_info['total'][base_currency]
        
        ticker = upbit.fetch_ticker(market)
        last_price = ticker['close']
        breakout_signal = check_breakout_conditions(market)
        if breakout_signal == 'sell' and currency_balance > 0:
            order = upbit.create_market_sell_order(market, currency_balance)
            handle_order_result(order, "Auto Sell")

        # Place a market sell order if the current price breaks below the lowest low
        breakout_signal = check_breakout_conditions(market)
        if breakout_signal == 'sell' and currency_balance > 0:
            order = upbit.create_market_sell_order(market, currency_balance)
            handle_order_result(order, "Auto Sell")


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

def auto_buy_sell():
    auto_buy()
    auto_sell()

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
    #button for auto buy and sell
    start_auto_execute_button = tk.Button(app, text="Start Auto Execute", command=lambda: threading.Thread(target=auto_execute_breakout_strategy).start())
    start_auto_execute_button.pack(side=tk.TOP, anchor=tk.N, pady=10)

    manual_auto_execute_button = tk.Button(app, text="Auto Buy/Sell", command=auto_buy_sell)
    manual_auto_execute_button.pack(side=tk.TOP, anchor=tk.N, pady=10)

    fetch_initial_balance()
    app.mainloop()

if __name__ == "__main__":
    get_gui()