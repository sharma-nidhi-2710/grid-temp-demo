import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from chronos import ChronosPipeline

# Initialize the API
app = FastAPI(title="Grid Temperature Forecasting API")

print("Loading Chronos model... this might take a minute the first time...")
# Load the model directly from Hugging Face Hub. 
# It will download the weights if not cached.
pipeline = ChronosPipeline.from_pretrained(
    "amazon/chronos-t5-small",
    device_map="cpu",  # Stick to CPU for the cost-effective demo
    torch_dtype=torch.float32,
)
print("Model loaded successfully!")

# Define the expected input format for the API
class ForecastRequest(BaseModel):
    # This list will contain the historical Oil Temperature (OT) values
    historical_temps: list[float]
    prediction_length: int = 24

@app.post("/predict")
def predict_temperature(request: ForecastRequest):
    """
    Accepts historical temperatures and returns a 24-hour forecast.
    """
    try:
        # Chronos model requires the input context to be a tensor
        context = torch.tensor(request.historical_temps)
        
        # Generate forecast (20 samples for robustness)
        forecast = pipeline.predict(
            context,
            prediction_length=request.prediction_length,
            num_samples=20 
        )
        
        # Return the median prediction as the primary forecast line
        median_forecast = torch.quantile(forecast, 0.5, dim=0).tolist()
        
        return {"forecast": median_forecast}

    except Exception as e:
        # Catch any errors (like bad input data)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Simple endpoint to check if the service is running."""
    return {"status": "healthy"}