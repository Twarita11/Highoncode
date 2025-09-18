import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from typing import Dict, Any, Optional, Tuple, List  # Added List import
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Global data_manager reference (we'll create this in utils)
try:
    from src.utils.data_loader import data_manager
except ImportError:
    # Fallback for standalone usage
    class DummyDataManager:
        def load_data(self, path):
            return pd.read_csv(path)
    data_manager = DummyDataManager()

class EnhancedCropPriceModel:
    def __init__(self):
        self.model = None
        self.crop_data = None
        self.label_encoder = LabelEncoder()
        self.feature_means = {}
        self.feature_ranges = {}
        
    def train_crop_model(self, crop_data_path: str):
        """Train RandomForestClassifier for crop recommendation with feature analysis."""
        self.crop_data = data_manager.load_data(crop_data_path)
        
        # Encode labels
        y_encoded = self.label_encoder.fit_transform(self.crop_data['label'])
        
        # Store feature statistics for better predictions
        features = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
        self.feature_means = self.crop_data[features].mean().to_dict()
        self.feature_ranges = self.crop_data[features].agg(['min', 'max']).to_dict()
        
        # Train model
        X = self.crop_data[features]
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y_encoded)
        
        print(f"Model trained on {len(self.crop_data)} samples")
        print(f"Available crops: {list(self.label_encoder.classes_)}")
    
    def _generate_environmental_conditions(self, rainfall: float) -> np.ndarray:
        """Generate realistic environmental conditions based on rainfall patterns."""
        conditions = []
        
        # Base conditions from averages
        base_conditions = [
            self.feature_means['N'],
            self.feature_means['P'], 
            self.feature_means['K'],
            self.feature_means['temperature'],
            self.feature_means['humidity'],
            self.feature_means['ph'],
            rainfall
        ]
        
        # Adjust based on rainfall patterns (simple heuristic)
        if rainfall > 1000:  # High rainfall areas
            conditions.extend([
                base_conditions[0] * 1.1,  # Slightly higher N
                base_conditions[1] * 0.9,  # Lower P
                base_conditions[2] * 1.05, # Slightly higher K
                base_conditions[3] - 2,    # Cooler temperature
                base_conditions[4] * 1.15, # Higher humidity
                base_conditions[5],        # Same pH
                rainfall
            ])
        else:  # Low rainfall areas
            conditions.extend([
                base_conditions[0] * 0.95,
                base_conditions[1] * 1.1,
                base_conditions[2] * 0.95,
                base_conditions[3] + 1,
                base_conditions[4] * 0.85,
                base_conditions[5] + 0.2,
                rainfall
            ])
            
        return np.array([conditions])
    
    def _forecast_prices(self, price_data: pd.DataFrame, crop: str, 
                        lookback_days: int = 90) -> Optional[Dict[str, Any]]:
        """Enhanced price forecasting with crop-specific filtering."""
        if price_data.empty:
            return None
            
        # Filter by crop if available (assuming crop name in data)
        # You might need to adjust column names based on your actual data
        if 'Commodity' in price_data.columns:
            crop_filtered = price_data[
                price_data['Commodity'].str.contains(crop, case=False, na=False)
            ]
        else:
            crop_filtered = price_data.copy()
        
        if crop_filtered.empty:
            # Fallback to all commodities
            crop_filtered = price_data.copy()
        
        # Convert date column for proper sorting
        if 'Arrival_Date' in crop_filtered.columns:
            try:
                crop_filtered['Arrival_Date'] = pd.to_datetime(crop_filtered['Arrival_Date'])
                crop_filtered = crop_filtered.sort_values('Arrival_Date')
                
                # Filter recent data
                cutoff_date = datetime.now() - timedelta(days=lookback_days)
                recent_data = crop_filtered[crop_filtered['Arrival_Date'] >= cutoff_date]
                
                if recent_data.empty:
                    return None
                
                # Calculate weighted moving average (recent prices weighted more)
                recent_data = recent_data.copy()
                price_col = 'Modal_x0020_Price' if 'Modal_x0020_Price' in recent_data.columns else 'Price'
                
                if price_col in recent_data.columns:
                    recent_data['Price'] = recent_data[price_col].fillna(
                        recent_data[price_col].mean()
                    )
                    
                    # Simple exponential moving average
                    recent_data['EMA'] = recent_data['Price'].ewm(span=5).mean()
                    
                    # Find best market conditions
                    best_idx = recent_data['EMA'].idxmax()
                    best_record = recent_data.loc[best_idx]
                    
                    return {
                        'market': best_record.get('Market', 'Unknown'),
                        'selling_date': best_record.get('Arrival_Date', 'Unknown').strftime('%Y-%m-%d'),
                        'predicted_price': float(best_record['EMA']),
                        'historical_price': float(best_record['Price']),
                        'confidence': self._calculate_price_confidence(recent_data)
                    }
            except Exception as e:
                print(f"Date parsing error: {e}")
                return None
        
        return None
    
    def _calculate_price_confidence(self, data: pd.DataFrame) -> float:
        """Calculate confidence score based on price stability."""
        if len(data) < 3:
            return 0.5
        
        if 'Price' not in data.columns:
            return 0.5
            
        price_std = data['Price'].std()
        price_mean = data['Price'].mean()
        
        if price_mean == 0 or pd.isna(price_mean):
            return 0.0
            
        cv = price_std / price_mean  # Coefficient of variation
        return max(0.1, min(0.9, 1 - cv))  # Scale to 0.1-0.9
    
    def recommend_crop(self, state: str, district: str, 
                      price_data: pd.DataFrame, rainfall_data: pd.DataFrame) -> Dict[str, Any]:
        """Enhanced crop recommendation with better environmental modeling."""
        # Normalize inputs
        state = state.strip().upper()
        district = district.strip().upper()
        
        # Get rainfall data
        rainfall_match = rainfall_data[
            (rainfall_data['STATE_UT_NAME'] == state) & 
            (rainfall_data['DISTRICT'] == district)
        ]
        
        if rainfall_match.empty:
            return {
                "error": f"No rainfall data available for {state}, {district}",
                "suggestions": self._get_alternative_locations(rainfall_data, state, district)
            }
        
        avg_rainfall = rainfall_match['ANNUAL'].mean()
        
        # Generate environmental conditions
        input_features = self._generate_environmental_conditions(avg_rainfall)
        
        # Predict crop
        crop_encoded = self.model.predict(input_features)[0]
        crop = self.label_encoder.inverse_transform([crop_encoded])[0]
        
        # Get prediction probabilities
        probabilities = self.model.predict_proba(input_features)[0]
        confidence = float(np.max(probabilities))
        
        # Forecast prices
        price_forecast = self._forecast_prices(price_data, crop)
        
        return {
            "success": True,
            "recommendation": {
                "crop": crop,
                "confidence": round(confidence, 3),
                "environmental_conditions": {
                    "state": state,
                    "district": district,
                    "annual_rainfall_mm": round(avg_rainfall, 1),
                    "n_pk_ratio": round(input_features[0][0:3].sum() / 3, 1),
                    "temperature_c": round(input_features[0][3], 1),
                    "humidity_percent": round(input_features[0][4], 1),
                    "soil_ph": round(input_features[0][5], 1)
                }
            },
            "market_analysis": price_forecast,
            "alternative_crops": self._get_alternative_recommendations(input_features)
        }
    
    def _get_alternative_recommendations(self, input_features: np.ndarray) -> List[str]:
        """Get top 3 crop recommendations."""
        probabilities = self.model.predict_proba(input_features)[0]
        top_indices = np.argsort(probabilities)[-3:][::-1]
        main_crop_idx = np.argmax(probabilities)
        
        alternatives = []
        for idx in top_indices:
            if idx != main_crop_idx and len(alternatives) < 2:
                alternatives.append(self.label_encoder.inverse_transform([idx])[0])
        
        return alternatives
    
    def _get_alternative_locations(self, rainfall_data: pd.DataFrame, 
                                 state: str, district: str) -> List[Dict]:
        """Suggest alternative locations with similar rainfall."""
        # Get target rainfall (approximate)
        target_rainfall = rainfall_data[
            (rainfall_data['STATE_UT_NAME'] == state)
        ]['ANNUAL'].mean()
        
        if pd.isna(target_rainfall):
            return []
        
        # Find similar rainfall areas
        similar_rainfall = rainfall_data[
            (rainfall_data['STATE_UT_NAME'] != state) &
            (abs(rainfall_data['ANNUAL'] - target_rainfall) < 200)
        ].head(3)
        
        return [
            {
                "state": row['STATE_UT_NAME'],
                "district": row['DISTRICT'],
                "rainfall_mm": round(row['ANNUAL'], 1)
            }
            for _, row in similar_rainfall.iterrows()
        ]
