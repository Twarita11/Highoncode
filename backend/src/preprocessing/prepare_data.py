import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
from src.utils.data_loader import load_data, save_data

def preprocess_data():
    # Load datasets
    crop_data = load_data("data/raw/Crop_recommendation.csv")
    price_data = load_data("data/raw/commodity_price.csv")
    rainfall_data = load_data("data/raw/district_wise_rainfall_normal.csv")
    
    # Clean and normalize state and district names
    price_data['State'] = price_data['State'].str.strip().str.upper()
    price_data['District'] = price_data['District'].str.strip().str.upper()
    rainfall_data['STATE_UT_NAME'] = rainfall_data['STATE_UT_NAME'].str.strip().str.upper()
    rainfall_data['DISTRICT'] = rainfall_data['DISTRICT'].str.strip().str.upper()
    
    # Merge price and rainfall data
    merged_data = pd.merge(
        price_data,
        rainfall_data[['STATE_UT_NAME', 'DISTRICT', 'ANNUAL']],
        left_on=['State', 'District'],
        right_on=['STATE_UT_NAME', 'DISTRICT'],
        how='left'
    )
    
    # Save processed data
    save_data(merged_data, "data/processed/processed_data.csv")
    
    return crop_data, merged_data

if __name__ == "__main__":
    preprocess_data()
