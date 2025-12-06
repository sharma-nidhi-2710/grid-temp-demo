import os
import sys
import torch
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chronos import ChronosPipeline

# Configure logging to output to stdout (CloudWatch will capture this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize the API
app = FastAPI(title="Grid Temperature Forecasting API")

# Path to locally saved model
LOCAL_MODEL_PATH = "./model"

logger.info("Loading Chronos model...")
# Load from local path if available, otherwise fall back to Hugging Face Hub
if os.path.exists(LOCAL_MODEL_PATH) and os.path.isfile(os.path.join(LOCAL_MODEL_PATH, "config.json")):
    logger.info(f"Loading model from local path: {LOCAL_MODEL_PATH}")
    pipeline = ChronosPipeline.from_pretrained(
        LOCAL_MODEL_PATH,
        device_map="cpu",
        torch_dtype=torch.float32,
    )
else:
    logger.info("Local model not found. Downloading from Hugging Face Hub...")
    logger.info("Run 'python save_model.py' to save the model locally for faster startup.")
    pipeline = ChronosPipeline.from_pretrained(
        "amazon/chronos-t5-small",
        device_map="cpu",
        torch_dtype=torch.float32,
    )
logger.info("Model loaded successfully!")

# Define the expected input format for the API
class ForecastRequest(BaseModel):
    historical_temps: list[float]
    prediction_length: int = 24

@app.post("/predict")
def predict_temperature(request: ForecastRequest):
    """
    Accepts historical temperatures and returns a 24-hour forecast.
    """
    try:
        logger.info(f"[PREDICT] Received request with {len(request.historical_temps)} historical temps")
        logger.info(f"[PREDICT] Request data: {request.historical_temps}")
        logger.info(f"[PREDICT] Prediction length: {request.prediction_length}")
        
        # Chronos model requires the input context to be a tensor
        context = torch.tensor(request.historical_temps)
        logger.info(f"[PREDICT] Context tensor shape: {context.shape}")
        
        # Generate forecast (20 samples for robustness)
        forecast = pipeline.predict(
            context,
            prediction_length=request.prediction_length,
            num_samples=20 
        )
        logger.info(f"[PREDICT] Forecast generated with shape: {forecast.shape}")
        
        # Return the median prediction as the primary forecast line
        median_forecast = torch.quantile(forecast, 0.5, dim=0).tolist()
        logger.info(f"[PREDICT] Median forecast: {median_forecast}")
        logger.info("[PREDICT] Request completed successfully")
        
        return {"forecast": median_forecast}

    except Exception as e:
        logger.error(f"[PREDICT] ERROR: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Simple endpoint to check if the service is running."""
    logger.info("[HEALTH] Health check called")
    return {"status": "healthy"}