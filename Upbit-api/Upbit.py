import ccxt
import config
import os
import sys

upbit = ccxt.upbit({
    'enbaleRateLimit' : True,
    'apiKey': config.Ubpit_ApiKey,
    'secret': config.Ubpit_SecretKey,
})

balance = upbit.fetch_balance()

print("Account Balance:")
for currency, amount in balance['total'].items():
    print(f"{currency}: {amount}")
'''
markets = upbit.load_markets('KRW')
closed_orders = upbit.fetch_closed_orders('SHIB/KRW')
balance = upbit.fetch_balance()


print(closed_orders)
'''