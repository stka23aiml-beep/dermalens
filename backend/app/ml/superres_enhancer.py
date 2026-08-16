from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np

# Resolved relative to this file's location on disk, not to whatever
# directory the process happens to be launched from.
WEIGHTS_PATH = Path(__file__).resolve().parent / "weights" / "EDSR_x2.pb"

# EDSR is a fixed 2x model. If an image is *very* large, running it at full
# size is wasteful, so we still cap input size -- but at a size that avoids
# throwing away detail for typical dermoscopy image resolutions. Adjust
# this based on what your actual dataset resolutions look like; 400 was
# too aggressive and was net-downscaling anything wider than 800px.
MAX_INPUT_WIDTH = 1024


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


def enhance_superres(image, sharpen=True, sharpen_strength=0.3):
    """
    Args:
        image: BGR uint8 numpy array
        sharpen: whether to apply post-SR sharpening at all. The previous
            hardcoded sharpening kernel amplified noise/artifacts along
            with real edges, which is a likely contributor to cases where
            AI Super Resolution increased the Laplacian-variance sharpness
            metric while REDUCING classifier confidence -- inflated
            "sharpness" from amplified noise, not recovered detail.
        sharpen_strength: 0.0 = no sharpening, 1.0 = the original kernel's
            full strength. Default lowered from implicit 1.0 to 0.3 so
            edges are lightly enhanced without amplifying compression
            artifacts as aggressively.
    """
    sr = get_sr_model()

    h, w = image.shape[:2]

    # Only downscale if the image is genuinely large -- avoid the previous
    # bug where anything wider than 800px was net-downscaled (shrunk to
    # 400px, then upsampled 2x back to 800px, a real loss of detail
    # disguised as "enhancement").
    if w > MAX_INPUT_WIDTH:
        scale = MAX_INPUT_WIDTH / w
        image = cv2.resize(
            image,
            (int(w * scale), int(h * scale)),
            interpolation=cv2.INTER_AREA
        )

    # AI super resolution
    result = sr.upsample(image)

    if sharpen and sharpen_strength > 0:
        # Unsharp-mask style kernel, blended with the original at
        # `sharpen_strength` to avoid amplifying noise/artifacts as hard
        # as the original fixed kernel did.
        kernel = np.array([
            [0, -1, 0],
            [-1, 5, -1],
            [0, -1, 0]
        ], dtype=np.float32)
        sharpened = cv2.filter2D(result, -1, kernel)
        result = cv2.addWeighted(
            result, 1 - sharpen_strength,
            sharpened, sharpen_strength,
            0
        )

    return result