# coincap-viz

### View the dashboard at https://coincap-viz-58c44f44475d.herokuapp.com/

## Main Dashboard
<img src="/main_page.png" alt="Home View" width="500">

The main dashboard visualizes weekly **crypto asset performance** through price changes, risk profiling, correlation analysis, and group comparisons, providing quick and easy-access insights on market trends.

## Momentum Analysis View
<img src="/momentum_analysis.png" alt="Home View" width="500">

The momentum analysis tracks the top assets' **price movements and momentum indicators**, highlighting overbought/oversold conditions and potential trend reversals over customizable periods.

### Tools
- Docker: containerizing the application and managing dependencies consistently across environments
- Streamlit: building app for data visualization
- CoinCap API: real-time crypto data without no API key. [Documentation](https://docs.coincap.io/)
- Heroku: deploying
- Python (pandas, numpy, plotly)

### Other ways to view the dashboard:

Run locally
```
streamlit run market_summary.py
```
or see at https://coincap-viz-bjejfqwxp3kxhemssyxr2k.streamlit.app/