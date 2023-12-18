import ccxt
import config

upbit = ccxt.upbit({
    'enbaleRateLimit' : True,
    'apiKey': config.Ubpit_ApiKey,
    'secret': config.Ubpit_SecretKey,
})
balance = upbit.fetch_balance()
krw_balance = balance['total']['KRW']

total_krw_value = 0

symbols = upbit.load_markets()
chosen_symbol = 'BTC/KRW' 

for symbol in symbols:
    print(symbol)

print("Available Trading Pairs on Upbit:")



print("Account Balance:")
print(f"Current KRW Balance: {krw_balance} KRW")


#total balance
for currency, amount in balance['total'].items():
    if currency != 'KRW' and amount > 0:
        try:
            market_price = upbit.fetch_ticker(f'{currency}/KRW')['close']

            currency_krw_value = amount * market_price

            total_krw_value += currency_krw_value

            print(f"{currency}: {amount} {currency} (Market Price: {market_price} KRW) - Value: {currency_krw_value:.2f} KRW")
        except ccxt.NetworkError as e:
            print(f"Network error while fetching data for {currency}/{chosen_symbol}: {e}")
        except ccxt.ExchangeError as e:
            print(f"Exchange error while fetching data for {currency}/{chosen_symbol}: {e}")
        except Exception as e:
            print(f"An error occurred for {currency}/{chosen_symbol}: {e}")
    print(f"\nTotal Value of All Currencies in KRW: {total_krw_value:.2f} KRW")

