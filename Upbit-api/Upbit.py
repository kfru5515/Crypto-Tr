import ccxt

Upbit = ccxt.Upbit()
markets = Upbit.load_market()

print(markets)