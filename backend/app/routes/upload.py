import os
import base64
import cv2

from fastapi import APIRouter, UploadFile, File

from app.ml.enhancement import enhance_image
from app.ml.metrics import calculate_sharpness, calculate_contrast, quality_score
from app.ml.derm_model import load_model, predict

router = APIRouter()

# Load model once, at import time, using a path resolved relative to this
# file's own location -- NOT relative to the process's working directory.
# This avoids the fragile cwd-dependent path bug that existed when
# predict_confidence was imported from evaluate_derm.py.
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .../app
_WEIGHTS_PATH = os.path.join(_APP_DIR, "ml", "models", "isic_resnet18.pth")

_model = load_model(_WEIGHTS_PATH)

# Same tolerance band used in evaluate_derm.py -- a confidence drop smaller
# than this is treated as noise, not real degradation. Keep these in sync
# if you change one.
DEGRADATION_THRESHOLD = -0.02


def predict_confidence(image_np):
    _, confidence = predict(_model, image_np)
    return float(confidence)


def generate_interpretation(
    sharpness_before,
    quality_after,
    confidence_delta,
    enhancement_accepted,
):
    """
    NOTE: previously this function's "AI confidence" messaging was actually
    driven by quality_after (sharpness/contrast), not by the real measured
    confidence_delta -- so the caption could say "may influence AI
    confidence" or "suitable for diagnosis" independent of what the
    classifier's confidence actually did. This version separates the two:
    blur-severity messaging still uses sharpness/quality as before, but the
    confidence-facing message is now driven directly by the gate decision.
    """
    insights = []

    # Blur severity analysis (unchanged from before)
    if sharpness_before < 10:
        insights.append("Severe blur detected")
        insights.append("AI-assisted restoration successfully applied")
        insights.append("Lesion visibility and edge definition improved")
    elif sharpness_before < 40:
        insights.append("Moderate blur detected")
        insights.append("Adaptive enhancement successfully applied")
        insights.append("Image clarity and texture detail improved")
    else:
        insights.append("Image already relatively clear")
        insights.append("Minimal enhancement required")
        insights.append("Original diagnostic quality preserved")

    # Confidence-facing message -- now driven by the ACTUAL measured delta
    # and the gate's real decision, not by quality_after.
    if not enhancement_accepted:
        insights.append(
            f"Enhancement reduced AI confidence by {abs(confidence_delta) * 100:.2f} "
            "points -- original image used for diagnosis instead"
        )
    elif quality_after > 75:
        insights.append("Suitable for AI-assisted diagnostic evaluation")
    elif quality_after > 40:
        insights.append("Diagnostic features largely preserved after enhancement")
    else:
        insights.append("Enhancement accepted, but residual quality remains limited")

    return insights


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    original, enhanced, mode = enhance_image(image_bytes)

    confidence_before = predict_confidence(original)
    confidence_after = predict_confidence(enhanced)
    confidence_delta = confidence_after - confidence_before

    print("CONF BEFORE:", confidence_before)
    print("CONF AFTER:", confidence_after)
    print("CONF DELTA:", confidence_delta)

    # ---- VALIDATION GATE ----
    # Same logic as evaluate_derm.py: reject the enhancement if it degrades
    # confidence beyond the noise-tolerance threshold, and serve the
    # original image + its prediction instead. This is what was MISSING
    # before -- the enhanced result was always returned regardless of
    # whether it actually helped.
    enhancement_accepted = confidence_delta >= DEGRADATION_THRESHOLD

    if enhancement_accepted:
        final_image = enhanced
        final_confidence = confidence_after
    else:
        final_image = original
        final_confidence = confidence_before

    # calculate metrics (still computed on original vs enhanced, for display)
    sharp_before = calculate_sharpness(original)
    sharp_after = calculate_sharpness(enhanced)

    contrast_before = calculate_contrast(original)
    contrast_after = calculate_contrast(enhanced)

    quality_before = quality_score(sharp_before, contrast_before)
    quality_after = quality_score(sharp_after, contrast_after)

    interpretation = generate_interpretation(
        sharp_before,
        quality_after,
        confidence_delta,
        enhancement_accepted,
    )

    # encode whichever image the gate decided to serve
    _, buffer = cv2.imencode(".jpg", final_image)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "image": image_base64,
        "mode": mode if enhancement_accepted else "No Enhancement (rejected by validation gate)",
        "enhancement_accepted": enhancement_accepted,
        "metrics": {
            "sharpness_before": sharp_before,
            "sharpness_after": sharp_after,
            "contrast_before": contrast_before,
            "contrast_after": contrast_after,
            "quality_before": quality_before,
            "quality_after": quality_after,
        },
        "confidence": {
            "before": confidence_before,
            "after": confidence_after,
            "delta": confidence_delta,
            "final": final_confidence,
        },
        "interpretation": interpretation,
    }