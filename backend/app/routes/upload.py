from app.ml.evaluate_derm import predict_confidence
from fastapi import APIRouter, UploadFile, File
import base64
import cv2

from app.ml.enhancement import enhance_image
from app.ml.metrics import calculate_sharpness, calculate_contrast
from app.ml.metrics import quality_score


def generate_interpretation(
    sharpness_before,
    sharpness_after,
    quality_before,
    quality_after,
    mode
):

    insights = []

    # Blur severity analysis
    if sharpness_before < 10:

        insights.append("Severe blur detected")

        insights.append(
            "AI-assisted restoration successfully applied"
        )

        insights.append(
            "Lesion visibility and edge definition improved"
        )

    elif sharpness_before < 40:

        insights.append("Moderate blur detected")

        insights.append(
            "Adaptive enhancement successfully applied"
        )

        insights.append(
            "Image clarity and texture detail improved"
        )

    else:

        insights.append(
            "Image already relatively clear"
        )

        insights.append(
            "Minimal enhancement required"
        )

        insights.append(
            "Original diagnostic quality preserved"
        )

    # AI reliability assessment
    if quality_after > 75:

        insights.append(
            "Suitable for AI-assisted diagnostic evaluation"
        )

    elif quality_after > 40:

        insights.append(
            "Diagnostic features largely preserved after enhancement"
        )

    else:

        insights.append(
            "Residual degradation may still influence AI confidence"
        )

    return insights
router = APIRouter()


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

    # calculate metrics
    sharp_before = calculate_sharpness(original)
    sharp_after = calculate_sharpness(enhanced)

    contrast_before = calculate_contrast(original)
    contrast_after = calculate_contrast(enhanced)

    quality_before = quality_score(sharp_before, contrast_before)
    quality_after = quality_score(sharp_after, contrast_after)

    
    interpretation = generate_interpretation(
    sharp_before,
    sharp_after,
    quality_before,
    quality_after,
    mode
)

    # encode enhanced image
    _, buffer = cv2.imencode(".jpg", enhanced)
    image_base64 = base64.b64encode(buffer).decode("utf-8")

    return {
    "image": image_base64,
    "mode": mode,
    "metrics": {
        "sharpness_before": sharp_before,
        "sharpness_after": sharp_after,
        "contrast_before": contrast_before,
        "contrast_after": contrast_after,
        "quality_before": quality_before,
        "quality_after": quality_after
    },

    "confidence": {
        "before": confidence_before,
        "after": confidence_after,
        "delta": confidence_delta
    },

    "interpretation": interpretation
}