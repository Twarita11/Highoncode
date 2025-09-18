# Crop Glut Prevention System

A comprehensive data-driven system to help farmers make informed decisions about crop selling and distribution to prevent oversupply and maximize income.

## Features

- Advanced price prediction using ensemble models (XGBoost and LightGBM)
- Market trend analysis with confidence bands
- Seasonal pattern detection and visualization
- Supply-demand pressure analysis
- Region-specific recommendations
- Interactive dashboards with real-time updates
- RESTful API with comprehensive documentation

## Quick Start

1. Create Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install backend dependencies:
```powershell
pip install --upgrade pip
pip install fastapi uvicorn[standard] pandas numpy statsmodels scikit-learn plotly xgboost lightgbm aiofiles python-multipart
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

4. Place your data files in `data/raw/` and run the data processing pipeline:
```powershell
# From project root
python etl/prepare_data.py  # Process raw data
python models/train_models.py  # Train ML models
```

5. Start the API server:
```powershell
cd api
uvicorn main:app --reload --port 8000
```

6. Start the frontend development server:
```bash
cd frontend
npm run dev
```

7. Open `http://localhost:3000` in your browser

## Project Structure

```
crop-glut-hackathon/
├─ api/                    # FastAPI backend
│  ├─ main.py             # Main API endpoints
│  ├─ models/             # Data models and schemas
│  └─ services/           # Business logic
├─ data/
│  ├─ raw/                # Input datasets
│  └─ processed/          # Processed data files
├─ etl/
│  └─ prepare_data.py     # Data processing pipeline
├─ models/
│  ├─ xgb_model.pkl       # XGBoost model
│  ├─ lgb_model.pkl       # LightGBM model
│  └─ train_models.py     # Model training scripts
├─ notebooks/
│  └─ unified_analysis.ipynb  # Analysis notebook
├─ frontend/
│  ├─ src/               # React components
│  ├─ public/            # Static assets
│  └─ package.json       # Frontend dependencies
└─ README.md
```

## API Documentation

### Market Analysis Endpoints

#### GET `/api/market/trends`
Get market trend analysis for a specific region and crop.

**Parameters:**
- `region`: string (required) - Region name
- `crop`: string (required) - Crop name
- `start_date`: string (optional) - Start date for analysis (YYYY-MM-DD)
- `end_date`: string (optional) - End date for analysis (YYYY-MM-DD)

**Response:**
```json
{
    "market_status": {
        "current_price": float,
        "avg_price": float,
        "price_trend": string,
        "volatility": float
    },
    "seasonal_insights": {
        "best_months": [int],
        "worst_months": [int],
        "current_month_rank": int
    },
    "market_pressure": {
        "supply_pressure": float,
        "demand_pressure": float
    }
}
```

#### GET `/api/market/recommendations`
Get personalized recommendations for a region.

**Parameters:**
- `region`: string (required) - Region name
- `crop`: string (required) - Crop name

**Response:**
```json
{
    "recommendations": [
        {
            "type": string,
            "urgency": string,
            "message": string
        }
    ]
}
```

### Price Prediction Endpoints

#### POST `/api/predict/price`
Get price predictions for upcoming days.

**Request Body:**
```json
{
    "region": string,
    "crop": string,
    "days": int
}
```

**Response:**
```json
{
    "predictions": [
        {
            "date": string,
            "predicted_price": float,
            "confidence_lower": float,
            "confidence_upper": float
        }
    ]
}
```

### Visualization Endpoints

#### GET `/api/visualizations/price-trends`
Get price trend visualization data.

**Parameters:**
- `region`: string (required)
- `crop`: string (required)
- `period`: string (optional) - "1m", "3m", "6m", "1y"

#### GET `/api/visualizations/seasonal-patterns`
Get seasonal pattern visualization data.

**Parameters:**
- `region`: string (required)
- `crop`: string (required)

## Frontend Components

### Market Dashboard
- Interactive price trends chart with confidence bands
- Seasonal pattern visualization
- Supply pressure gauge
- Real-time market recommendations

### Prediction Interface
- Date range selector
- Region/crop selector
- Advanced visualization options
- Export functionality

### Recommendation Display
- Urgency-based color coding
- Actionable insights
- Market pressure indicators

## Model Information

The system uses two main models:

1. **XGBoost Model** (`models/xgb_model.pkl`)
   - Short-term price predictions
   - Features: price history, weather data, market indicators
   - Performance: R² = 0.795

2. **LightGBM Model** (`models/lgb_model.pkl`)
   - Long-term trend predictions
   - Features: seasonal patterns, market trends
   - Performance: R² = 0.836

## Error Handling

All API endpoints use this error response format:
```json
{
    "error": {
        "code": string,
        "message": string,
        "details": object
    }
}
```

Common error codes:
- `INVALID_REGION`: Region not found
- `INSUFFICIENT_DATA`: Not enough data
- `MODEL_ERROR`: Prediction error
- `VALIDATION_ERROR`: Invalid parameters

## Team Workflow

1. **Data Engineer**: 
   - Manage data pipeline
   - Implement feature engineering
   - Maintain data quality

2. **ML Engineer**:
   - Train and optimize models
   - Monitor model performance
   - Update prediction logic

3. **Backend Developer**:
   - Implement API endpoints
   - Handle data validation
   - Manage error handling

4. **Frontend Developer**:
   - Build reactive components
   - Implement visualizations
   - Ensure mobile responsiveness

5. **QA Engineer**:
   - Test API endpoints
   - Validate predictions
   - Ensure data accuracy