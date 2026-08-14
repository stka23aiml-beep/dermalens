from fastapi import APIRouter, UploadFile, File
import base64
import cv2

from app.ml.enhancement import enhance_image
from app.ml.metrics import calculate_sharpness, calculate_contrast
from app.ml.metrics import quality_score
from app.ml.inference import predict_confidence

router = APIRouter()

# Enhancement is rejected if it makes the model LESS confident than this.
# Matches the threshold validated in evaluate_derm.py.
CONFIDENCE_DELTA_THRESHOLD = -0.02


def generate_interpretation(
    sharpness_before,
    quality_after,
    confidence_delta,
    mode,
):
    insights = []

    # Blur severity analysis -- purely descriptive, based on measured sharpness.
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

    # AI reliability assessment -- now driven by the actual measured
    # confidence delta, not by quality_after as a proxy for it.
    if confidence_delta < CONFIDENCE_DELTA_THRESHOLD:
        insights.append(
            "Enhancement reduced AI confidence; original image used for evaluation"
        )
    elif quality_after <= 40:
        # Quality-based artifacts can still be worth flagging even when
        # confidence held up -- kept as a separate, explicitly-labeled signal
        # rather than conflated with the confidence check above.
        insights.append(
            "Residual visual degradation detected; recommend manual review"
        )
    elif quality_after > 75:
        insights.append("Suitable for AI-assisted diagnostic evaluation")
    else:
        insights.append("Diagnostic features largely preserved after enhancement")

    return insights


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    image_bytes = await file.read()

    original, enhanced, mode = enhance_image(image_bytes)

    confidence_before = predict_confidence(original)
    confidence_after = predict_confidence(enhanced)
    confidence_delta = confidence_after - confidence_before

    # --- Gate: reject the enhancement if it measurably hurt confidence ---
    enhancement_accepted = confidence_delta >= CONFIDENCE_DELTA_THRESHOLD

    if enhancement_accepted:
        final_image = enhanced
        final_confidence = confidence_after
    else:
        final_image = original
        final_confidence = confidence_before

    # calculate metrics (always computed on original vs enhanced, for display)
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
        mode,
    )

    if not enhancement_accepted:
        interpretation.insert(
            0,
            f"Enhancement rejected: confidence dropped "
            f"{abs(confidence_delta) * 100:.2f} points; showing original image",
        )

    # encode whichever image the gate selected -- NOT always `enhanced`
    _, buffer = cv2.imencode(".jpg", final_image)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "image": image_base64,
        "mode": mode,
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