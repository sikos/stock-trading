import config as cf
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
import matplotlib.pyplot as plt
import numpy as np

# Base URL for fetching data, portfolio, etc. from Alpaca
BASE_URL = "https://paper-api.alpaca.markets"

# Create REST API connection
api = tradeapi.REST(key_id=cf.ALPACA_API_KEY,
                    secret_key=cf.ALPACA_SECRET_KEY, base_url=BASE_URL, api_version='v2')

STOCKNAME='AAPL'

# Fetch Apple data from last 20 days
STOCK_DATA = api.get_bars(STOCKNAME, TimeFrame.Day, "2022-01-01", "2022-03-28", limit=100).df

# Reformat data (drop multiindex, rename columns, reset index)
STOCK_DATA.columns = STOCK_DATA.columns.to_flat_index()
STOCK_DATA.reset_index(inplace=True)

# Calculate moving averages
STOCK_DATA['20_SMA'] = STOCK_DATA['close'].rolling(window=20, min_periods=1).mean()
STOCK_DATA['10_SMA'] = STOCK_DATA['close'].rolling(window=10, min_periods=1).mean()

# Find crossover points
STOCK_DATA['Cross'] = 0.0
STOCK_DATA['Cross'] = np.where(STOCK_DATA['10_SMA'] > STOCK_DATA['20_SMA'], 1.0, 0.0)
STOCK_DATA['Signal'] = STOCK_DATA['Cross'].diff()

# Map numbers to words
map_dict = {-1.0: 'sell', 1.0: 'buy', 0.0: 'none'}
STOCK_DATA["Signal"] = STOCK_DATA["Signal"].map(map_dict)

# Preview Data
# print(STOCK_DATA.head())

# Show Relevant Buy/Sell data
# print(STOCK_DATA[STOCK_DATA['Signal'] != 'none'].dropna())


# Plot stock price data
STOCK_DATA.plot(x="timestamp", y=["close", "20_SMA", "10_SMA"], color=['k', 'b', 'm'])

# Plot ‘buy’ signals
plt.plot(STOCK_DATA[STOCK_DATA['Signal'] == 'buy']['timestamp'],
         STOCK_DATA['20_SMA'][STOCK_DATA['Signal'] == 'buy'],
         '^', markersize=8, color='g', label='buy')


print(STOCK_DATA[STOCK_DATA['Signal'] == 'buy']['timestamp'])

# # Plot ‘sell’ signals
plt.plot(STOCK_DATA[STOCK_DATA['Signal'] == 'sell']['timestamp'],
         STOCK_DATA['20_SMA'][STOCK_DATA['Signal'] == 'sell'],
         'v', markersize=8, color='r', label='sell')

plt.xlabel("Date")
plt.ylabel(STOCKNAME+" Close Price ($)")
plt.title(STOCKNAME)
plt.legend()
plt.show()
