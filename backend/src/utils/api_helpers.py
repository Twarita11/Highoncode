import pandas as pd
import requests
from functools import lru_cache
from datetime import datetime
import os

@lru_cache(maxsize=1)
def load_crop_calendar() -> pd.DataFrame:
    """Load static crop calendar CSV."""
    csv_path = "data/raw/india_crop_calendar.csv"  # Place your CSV here
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    else:
        # Fallback empty DF
        return pd.DataFrame(columns=['Crop', 'Harvest Months'])

@lru_cache(maxsize=128)
def fetch_production_data(state: str, crop: str, api_key: str) -> list:
    """Fetch/filter low-production districts from data.gov.in."""
    url = "https://api.data.gov.in/resource/3ef66c13-6ab7-4ba9-9b0e-34e281b8f98d"
    params = {
        'api-key': api_key,
        'format': 'json',
        'limit': 1000,
        'filters': f'state:{state};crop:{crop.lower()}'
    }
    try:
        resp = requests.get(url, params=params)
        data = resp.json().get('records', [])
        df = pd.DataFrame(data)
        if not df.empty:
            df['production_tonnes'] = pd.to_numeric(df.get('production', 0), errors='coerce')
            median_prod = df['production_tonnes'].median()
            low_prod = df[df['production_tonnes'] < median_prod].head(5).to_dict('records')
            return [{'district': r['district_name'], 'production_tonnes': r['production_tonnes'], 'potential_profit': 'High (low supply)'} for r in low_prod]
    except Exception:
        pass
    return []  # Fallback

def get_harvest_window(crop: str, current_date: datetime, calendar_df: pd.DataFrame) -> dict:
    """Get optimal selling time from calendar."""
    row = calendar_df[calendar_df['Crop'].str.contains(crop, case=False, na=False)]
    if not row.empty:
        harvest_months = row.iloc[0]['Harvest Months'].lower()
        current_month = current_date.strftime('%b').lower()
        if current_month in harvest_months.replace('-', ' ').split():
            return {
                'optimal_window': row.iloc[0]['Harvest Months'],
                'suggested_date': 'Within 1 month (harvest season now)',
                'reason': 'Post-harvest peak prices; sell to avoid storage losses'
            }
        else:
            return {
                'optimal_window': row.iloc[0]['Harvest Months'],
                'suggested_date': 'In 2-3 months',
                'reason': f'Prepare for {row.iloc[0]["Harvest Months"]} harvest'
            }
    return {'optimal_window': 'Sep-Oct (Kharif)', 'suggested_date': 'Soon', 'reason': 'General tropical crop advice'}
