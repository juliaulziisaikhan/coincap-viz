from coincap_api import CoinCapAPI
import pandas as pd

# Create an instance of CoinCapAPI
api = CoinCapAPI()

# Get assets using the instance
assets = api.get_assets(limit=100)

# Create dataframe
df = pd.DataFrame(assets)
df['changePercent24Hr'] = df['changePercent24Hr'].astype(float)
df['volumeUsd24Hr'] = df['volumeUsd24Hr'].astype(float)
df['marketCapUsd'] = df['marketCapUsd'].astype(float)

print('preview top 10 1st columns')
preview_columns = ['name', 'supply', 'maxSupply', 'marketCapUsd', 'volumeUsd24Hr']
preview_columns_2 = ['name', 'priceUsd', 'changePercent24Hr', 'vwap24Hr', 'explorer']
print('preview top 10 2nd columns')
print(df[preview_columns].head(10))
print(df[preview_columns_2].head(10))

market_summary_columns = ['symbol', 'name', 'changePercent24Hr', 'volumeUsd24Hr', 'marketCapUsd']
new_df = df[market_summary_columns]

print('gainers 24h')
gainers = new_df.nlargest(3, 'changePercent24Hr')
print(gainers)

print('losers 24h')
losers = new_df.nsmallest(3, 'changePercent24Hr')
print(losers)

print('top volume 24h')
volume_leaders = new_df.nlargest(3, 'volumeUsd24Hr')
print(volume_leaders)