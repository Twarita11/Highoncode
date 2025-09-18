# models/train_price.py
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pathlib import Path

PROC = Path("data/processed")
CROP = "tomato"
MARKET_ID = "MAH_Pune"
horizon = 30

df = pd.read_csv(PROC/f'{CROP}_{MARKET_ID}_features.csv', parse_dates=['date'])
df = df.set_index('date').sort_index()
y = df['price'].asfreq('D').fillna(method='ffill')

# quick SARIMAX (very small orders to be fast)
model = SARIMAX(y, order=(1,1,1), seasonal_order=(1,1,1,7), enforce_stationarity=False, enforce_invertibility=False)
res = model.fit(disp=False)
pred = res.get_forecast(steps=horizon)
pred_mean = pred.predicted_mean
ci = pred.conf_int(alpha=0.2)  # 80% PI

out = pd.DataFrame({
    'date': pred_mean.index,
    'predicted': pred_mean.values,
    'lower': ci.iloc[:,0].values,
    'upper': ci.iloc[:,1].values
})
out.to_csv(PROC/f'forecast_{CROP}_{MARKET_ID}_{horizon}d.csv', index=False)
print("Forecast saved:", out.shape)