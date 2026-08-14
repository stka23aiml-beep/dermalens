from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

# Resolved relative to this file's location on disk, not to whatever
# directory the process happens to be launched from.
WEIGHTS_PATH = Path(__file__).resolve().parent / "weights" / "EDSR_x2.pb"


@lru_cache(maxsize=1)
def get_sr_model():
    """
    Loads the super-resolution model on first use and caches it for the
    life of the process. No loading happens at import time.
    """
    if not WEIGHTS_PATH.exists():
        raise FileNotFoundError(
            f"Super-resolution weights not found at {WEIGHTS_PATH}. "
            f"Expected them at app/ml/weights/EDSR_x2.pb relative to "
            f"this file."
        )
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel(str(WEIGHTS_PATH))
    sr.setModel("edsr", 2)
    return sr


def enhance_superres(image):
    sr = get_sr_model()

    h, w = image.shape[:2]

    # resize before SR
    if w > 400:
        scale = 400 / w
        image = cv2.resize(
            image,
            (int(w * scale), int(h * scale))
        )

    # AI super resolution
    result = sr.upsample(image)

    # mild sharpening after SR
    kernel = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ], dtype=np.float32)

    result = cv2.filter2D(result, -1, kernel)

    return result