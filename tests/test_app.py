import pytest
from fastapi.testclient import TestClient

import app as app_module


class MockPipeline:
    def predict(self, context, prediction_length: int = 24, num_samples: int = 1):
        # Return a numpy array of shape (num_samples, prediction_length)
        import numpy as _np

        # determine last value in context
        try:
            last = float(context[-1].item())
        except Exception:
            last = float(context[-1]) if len(context) > 0 else 0.0

        samples = _np.full((num_samples, prediction_length), fill_value=last, dtype=float)
        return samples


@pytest.fixture(autouse=True)
def inject_mock_pipeline(monkeypatch):
    """Replace the real Chronos pipeline with a lightweight mock for tests."""
    mock = MockPipeline()
    monkeypatch.setattr(app_module, "pipeline", mock)
    yield


def test_health_endpoint():
    client = TestClient(app_module.app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_predict_endpoint_basic():
    client = TestClient(app_module.app)
    payload = {"historical_temps": [10.0, 12.0, 11.5], "prediction_length": 3}
    r = client.post("/predict", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "forecast" in data
    assert isinstance(data["forecast"], list)
    assert len(data["forecast"]) == 3
    # Since mock repeats the last value, check equality
    assert all(x == 11.5 for x in data["forecast"]) 
