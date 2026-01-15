import os
import sys
import logging
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Any

# Defer importing heavy ML libs until they're needed so tests can import this module
_torch_available = True
try:
    import torch  # type: ignore
except Exception:
    torch = None
    _torch_available = False


def _import_chronos():
    try:
        from chronos import ChronosPipeline

        return ChronosPipeline
    except Exception:
        return None

# Configure logging to output to stdout (CloudWatch will capture this)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize the API
app = FastAPI(title="Grid Temperature Forecasting API")

# Mount static files
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def web_ui():
    return FileResponse("static/index.html")

# Path to locally saved model
LOCAL_MODEL_PATH = "./model"

pipeline = None


def get_pipeline() -> Any:
    """Return a loaded ChronosPipeline (or Any), loading it lazily on first use.

    Tests can monkeypatch the module-level `pipeline` variable to inject a fake pipeline.
    """
    global pipeline
    if pipeline is not None:
        return pipeline

    logger.info("Loading Chronos model lazily...")
    # Load from local path if available, otherwise fall back to Hugging Face Hub
    ChronosPipeline = _import_chronos()
    if ChronosPipeline is None:
        raise RuntimeError("ChronosPipeline is not available in this environment")

    if os.path.exists(LOCAL_MODEL_PATH) and os.path.isfile(os.path.join(LOCAL_MODEL_PATH, "config.json")):
        logger.info(f"Loading model from local path: {LOCAL_MODEL_PATH}")
        pipeline = ChronosPipeline.from_pretrained(
            LOCAL_MODEL_PATH,
            device_map="cpu",
            torch_dtype=(torch.float32 if _torch_available else None),
        )
    else:
        logger.info("Local model not found. Downloading from Hugging Face Hub...")
        logger.info("Run 'python save_model.py' to save the model locally for faster startup.")
        pipeline = ChronosPipeline.from_pretrained(
            "amazon/chronos-t5-small",
            device_map="cpu",
            torch_dtype=(torch.float32 if _torch_available else None),
        )
    logger.info("Model loaded successfully!")
    return pipeline

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
        # Try to convert to a torch tensor if available, otherwise use numpy array
        if _torch_available and torch is not None:
            context = torch.tensor(request.historical_temps)
            logger.info(f"[PREDICT] Context tensor shape: {context.shape}")
        else:
            import numpy as _np

            context = _np.array(request.historical_temps, dtype=float)
            logger.info(f"[PREDICT] Context numpy array shape: {context.shape}")
        
        # Generate forecast (20 samples for robustness)
        pl = get_pipeline()

        forecast = pl.predict(
            context,
            prediction_length=request.prediction_length,
            num_samples=20 
        )
        # Forecast may be a torch tensor or a numpy array
        try:
            shape = getattr(forecast, "shape", None)
            logger.info(f"[PREDICT] Forecast generated with shape: {shape}")
        except Exception:
            logger.info("[PREDICT] Forecast generated")

        # Return the median prediction as the primary forecast line
        try:
            import numpy as _np

            if isinstance(forecast, _np.ndarray):
                median_forecast = _np.quantile(forecast, 0.5, axis=0).tolist()
            else:
                # prefer torch for torch tensors
                if _torch_available and torch is not None and hasattr(torch, "quantile"):
                    median_forecast = torch.quantile(forecast, 0.5, dim=0).tolist()
                else:
                    # fallback to numpy conversion
                    median_forecast = _np.quantile(_np.array(forecast), 0.5, axis=0).tolist()
        except Exception:
            # Last-resort: try to coerce to list
            try:
                median_forecast = list(map(float, forecast.mean(axis=0)))
            except Exception:
                median_forecast = []
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