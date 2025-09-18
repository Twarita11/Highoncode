# models/glut_signal.py
import pandas as pd
from pathlib import Path

PROC = Path("data/processed")
CROP = "tomato"
MARKET_ID = "MAH_Pune"
horizon = 30

hist = pd.read_csv(PROC/f'{CROP}_{MARKET_ID}_features.csv', parse_dates=['date'])
f = pd.read_csv(PROC/f'forecast_{CROP}_{MARKET_ID}_{horizon}d.csv', parse_dates=['date'])

hist_mean_30 = hist['price'].tail(30).mean()
pred_mean_14 = f['predicted'].head(14).mean()

signal = 'LOW'
if pred_mean_14 < 0.8 * hist_mean_30:
    signal = 'HIGH'
elif pred_mean_14 < 0.95 * hist_mean_30:
    signal = 'MEDIUM'

out = {
    'market': MARKET_ID, 
    'crop': CROP, 
    'hist_mean_30': hist_mean_30, 
    'pred_mean_14': pred_mean_14, 
    'signal': signal,
    'advisory': f"Risk Level: {signal}. " + (
        "High risk of glut. Consider selling in alternative markets or using cold storage." if signal == 'HIGH'
        else "Moderate risk. Monitor prices closely." if signal == 'MEDIUM'
        else "Low risk. Normal market conditions expected."
    )
}
print(out)