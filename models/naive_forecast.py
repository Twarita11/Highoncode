# models/naive_forecast.py
import pandas as pd
from pathlib import Path

PROC = Path("data/processed")
CROP = "tomato"
MARKET_ID = "MAH_Pune"
horizon = 30

df = pd.read_csv(PROC/f'{CROP}_{MARKET_ID}_features.csv', parse_dates=['date']).set_index('date')
last_ma = df['price'].rolling(7).mean().iloc[-1]
dates = pd.date_range(df.index.max()+pd.Timedelta(days=1), periods=horizon)
out = pd.DataFrame({'date': dates, 'predicted': [last_ma]*horizon})
out['lower'] = out['predicted']*0.9
out['upper'] = out['predicted']*1.1
out.to_csv(PROC/f'forecast_{CROP}_{MARKET_ID}_{horizon}d.csv', index=False)
print("Naive forecast saved:", out.shape)