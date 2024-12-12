import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
from constants import CONSTANTS
from coincap_api import CoinCapAPI
import requests
sys.path.append('..')

class EnhancedCryptoVisualizer:
    def __init__(self):
        self.api = CoinCapAPI()
        
    def get_market_metrics(self):
        """calc market metrics"""
        assets = self.api.get_assets(limit=CONSTANTS['market_metrics']['calcs']['limit'])
        df = pd.DataFrame(assets)
        df['changePercent24Hr'] = df['changePercent24Hr'].astype(float)
        df['volumeUsd24Hr'] = df['volumeUsd24Hr'].astype(float)
        
        gainers = df.nlargest(3, 'changePercent24Hr')[['name', 'symbol', 'changePercent24Hr']]
        losers = df.nsmallest(3, 'changePercent24Hr')[['name', 'symbol', 'changePercent24Hr']]
        volume_leaders = df.nlargest(3, 'volumeUsd24Hr')[['name', 'symbol', 'volumeUsd24Hr']]
        
        return gainers, losers, volume_leaders
    
    def create_market_metrics(self):
        """viz market metrics"""
        st.subheader(CONSTANTS['market_metrics']['dashboard']['title'])
        gainers, losers, volume_leaders = self.get_market_metrics()
        
        # 3x3 viz
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader(CONSTANTS['market_metrics']['dashboard']['gainers_title'])
            for _, row in gainers.iterrows():
                st.metric(f"{row['name']} ({row['symbol']})", f"{row['changePercent24Hr']:.2f}%")
        
        with col2:
            st.subheader(CONSTANTS['market_metrics']['dashboard']['losers_title'])
            for _, row in losers.iterrows():
                st.metric(f"{row['name']} ({row['symbol']})", f"{row['changePercent24Hr']:.2f}%")
        
        with col3:
            st.subheader(CONSTANTS['market_metrics']['dashboard']['volume_leaders_title'])
            for _, row in volume_leaders.iterrows():
                st.metric(f"{row['name']} ({row['symbol']})", f"${row['volumeUsd24Hr']:,.0f}")

    def get_volatility(self, history_data):
        """calc volatility from history endpoint"""
        prices = pd.Series([float(d['priceUsd']) for d in history_data])
        return np.std(prices.pct_change().dropna()) * 100
        
    def create_asset_risk_profile(self):
        """viz asset risk profile"""
        # only look at top 20 assets
        assets = self.api.get_assets(limit=20)
        lookback_d = CONSTANTS['asset_risk_profile']['calcs']['lookback_d']
        interval_h = CONSTANTS['asset_risk_profile']['calcs']['interval']
        
        # calc volatility for each asset
        volatilities = []
        market_caps = []
        volumes = []
        names = []
        changes = []
        
        for asset in assets:
            history = self.api.get_asset_history(
                asset['id'],
                interval=interval_h,
                start=int((datetime.now() - timedelta(days=lookback_d)).timestamp() * 1000)
            )
            
            volatilities.append(self.get_volatility(history))
            market_caps.append(float(asset['marketCapUsd']))
            volumes.append(float(asset['volumeUsd24Hr']))
            names.append(asset['name'])
            changes.append(float(asset['changePercent24Hr']))
        
        # Create DataFrame
        df = pd.DataFrame({
            'Asset': names,
            'Market Cap': market_caps,
            'Volatility': volatilities,
            'Volume': volumes,
            '24h Change': changes
        })
        
        # Create visualization
        fig = px.scatter(
            df,
            x='Market Cap',
            y='Volatility',
            size='Volume',
            color='24h Change',
            hover_name='Asset',
            log_x=True,
            title=CONSTANTS['asset_risk_profile']['dashboard']['title']
        )
        
        fig.update_layout(
            xaxis_title="Market Cap (USD, log scale)",
            yaxis_title="Volatility (%)",
            coloraxis_colorbar_title="24h Change (%)"
        )
        
        return fig
    
    def create_top_asset_performance(self, top_n=5):
        """viz multi-asset price movement"""
        # Get top N assets
        assets = self.api.get_assets(limit=top_n)
        lookback_d = CONSTANTS['top_asset_performance']['calcs']['lookback_d']
        interval_h = CONSTANTS['top_asset_performance']['calcs']['interval']
        
        # Get historical data for each asset
        fig = go.Figure()
        
        for asset in assets:
            history = self.api.get_asset_history(
                asset['id'],
                interval=interval_h,
                start=int((datetime.now() - timedelta(days=lookback_d)).timestamp() * 1000)
            )
            
            prices = [float(d['priceUsd']) for d in history]
            timestamps = [datetime.fromtimestamp(int(d['time'])/1000) for d in history]
            
            # Normalize prices to percentage change from start
            base_price = prices[0]
            normalized_prices = [(p - base_price) / base_price * 100 for p in prices]
            
            fig.add_trace(go.Scatter(
                x=timestamps,
                y=normalized_prices,
                name=asset['name'],
                hovertemplate=
                "<b>%{x}</b><br>" +
                "Change: %{y:.2f}%<br>" +
                "<extra></extra>"
            ))
        
        fig.update_layout(
            title=CONSTANTS['top_asset_performance']['dashboard']['title'],
            xaxis_title='Date',
            yaxis_title='Price Change (%)',
            hovermode='x unified'
        )
        
        return fig
    
    def create_price_correlation_matrix(self, top_n=10):
        """Create price correlation matrix for top assets"""
        assets = self.api.get_assets(limit=top_n)
        lookback_d = CONSTANTS['price_correlation_matrix']['calcs']['lookback_d']
        interval_h = CONSTANTS['price_correlation_matrix']['calcs']['interval']
        price_data = {}
        
        # Collect historical prices for each asset
        for asset in assets:
            history = self.api.get_asset_history(
                asset['id'],
                interval=interval_h,
                start=int((datetime.now() - timedelta(days=lookback_d)).timestamp() * 1000)
            )
            prices = [float(d['priceUsd']) for d in history]
            price_data[asset['name']] = prices
        
        # Create correlation matrix
        df = pd.DataFrame(price_data)
        corr_matrix = df.corr()
        
        # Create heatmap
        fig = px.imshow(
            corr_matrix,
            title=CONSTANTS['price_correlation_matrix']['dashboard']['title'],
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        return fig
    
    def create_asset_group_performance(self):
        """Create performance comparison by asset groups"""
        # Define asset groups (you could make this dynamic/configurable)
        groups = {
            'Meme Coins': ['dogecoin', 'shiba-inu'],
            'DeFi': ['uniswap', 'aave', 'maker'],
            'Layer 1': ['bitcoin', 'ethereum', 'solana'],
            'Exchange Tokens': ['binance-coin', 'ftx-token']
        }
        lookback_d = CONSTANTS['asset_group_performance']['calcs']['lookback_d']
        interval_h = CONSTANTS['asset_group_performance']['calcs']['interval']
        fig = go.Figure()
        
        for group_name, assets in groups.items():
            performances = []
            for asset_id in assets:
                try:
                    history = self.api.get_asset_history(
                        asset_id,
                        interval=interval_h,
                        start=int((datetime.now() - timedelta(days=lookback_d)).timestamp() * 1000)
                    )
                    
                    prices = [float(d['priceUsd']) for d in history]
                    perf = [(p - prices[0]) / prices[0] * 100 for p in prices]
                    performances.append(perf)
                except:
                    continue
            
            if performances:
                # Average performance for the group
                avg_perf = np.mean(performances, axis=0)
                timestamps = [datetime.fromtimestamp(int(d['time'])/1000) for d in history]
                
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=avg_perf,
                    name=group_name,
                    hovertemplate=
                    "<b>%{x}</b><br>" +
                    "Change: %{y:.2f}%<br>" +
                    "<extra></extra>"
                ))
        
        fig.update_layout(
            title=CONSTANTS['asset_group_performance']['dashboard']['title'],
            xaxis_title='Date',
            yaxis_title='Average Price Change (%)',
            hovermode='x unified'
        )
        
        return fig