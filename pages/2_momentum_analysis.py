import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from coincap_api import CoinCapAPI
import sys
sys.path.append('../..')  # Go up two levels to reach main directory

def calculate_momentum(prices, window=24):
    """calculate momentum similar to relative strength index"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def create_momentum_page():
    st.title("Price Momentum Analysis")
    
    # Initialize API
    api = CoinCapAPI()
    
    # Sidebar controls
    st.sidebar.header("Configuration")
    
    asset_options = {
        "Bitcoin (BTC)": "bitcoin",
        "Ethereum (ETH)": "ethereum", 
        "Binance Coin (BNB)": "binance-coin",
        "Solana (SOL)": "solana",
        "Cardano (ADA)": "cardano",
        "Ripple (XRP)": "ripple",
        "Polkadot (DOT)": "polkadot",
        "Dogecoin (DOGE)": "dogecoin"
    }
    
    selected_asset = st.sidebar.selectbox(
        "Select Asset",
        list(asset_options.keys())
    )
    
    # Get the corresponding asset ID for the selected option
    selected_asset_id = asset_options[selected_asset]
    
    lookback_days = st.sidebar.slider(
        "Lookback Period (days)", 
        min_value=7,
        max_value=30,
        value=21
    )
    
    window = st.sidebar.slider(
        "Momentum Window (hours)",
        min_value=6,
        max_value=72,
        value=24
    )
    
    try:
        # Fix timestamp calculation
        end_time = int(datetime.now().timestamp() * 1000)
        start_time = int((datetime.now() - timedelta(days=lookback_days)).timestamp() * 1000)
        
        # Get historical data
        history = api.get_asset_history(
            selected_asset_id,
            interval='h1',
            start=start_time,
            end=end_time
        )
    
        # Process data
        df = pd.DataFrame(history)
        df['time'] = pd.to_datetime(df['time'].astype(int), unit='ms')
        df['priceUsd'] = df['priceUsd'].astype(float)
        
        # Calculate momentum
        df['momentum'] = calculate_momentum(df['priceUsd'], window=window)
        
        # Create figure
        fig = go.Figure()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['priceUsd'],
            name='Price',
            line=dict(color='blue'),
            yaxis='y'
        ))
        
        # Add momentum line  
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df['momentum'],
            name='Momentum',
            line=dict(color='red'),
            yaxis='y2'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'{selected_asset} Price and Momentum Analysis',
            yaxis=dict(
                title='Price (USD)',
                tickformat='$,.2f'
            ),
            yaxis2=dict(
                title='Momentum',
                overlaying='y',
                side='right',
                range=[0, 100] 
            ),
            hovermode='x unified',
            height=600
        )
        
        # Display figure
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        with st.expander("Understanding Momentum"):
            st.write("""
            The momentum indicator can identify potential trend reversals.
            - Values above 70 may indicate overbought conditions
            - Values below 30 may indicate oversold conditions
            - Crossing the 50 line may signal changes in trend
            """)
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")

if __name__ == "__main__":
    create_momentum_page()