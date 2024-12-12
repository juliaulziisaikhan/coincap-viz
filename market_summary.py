from config import load_config
import streamlit as st
from app import EnhancedCryptoVisualizer

st.set_page_config(layout="wide")

config = load_config('config.yaml')
st.title(config['main_page']['dashboard']['title'])

# initialize
visualizer = EnhancedCryptoVisualizer()

# part 1
# market metrics summary
visualizer.create_market_metrics()
st.empty()

# part 2
# 2x2 visualizations
st.subheader(config['second_part']['dashboard']['title'])
viz2 = config['top_asset_performance']['dashboard']['title']
viz1 = config['asset_risk_profile']['dashboard']['title']
viz3 = config['price_correlation_matrix']['dashboard']['title']
viz4 = config['asset_group_performance']['dashboard']['title']


with st.container():
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        with st.spinner(f"Generating {viz2}..."):
            fig1 = visualizer.create_top_asset_performance()
        st.plotly_chart(fig1, use_container_width=True)
    with row1_col2:
        with st.spinner(f"Generating {viz1}..."):
            fig2 = visualizer.create_asset_risk_profile()
        st.plotly_chart(fig2, use_container_width=True)
    
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        with st.spinner(f"Generating {viz3}..."):
            fig3 = visualizer.create_price_correlation_matrix()
        st.plotly_chart(fig3, use_container_width=True)
    with row2_col2:
        with st.spinner(f"Generating {viz4}..."):
            fig4 = visualizer.create_asset_group_performance()
        st.plotly_chart(fig4, use_container_width=True)