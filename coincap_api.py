import requests
from datetime import datetime, timedelta  # Add this line
import sys
sys.path.append('..')

class CoinCapAPI:
    def __init__(self, base_url="https://api.coincap.io/v2"):
        self.base_url = base_url
        
    def get_assets(self, limit=100):
        """Get information about all cryptocurrencies"""
        endpoint = f"{self.base_url}/assets"
        response = requests.get(endpoint, params={"limit": limit})
        return response.json()["data"]
    
    def get_asset_history(self, asset_id, interval="d1", start=None, end=None):
        """Get historical data for a specific asset
        Intervals: m1, m5, m15, m30, h1, h2, h6, h12, d1
        """
        if not start:
            start = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
        if not end:
            end = int(datetime.now().timestamp() * 1000)
            
        endpoint = f"{self.base_url}/assets/{asset_id}/history"
        params = {
            "interval": interval,
            "start": start,
            "end": end
        }
        response = requests.get(endpoint, params=params)
        return response.json()["data"]
    
    def get_markets(self, asset_id=None, limit=100):
        """Get market data for all markets or a specific asset"""
        endpoint = f"{self.base_url}/markets"
        params = {"limit": limit}
        if asset_id:
            params["baseId"] = asset_id
        response = requests.get(endpoint, params=params)
        return response.json()["data"]
    
    def get_exchanges(self, limit=100):
        """Get information about exchanges"""
        endpoint = f"{self.base_url}/exchanges"
        response = requests.get(endpoint, params={"limit": limit})
        return response.json()["data"]
    
    def get_rates(self):
        """Get exchange rates for all supported fiat currencies"""
        endpoint = f"{self.base_url}/rates"
        response = requests.get(endpoint)
        return response.json()["data"]