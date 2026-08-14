# backend/app/ml/inference.py
"""
Shared model-loading + inference entry point.

Both the FastAPI route (app/routes/upload.py) and the standalone
evaluation script (app/ml/evaluate_derm.py) import from HERE instead
of from each other. This is the only place that:
  - resolves the weights path (absolute, not cwd-dependent)
  - loads the model (lazily, once per process)
"""

from functools import lru_cache
from pathlib import Path

from app.ml.derm_model import load_model, predict

# Resolved relative to this file's location on disk, not to whatever
# directory the process happens to be launched from.
WEIGHTS_PATH = Path(__file__).resolve().parent / "models" / "isic_resnet18.pth"


@lru_cache(maxsize=1)
def get_model():
    """
    Loads the model on first call and caches it for the lifetime of the
    process. No model loading happens at import time -- importing this
    module is now cheap and side-effect-free.
    """
    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(
            f"Model weights not found at {WEIGHTS_PATH}. "
            f"Expected them at app/ml/models/isic_resnet18.pth relative "
            f"to this file."
        )
    return load_model(str(WEIGHTS_PATH))


def predict_confidence(image):
    model = get_model()
    _, confidence = predict(model, image)
    return float(confidence)