import os
import pandas as pd
from datetime import datetime
from coincap_api import CoinCapAPI  # Save the previous code as coincap_api.py

def setup_data_directory():
    """Create directory structure for crypto data"""
    # Create base directory
    base_dir = "crypto_data"
    raw_dir = os.path.join(base_dir, "raw")
    
    # Create directories if they don't exist
    for dir_path in [base_dir, raw_dir]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    
    return raw_dir

def fetch_and_save_preview_data():
    """Fetch 1000 rows of data from each endpoint and save to CSVs"""
    api = CoinCapAPI()
    raw_dir = setup_data_directory()
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Fetch and save assets data
    assets = api.get_assets(limit=1000)
    assets_df = pd.DataFrame(assets)
    assets_df.to_csv(os.path.join(raw_dir, f'assets_{timestamp}.csv'), index=False)
    
    # Fetch and save markets data
    markets = api.get_markets(limit=1000)
    markets_df = pd.DataFrame(markets)
    markets_df.to_csv(os.path.join(raw_dir, f'markets_{timestamp}.csv'), index=False)
    
    # Fetch and save exchanges data
    exchanges = api.get_exchanges(limit=1000)
    exchanges_df = pd.DataFrame(exchanges)
    exchanges_df.to_csv(os.path.join(raw_dir, f'exchanges_{timestamp}.csv'), index=False)
    
    # Fetch and save rates data
    rates = api.get_rates()
    rates_df = pd.DataFrame(rates)
    rates_df.to_csv(os.path.join(raw_dir, f'rates_{timestamp}.csv'), index=False)
    
    # Fetch historical data for Bitcoin as an example
    btc_history = api.get_asset_history('bitcoin', interval='h1')
    history_df = pd.DataFrame(btc_history)
    history_df.to_csv(os.path.join(raw_dir, f'bitcoin_history_{timestamp}.csv'), index=False)
    
    print(f"Data files saved in {raw_dir}/")
    return {
        'assets': assets_df,
        'markets': markets_df,
        'exchanges': exchanges_df,
        'rates': rates_df,
        'btc_history': history_df
    }

if __name__ == "__main__":
    dfs = fetch_and_save_preview_data()
    
    # Print preview of each dataset
    for name, df in dfs.items():
        print(f"\n=== Preview of {name} dataset ===")
        print(f"Shape: {df.shape}")
        print("\nFirst few rows:")
        print(df.head())
        print("\nColumns:")
        print(df.columns.tolist())