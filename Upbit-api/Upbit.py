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
    balance = upbit.fetch_balance()
    krw_balance = balance['total']['KRW']

    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Current KRW Balance: {krw_balance} KRW\n")

    # Total balance
    total_krw_value = 0
    for currency, amount in balance['total'].items():
        if currency != 'KRW' and amount > 0:
            try:
                market_price = upbit.fetch_ticker(f'{currency}/KRW')['close']
                currency_krw_value = amount * market_price
                total_krw_value += currency_krw_value

                result_text.insert(tk.END, f"{currency}: {amount} {currency} (Market Price: {market_price} KRW) - Value: {currency_krw_value:.2f} KRW\n")
            except ccxt.NetworkError as e:
                result_text.insert(tk.END, f"Network error while fetching data for {currency}: {e}\n")
            except ccxt.ExchangeError as e:
                result_text.insert(tk.END, f"Exchange error while fetching data for {currency}: {e}\n")
            except Exception as e:
                result_text.insert(tk.END, f"An error occurred for {currency}: {e}\n")


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
        if 'info' in order:
            result_text.insert(tk.END, f"Buy order successful: {order['info']}\n")
        else:
            result_text.insert(tk.END, f"Failed to create buy order: {order}\n")
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
        if 'info' in order:
            result_text.insert(tk.END, f"Sell order successful: {order['info']}\n")
        else:
            result_text.insert(tk.END, f"Failed to create sell order: {order}\n")
    except ccxt.NetworkError as e:
        result_text.insert(tk.END, f"Network error: {e}\n")
    except ccxt.ExchangeError as e:
        result_text.insert(tk.END, f"Exchange error: {e}\n")
    except Exception as e:
        result_text.insert(tk.END, f"An unexpected error occurred: {e}\n")

def update_balance():
    try:
        while True:
            balance = upbit.fetch_balance()
            krw_balance = balance['total']['KRW']


            # Display total balance
            total_krw_value = 0
            for currency, amount in balance['total'].items():
                if currency != 'KRW' and amount > 0:
                    try:
                        market_price = upbit.fetch_ticker(f'{currency}/KRW')['close']
                        currency_krw_value = amount * market_price
                        total_krw_value += currency_krw_value
                    except ccxt.NetworkError as e:
                        result_text.insert(tk.END, f"Network error while fetching data for {currency}: {e}\n")
                    except ccxt.ExchangeError as e:
                        result_text.insert(tk.END, f"Exchange error while fetching data for {currency}: {e}\n")
                    except Exception as e:
                        result_text.insert(tk.END, f"An error occurred for {currency}: {e}\n")

            update_balance_text(f"Total KRW Value: {total_krw_value:.2f}KRW\nCurrent KRW Balance: {krw_balance:.2f}KRW")
            # Update every minute
            time.sleep(60)
    except Exception as e:
        update_balance_text(f"An error occurred while updating balance: {e}\n")

def fetch_initial_balance():
    balance_thread = threading.Thread(target=update_balance)
    balance_thread.start()

def update_balance_text(text):
    balance_text.config(state=tk.NORMAL)
    balance_text.delete(1.0, tk.END)
    balance_text.insert(tk.END, text)
    balance_text.config(state=tk.DISABLED)

#GUI
def main():
    global amount_entry, result_text, market_var, balance_text  # Declare the variables as global before using them
    result_text = None  # Add this line to declare result_text

    app = tk.Tk()
    app.title("Balance")

    total_balance_button = tk.Button(app, text="Total Balance", command=balance)
    total_balance_button.pack(side=tk.TOP, anchor=tk.N, pady=10)



    button_frame = tk.Frame(app)
    button_frame.pack(side=tk.TOP, pady=10)

    amount_label = tk.Label(button_frame, text="Amount:")
    amount_label.pack(side=tk.LEFT, padx=10)
    amount_entry = tk.Entry(button_frame)
    amount_entry.pack(side=tk.LEFT, padx=10)

    market_label = tk.Label(button_frame, text="Market:")
    market_label.pack(side=tk.LEFT, padx=10)

    markets = [market['symbol'] for market in upbit.fetch_markets() if market['active']]

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

    # Text widget to display balance directly on the main page
    balance_text = tk.Text(app, height=2, state=tk.DISABLED)
    balance_text.pack(pady=10)

    fetch_initial_balance()
    app.mainloop()
if __name__ == "__main__":
    main()