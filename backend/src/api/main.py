from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from src.models.crop_price_model import EnhancedCropPriceModel
from src.utils.data_loader import data_manager, load_data  # Import both
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enhanced Crop Recommendation & Price Forecasting API",
    description="AI-powered agricultural recommendations with market analysis",
    version="2.0.0"
)

# Initialize model
model = EnhancedCropPriceModel()

# Load data with error handling
try:
    model.train_crop_model("data/raw/Crop_recommendation.csv")
    price_data = data_manager.load_data("data/processed/processed_data.csv")
    rainfall_data = data_manager.load_data("data/raw/district_wise_rainfall_normal.csv")
    logger.info("Data loaded successfully")
except Exception as e:
    logger.error(f"Failed to load data: {e}")
    price_data = pd.DataFrame()
    rainfall_data = pd.DataFrame()

class RecommendationRequest(BaseModel):
    state: str = Field(..., min_length=2, max_length=50, description="State name")
    district: str = Field(..., min_length=2, max_length=50, description="District name")
    lookback_days: Optional[int] = Field(90, ge=7, le=365, description="Days for price analysis")

class RecommendationResponse(BaseModel):
    success: bool
    recommendation: dict
    market_analysis: Optional[dict] = None
    alternative_crops: Optional[List[str]] = None
    error: Optional[str] = None

@app.get("/health", response_model=dict)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": model.model is not None,
        "data_available": not price_data.empty and not rainfall_data.empty,
        "available_crops": list(model.label_encoder.classes_) if hasattr(model, 'label_encoder') and model.label_encoder else []
    }

@app.get("/recommend", response_model=RecommendationResponse)
async def recommend_crop(
    state: str = Query(..., description="State name (e.g., Gujarat)"),
    district: str = Query(..., description="District name (e.g., Amreli)"),
    lookback_days: Optional[int] = Query(90, ge=7, le=365)
):
    """Get comprehensive crop recommendation and market analysis.
    
    This endpoint provides:
    - AI-powered crop recommendations based on environmental conditions
    - Market price forecasting using exponential moving averages
    - Confidence scores and alternative suggestions
    """
    try:
        logger.info(f"Processing request for {state}, {district}")
        
        # Validate inputs
        if not state or not district:
            raise HTTPException(status_code=400, detail="State and district are required")
        
        recommendation = model.recommend_crop(state, district, price_data, rainfall_data)
        
        if "error" in recommendation:
            raise HTTPException(status_code=404, detail=recommendation["error"])
        
        return RecommendationResponse(**recommendation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/crops")
async def get_available_crops():
    """Get list of crops the model can recommend."""
    if not hasattr(model, 'label_encoder') or model.label_encoder is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    return {
        "crops": list(model.label_encoder.classes_),
        "total_crops": len(model.label_encoder.classes_)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
