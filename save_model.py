"""
Script to download and save the Chronos model locally.
Run this once to save the model, then use app.py with the local model.
"""
import torch
from chronos import ChronosPipeline

MODEL_NAME = "amazon/chronos-t5-small"
LOCAL_MODEL_PATH = "./model"

print(f"Download ing {MODEL_NAME} from Hugging Face Hub...")
pipeline = ChronosPipeline.from_pretrained(
    MODEL_NAME,
    device_map="cpu",
    torch_dtype=torch.float32,
)

print(f"Saving model to {LOCAL_MODEL_PATH}...")
# The inner_model is the actual HuggingFace PreTrainedModel that has save_pretrained
pipeline.inner_model.save_pretrained(LOCAL_MODEL_PATH)

print(f"Model saved successfully to {LOCAL_MODEL_PATH}!")
print("You can now run app.py which will use the local model.")
