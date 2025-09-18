# etl/prepare_data.py
import pandas as pd
from pathlib import Path
RAW = Path("data/raw")
PROC = Path("data/processed")
PROC.mkdir(parents=True, exist_ok=True)

# config
CROP = "tomato"
MARKET_ID = "MAH_Pune"  # change to match your market id string in CSV

# load price
prices = pd.read_csv(RAW/"mandi_prices.csv", parse_dates=['date'])
prices['commodity'] = prices['commodity'].str.lower()
prices = prices[prices['commodity'].str.contains(CROP)]
# unify market id naming: find a market string that matches
prices = prices.rename(columns={'modal_price':'price'})[['date','market_id','market_name','price']]

# optionally pick a single market for speed
prices = prices[prices['market_id']==MARKET_ID].sort_values('date').dropna(subset=['price'])
prices = prices.set_index('date').asfreq('D').fillna(method='ffill').reset_index()

# lag features
for lag in [1,7,14,30]:
    prices[f'price_lag_{lag}'] = prices['price'].shift(lag)

# rolling
prices['price_ma_7'] = prices['price'].rolling(7).mean()
prices['price_ma_30'] = prices['price'].rolling(30).mean()

# merge weather if available
try:
    weather = pd.read_csv(RAW/"weather.csv", parse_dates=['date'])
    weather = weather[['date','precipitation','temp_max','temp_min','humidity']]
    df = prices.merge(weather, on='date', how='left')
except FileNotFoundError:
    df = prices

# simple forward fill
df.fillna(method='ffill', inplace=True)
df.to_csv(PROC/f'{CROP}_{MARKET_ID}_features.csv', index=False)
print("Saved:", PROC/f'{CROP}_{MARKET_ID}_features.csv')