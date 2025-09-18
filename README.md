# Crop Glut Prevention Hackathon

A quick solution to forecast crop prices and prevent glut situations by providing early warnings to farmers.

## Quick Start

1. Create Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

2. Install dependencies:
```powershell
pip install --upgrade pip
pip install fastapi uvicorn[standard] pandas numpy statsmodels scikit-learn plotly aiofiles
```

3. Place your data files in `data/raw/`:
- `mandi_prices.csv` (required)
- `weather.csv` (optional)
- `soil.csv` (optional)

4. Run the pipeline:
```powershell
# From project root
python etl/prepare_data.py  # Process raw data
python models/train_price.py  # Train SARIMAX model
# If SARIMAX fails, run: python models/naive_forecast.py
python models/glut_signal.py  # Generate risk signals
```

5. Start the API server:
```powershell
cd api
uvicorn main:app --reload --port 8000
```

6. Open `http://localhost:8000` in your browser

## Project Structure

```
crop-glut-hackathon/
├─ data/
│  ├─ raw/                 # Input CSVs
│  └─ processed/           # ETL outputs
├─ etl/
│  └─ prepare_data.py      # Data processing
├─ models/
│  ├─ train_price.py       # SARIMAX model
│  ├─ naive_forecast.py    # Fallback model
│  └─ glut_signal.py      # Risk assessment
├─ api/
│  └─ main.py             # FastAPI backend
├─ frontend/
│  └─ index.html          # Dashboard UI
└─ README.md
```

## Features

- Price forecasting using SARIMAX model with 80% confidence intervals
- Simple glut risk assessment based on price trends
- RESTful API with FastAPI
- Mobile-responsive dashboard with Plotly visualization
- CSV export functionality

## Team Workflow

1. **Data Engineer**: Handle data prep with `prepare_data.py`
2. **ML Engineer**: Train model with `train_price.py`
3. **Backend Dev**: Run API with FastAPI
4. **Frontend Dev**: Customize dashboard in `index.html`
5. **Integrator**: Coordinate and prepare demo