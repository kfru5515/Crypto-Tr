import ccxt
import config
import tkinter as tk
from tkinter import scrolledtext

#Api
upbit = ccxt.upbit({
    'enbaleRateLimit' : True,
    'apiKey': config.Ubpit_ApiKey,
    'secret': config.Ubpit_SecretKey,
})

def fetch_balance():
    balance = upbit.fetch_balance()
    krw_balance = balance['total']['KRW']

    # Clear previous content in the text widget
    result_text.delete(1.0, tk.END)

    # Display account balance in the text widget
    result_text.insert(tk.END, f"Current KRW Balance: {krw_balance} KRW\n\n")

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

    result_text.insert(tk.END, f"\nTotal Value of All Currencies in KRW: {total_krw_value:.2f} KRW")

def buy():
    try:
        market = 'BTC/KRW'  
        amount_to_buy = 0.001  

        order = upbit.create_market_buy_order(market, amount_to_buy)
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

def main():
    app = tk.Tk()
    app.title("Upbit Balance")

    fetch_button = tk.Button(app, text="Total Balance", command=fetch_balance)
    fetch_button.pack(pady=10)

    buy_button = tk.Button(app, text="Buy Currency", command=buy)
    buy_button.pack(pady=10)


    global result_text 
    result_text = scrolledtext.ScrolledText(app, width=80, height=20)
    result_text.pack(padx=100, pady=100)
    app.mainloop()
if __name__ == "__main__":
    main()