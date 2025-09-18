# Generate synthetic data for testing
import pandas as pd
import numpy as np
from pathlib import Path

RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)

# Generate price data
np.random.seed(42)
dates = pd.date_range('2024-01-01', periods=365)
base_price = 40
trend = np.linspace(0, 10, 365)  # Slight upward trend
seasonal = 10 * np.sin(2 * np.pi * np.arange(365) / 30)  # Monthly seasonality
noise = np.random.normal(0, 3, 365)
price = base_price + trend + seasonal + noise

# Create mandi prices CSV
df_mandi = pd.DataFrame({
    'date': dates,
    'market_id': 'MAH_Pune',
    'market_name': 'Pune',
    'commodity': 'tomato',
    'modal_price': np.maximum(price, 10)  # Ensure prices don't go below 10
})
df_mandi.to_csv(RAW/'mandi_prices.csv', index=False)
print("Created mandi_prices.csv")

# Generate weather data
temp_base = 25
temp_seasonal = 8 * np.sin(2 * np.pi * np.arange(365) / 365)  # Yearly seasonality
temp_noise = np.random.normal(0, 2, 365)

df_weather = pd.DataFrame({
    'date': dates,
    'precipitation': np.random.exponential(5, 365),  # Random rainfall
    'temp_max': temp_base + temp_seasonal + temp_noise + 5,
    'temp_min': temp_base + temp_seasonal + temp_noise - 5,
    'humidity': np.random.normal(70, 10, 365).clip(30, 100)  # Random humidity
})
df_weather.to_csv(RAW/'weather.csv', index=False)
print("Created weather.csv")

print("\nSynthetic data generated successfully!")
print(f"Location: {RAW.absolute()}")