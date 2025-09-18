# api/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA = Path("../data/processed")  # relative path

@app.get("/api/forecast/price")
def get_price_forecast(crop: str = "tomato", market_id: str = "MAH_Pune", horizon: int = 30):
    path = DATA / f"forecast_{crop}_{market_id}_{horizon}d.csv"
    df = pd.read_csv(path, parse_dates=['date'])
    return {
        "crop": crop,
        "market_id": market_id,
        "dates": df['date'].dt.strftime('%Y-%m-%d').tolist(),
        "predicted": df['predicted'].round(2).tolist(),
        "lower": df['lower'].round(2).tolist(),
        "upper": df['upper'].round(2).tolist()
    }

@app.get("/api/risk/glut")
def get_glut_risk(crop: str = "tomato", market_id: str = "MAH_Pune", horizon: int = 30):
    hist = pd.read_csv(DATA/f'{crop}_{market_id}_features.csv', parse_dates=['date'])
    f = pd.read_csv(DATA/f'forecast_{crop}_{market_id}_{horizon}d.csv', parse_dates=['date'])
    
    hist_mean_30 = hist['price'].tail(30).mean()
    pred_mean_14 = f['predicted'].head(14).mean()
    
    signal = 'LOW'
    if pred_mean_14 < 0.8 * hist_mean_30:
        signal = 'HIGH'
    elif pred_mean_14 < 0.95 * hist_mean_30:
        signal = 'MEDIUM'
        
    return {
        "market": market_id,
        "crop": crop,
        "hist_mean_30": round(hist_mean_30, 2),
        "pred_mean_14": round(pred_mean_14, 2),
        "signal": signal,
        "advisory": f"Risk Level: {signal}. " + (
            "High risk of glut. Consider selling in alternative markets or using cold storage." if signal == 'HIGH'
            else "Moderate risk. Monitor prices closely." if signal == 'MEDIUM'
            else "Low risk. Normal market conditions expected."
        )
    }

# mount frontend as static
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")