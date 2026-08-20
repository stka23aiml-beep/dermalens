
import os
import base64
import cv2
import numpy as np

from fastapi import APIRouter, UploadFile, File

from app.ml.enhancement import enhance_image
from app.ml.metrics import (
    calculate_sharpness,
    calculate_contrast,
    calculate_brightness,
    brightness_improvement,
    quality_score,
)
from app.ml.derm_model import load_model, predict


router = APIRouter()


# --------------------------------------------------
# MODEL
# --------------------------------------------------

_APP_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

_WEIGHTS_PATH = os.path.join(
    _APP_DIR,
    "ml",
    "models",
    "isic_resnet18.pth"
)

_model = load_model(_WEIGHTS_PATH)


# --------------------------------------------------
# IMAGE-QUALITY SETTINGS
# --------------------------------------------------

# For normal/acceptable exposure images, enhancement
# should demonstrate a meaningful improvement.
MIN_QUALITY_IMPROVEMENT = 0.02


# Prevent enhancement from creating an extreme
# sharpness jump that is likely artificial.
MAX_SHARPNESS_MULTIPLIER = 4.0


# Prevent aggressive brightening from blowing out
# the image.
MAX_ACCEPTABLE_BRIGHTNESS = 220.0


# --------------------------------------------------
# AI CONFIDENCE
# --------------------------------------------------
#
# IMPORTANT:
#
# Confidence DOES NOT decide whether enhancement
# is accepted.
#
# It is only reported as secondary information.
#


def predict_confidence(image_np):

    _, confidence = predict(
        _model,
        image_np
    )

    return float(confidence)


# --------------------------------------------------
# IMAGE HELPERS
# --------------------------------------------------

def calculate_noise_estimate(image):
    """
    Estimate high-frequency noise.

    This is intentionally used as a supporting signal,
    NOT as an absolute noise detector.

    A sudden large increase in high-frequency energy
    can indicate that enhancement is creating texture
    rather than recovering useful information.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    median = cv2.medianBlur(
        gray,
        3
    )

    residual = cv2.absdiff(
        gray,
        median
    )

    return float(
        np.mean(residual)
    )


def calculate_color_shift(
    original,
    enhanced
):
    """
    Measure average color change between original
    and enhanced image.

    Small changes are expected from brightness/contrast
    correction.

    Large changes can indicate aggressive processing.
    """

    if original.shape != enhanced.shape:

        enhanced_resized = cv2.resize(
            enhanced,
            (
                original.shape[1],
                original.shape[0]
            ),
            interpolation=cv2.INTER_AREA
        )

    else:

        enhanced_resized = enhanced

    original_lab = cv2.cvtColor(
        original,
        cv2.COLOR_BGR2LAB
    )

    enhanced_lab = cv2.cvtColor(
        enhanced_resized,
        cv2.COLOR_BGR2LAB
    )

    diff = cv2.absdiff(
        original_lab,
        enhanced_lab
    )

    return float(
        np.mean(diff)
    )


def calculate_structure_similarity(
    original,
    enhanced
):
    """
    Simple structure-preservation measure.

    This is not SSIM.

    It measures normalized grayscale correlation
    between the original and enhanced image after
    resizing the enhanced image back to original size.

    Higher is better.
    """

    if original.shape != enhanced.shape:

        enhanced_resized = cv2.resize(
            enhanced,
            (
                original.shape[1],
                original.shape[0]
            ),
            interpolation=cv2.INTER_AREA
        )

    else:

        enhanced_resized = enhanced

    original_gray = cv2.cvtColor(
        original,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    enhanced_gray = cv2.cvtColor(
        enhanced_resized,
        cv2.COLOR_BGR2GRAY
    ).astype(np.float32)

    original_flat = (
        original_gray -
        np.mean(original_gray)
    )

    enhanced_flat = (
        enhanced_gray -
        np.mean(enhanced_gray)
    )

    denominator = (
        np.sqrt(
            np.sum(
                original_flat ** 2
            )
        )
        *
        np.sqrt(
            np.sum(
                enhanced_flat ** 2
            )
        )
    )

    if denominator == 0:

        return 1.0

    correlation = (
        np.sum(
            original_flat *
            enhanced_flat
        )
        /
        denominator
    )

    return float(
        np.clip(
            correlation,
            -1.0,
            1.0
        )
    )


# --------------------------------------------------
# CANDIDATE VALIDATION
# --------------------------------------------------

def evaluate_candidate(
    original,
    candidate,
    candidate_mode,
):
    """
    Evaluate one enhancement candidate.

    The candidate is judged using image-quality signals,
    NOT classifier confidence.

    The goal is:

        clearer
        brighter when needed
        better contrast when needed
        more useful detail

    WITHOUT:

        excessive sharpening
        extreme brightness
        excessive noise
        large color changes
        destruction of original structure
    """

    # --------------------------------------------------
    # ORIGINAL METRICS
    # --------------------------------------------------

    sharp_before = calculate_sharpness(
        original
    )

    contrast_before = calculate_contrast(
        original
    )

    brightness_before = calculate_brightness(
        original
    )

    quality_before = quality_score(
        sharp_before,
        contrast_before,
        brightness_before
    )

    noise_before = calculate_noise_estimate(
        original
    )

    # --------------------------------------------------
    # CANDIDATE METRICS
    # --------------------------------------------------

    sharp_after = calculate_sharpness(
        candidate
    )

    contrast_after = calculate_contrast(
        candidate
    )

    brightness_after = calculate_brightness(
        candidate
    )

    quality_after = quality_score(
        sharp_after,
        contrast_after,
        brightness_after
    )

    noise_after = calculate_noise_estimate(
        candidate
    )

    # --------------------------------------------------
    # IMPROVEMENTS
    # --------------------------------------------------

    if quality_before > 0:

        quality_improvement = (
            quality_after -
            quality_before
        ) / quality_before

    else:

        quality_improvement = 0.0

    exposure_improvement = brightness_improvement(
        brightness_before,
        brightness_after
    )

    # --------------------------------------------------
    # SHARPNESS MULTIPLIER
    # --------------------------------------------------

    if sharp_before > 0:

        sharpness_multiplier = (
            sharp_after /
            sharp_before
        )

    else:

        sharpness_multiplier = 1.0

    # --------------------------------------------------
    # NOISE CHANGE
    # --------------------------------------------------

    if noise_before > 0:

        noise_change = (
            noise_after -
            noise_before
        ) / noise_before

    else:

        noise_change = 0.0

    # --------------------------------------------------
    # STRUCTURE
    # --------------------------------------------------

    structure_similarity = (
        calculate_structure_similarity(
            original,
            candidate
        )
    )

    # --------------------------------------------------
    # COLOR SHIFT
    # --------------------------------------------------

    color_shift = calculate_color_shift(
        original,
        candidate
    )

    # --------------------------------------------------
    # IMAGE CONDITIONS
    # --------------------------------------------------

    is_low_light = (
        brightness_before < 90
    )

    is_severely_dark = (
        brightness_before < 50
    )

    is_blurry = (
        sharp_before < 80
    )

    # --------------------------------------------------
    # SAFETY CONDITIONS
    # --------------------------------------------------

    brightness_safe = (
        brightness_after
        <= MAX_ACCEPTABLE_BRIGHTNESS
    )

    sharpness_safe = (
        sharpness_multiplier
        <= MAX_SHARPNESS_MULTIPLIER
    )

    structure_safe = (
        structure_similarity
        >= 0.90
    )

    color_safe = (
        color_shift
        <= 20.0
    )

    # --------------------------------------------------
    # NOISE SAFETY
    # --------------------------------------------------

    # Allow some increase because super-resolution
    # can legitimately reveal high-frequency detail.

    noise_safe = (
        noise_change
        <= 1.50
    )

    # --------------------------------------------------
    # DETERMINE WHETHER CANDIDATE IS USEFUL
    # --------------------------------------------------

    accepted = False

    reason = ""

    # --------------------------------------------------
    # LOW-LIGHT IMAGE
    # --------------------------------------------------

    if is_low_light:

        # Brightness correction is the PRIMARY objective.

        if (
            exposure_improvement > 0
            and
            brightness_safe
            and
            structure_safe
            and
            color_safe
            and
            noise_safe
            and
            quality_after >= (
                quality_before * 0.90
            )
        ):

            accepted = True

            reason = (
                "Low-light image improved "
                "without excessive alteration"
            )


    # --------------------------------------------------
    # BLUR IMAGE
    # --------------------------------------------------

    elif is_blurry:

        # Blur restoration has a different objective from
        # brightness/contrast enhancement.
        #
        # We primarily require:
        #   1. measurable sharpness improvement
        #   2. preserved original structure
        #   3. controlled noise
        #   4. no excessive artificial sharpening
        #
        # We deliberately do NOT require the generic
        # quality-improvement threshold here because a
        # small sharpness recovery can be useful even when
        # the composite quality score changes very little.

        blur_improved = (
            sharp_after > sharp_before
        )

        blur_structure_safe = (
            structure_similarity >= 0.90
        )

        blur_noise_safe = (
            noise_change <= 1.50
        )

        blur_sharpness_safe = (
            sharpness_multiplier <= MAX_SHARPNESS_MULTIPLIER
        )

        if (
            blur_improved
            and blur_structure_safe
            and blur_noise_safe
            and blur_sharpness_safe
            and brightness_safe
            and color_safe
        ):

            accepted = True

            reason = (
                "Blur restoration improved "
                "recoverable detail while preserving "
                "original structure"
            )

    # --------------------------------------------------
    # NORMAL EXPOSURE
    # --------------------------------------------------

    else:

        if (
            quality_improvement
            >= MIN_QUALITY_IMPROVEMENT
            and
            brightness_safe
            and
            sharpness_safe
            and
            structure_safe
            and
            color_safe
            and
            noise_safe
        ):

            accepted = True

            reason = (
                "Image-quality metrics "
                "show meaningful improvement"
            )
    # --------------------------------------------------
    # SPECIAL CASE:
    # EXTREMELY DARK IMAGE
    # --------------------------------------------------

    if is_severely_dark:

        if (
            exposure_improvement > 0
            and
            brightness_after > brightness_before
            and
            brightness_after <= MAX_ACCEPTABLE_BRIGHTNESS
            and
            structure_similarity >= 0.85
        ):

            accepted = True

            reason = (
                "Severe low-light image "
                "received exposure correction"
            )

    # --------------------------------------------------
    # ORIGINAL CANDIDATE
    # --------------------------------------------------

    if candidate_mode == "Original":

        accepted = False

        reason = (
            "Original image"
        )

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    print(
        "----------------------------------------"
    )

    print(
        "CANDIDATE:",
        candidate_mode
    )

    print(
        "BRIGHTNESS:",
        brightness_before,
        "→",
        brightness_after
    )

    print(
        "SHARPNESS:",
        sharp_before,
        "→",
        sharp_after
    )

    print(
        "CONTRAST:",
        contrast_before,
        "→",
        contrast_after
    )

    print(
        "QUALITY:",
        quality_before,
        "→",
        quality_after
    )

    print(
        "QUALITY IMPROVEMENT:",
        quality_improvement
    )

    print(
        "EXPOSURE IMPROVEMENT:",
        exposure_improvement
    )

    print(
        "SHARPNESS MULTIPLIER:",
        sharpness_multiplier
    )

    print(
        "NOISE:",
        noise_before,
        "→",
        noise_after
    )

    print(
        "NOISE CHANGE:",
        noise_change
    )

    print(
        "STRUCTURE SIMILARITY:",
        structure_similarity
    )

    print(
        "COLOR SHIFT:",
        color_shift
    )

    print(
        "ACCEPTED:",
        accepted
    )

    print(
        "REASON:",
        reason
    )

    return {
        "accepted": accepted,
        "reason": reason,
        "quality_before": quality_before,
        "quality_after": quality_after,
        "quality_improvement": quality_improvement,
        "brightness_before": brightness_before,
        "brightness_after": brightness_after,
        "exposure_improvement": exposure_improvement,
        "sharpness_before": sharp_before,
        "sharpness_after": sharp_after,
        "sharpness_multiplier": sharpness_multiplier,
        "contrast_before": contrast_before,
        "contrast_after": contrast_after,
        "noise_before": noise_before,
        "noise_after": noise_after,
        "noise_change": noise_change,
        "structure_similarity": structure_similarity,
        "color_shift": color_shift,
    }


# --------------------------------------------------
# SELECT BEST CANDIDATE
# --------------------------------------------------

def select_best_candidate(
    original,
    candidates
):
    """
    Select the best valid enhancement candidate.

    IMPORTANT:

    We do NOT simply choose the candidate with the
    highest sharpness.

    That would reward artificial texture.

    Instead we prioritize:

        1. meaningful quality improvement
        2. brightness improvement when image is dark
        3. structure preservation
        4. controlled sharpness
        5. controlled noise
    """

    original_brightness = calculate_brightness(
        original
    )

    is_low_light = (
        original_brightness < 90
    )

    evaluated = []

    for candidate in candidates:

        candidate_image = candidate["image"]

        candidate_mode = candidate["mode"]

        result = evaluate_candidate(
            original,
            candidate_image,
            candidate_mode
        )

        evaluated.append(
            {
                "candidate": candidate,
                "evaluation": result,
            }
        )

    valid_candidates = [
        item
        for item in evaluated
        if item["evaluation"]["accepted"]
    ]

    # --------------------------------------------------
    # NO VALID ENHANCEMENT
    # --------------------------------------------------

    if len(valid_candidates) == 0:

        print(
            "SELECTION → no valid enhancement "
            "candidate found"
        )

        return (
            original,
            "No Enhancement"
        )

    # --------------------------------------------------
    # SCORE CANDIDATES
    # --------------------------------------------------

    def candidate_score(item):

        metrics = item["evaluation"]

        quality_gain = (
            metrics["quality_improvement"]
        )

        exposure_gain = (
            metrics["exposure_improvement"]
        )

        structure = (
            metrics["structure_similarity"]
        )

        sharpness_multiplier = (
            metrics["sharpness_multiplier"]
        )

        noise_change = (
            metrics["noise_change"]
        )

        # Base score from actual quality improvement.
        score = (
            quality_gain * 100.0
        )

        # For low-light images, brightness correction
        # gets additional importance.
        if is_low_light:

            score += (
                max(
                    exposure_gain,
                    0.0
                )
                * 30.0
            )

        # Reward structure preservation.
        score += (
            structure * 10.0
        )

        # Penalize aggressive sharpness.
        if sharpness_multiplier > 2.0:

            score -= (
                sharpness_multiplier -
                2.0
            ) * 3.0

        # Penalize noise growth.
        if noise_change > 0:

            score -= (
                noise_change * 5.0
            )

        return score

    best = max(
        valid_candidates,
        key=candidate_score
    )

    best_candidate = best["candidate"]

    best_evaluation = best["evaluation"]

    print(
        "========================================"
    )

    print(
        "BEST CANDIDATE:",
        best_candidate["mode"]
    )

    print(
        "BEST SCORE:",
        candidate_score(best)
    )

    print(
        "QUALITY IMPROVEMENT:",
        best_evaluation[
            "quality_improvement"
        ]
    )

    print(
        "BRIGHTNESS IMPROVEMENT:",
        best_evaluation[
            "exposure_improvement"
        ]
    )

    print(
        "STRUCTURE:",
        best_evaluation[
            "structure_similarity"
        ]
    )

    print(
        "========================================"
    )

    return (
        best_candidate["image"],
        best_candidate["mode"]
    )


# --------------------------------------------------
# INTERPRETATION
# --------------------------------------------------

def generate_interpretation(
    sharpness_before,
    brightness_before,
    brightness_after,
    quality_before,
    quality_after,
    confidence_delta,
    enhancement_accepted,
    final_mode,
):
    insights = []

    # --------------------------------------------------
    # LIGHTING
    # --------------------------------------------------

    if brightness_before < 40:

        insights.append(
            "Very low-light image detected"
        )

    elif brightness_before < 70:

        insights.append(
            "Low-light image detected"
        )

    elif brightness_before < 90:

        insights.append(
            "Slightly underexposed image detected"
        )

    else:

        insights.append(
            "Image exposure was already acceptable"
        )

    # --------------------------------------------------
    # BLUR
    # --------------------------------------------------

    if sharpness_before < 10:

        insights.append(
            "Severe blur detected"
        )

    elif sharpness_before < 40:

        insights.append(
            "Moderate blur detected"
        )

    elif sharpness_before < 80:

        insights.append(
            "Mild blur detected"
        )

    else:

        insights.append(
            "Image already relatively clear"
        )

    # --------------------------------------------------
    # ENHANCEMENT
    # --------------------------------------------------

    if enhancement_accepted:

        if brightness_after > brightness_before:

            insights.append(
                "Image brightness was adaptively improved"
            )

        insights.append(
            f"Adaptive enhancement applied: "
            f"{final_mode}"
        )

        insights.append(
            "Original image structure was preserved"
        )

    else:

        insights.append(
            "No enhancement candidate provided "
            "sufficient image-quality benefit"
        )

        insights.append(
            "Original image preserved as final fallback"
        )

    # --------------------------------------------------
    # CONFIDENCE
    # --------------------------------------------------
    #
    # INFORMATIONAL ONLY.
    #

    if confidence_delta > 0:

        insights.append(
            f"AI classifier confidence changed by "
            f"+{confidence_delta * 100:.2f} "
            "percentage points"
        )

    elif confidence_delta < 0:

        insights.append(
            f"AI classifier confidence changed by "
            f"{confidence_delta * 100:.2f} "
            "percentage points"
        )

    else:

        insights.append(
            "AI classifier confidence remained unchanged"
        )

    return insights


# --------------------------------------------------
# UPLOAD
# --------------------------------------------------

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...)
):

    # --------------------------------------------------
    # READ IMAGE
    # --------------------------------------------------

    image_bytes = await file.read()

    original, candidates, _ = enhance_image(
        image_bytes
    )

    # --------------------------------------------------
    # SELECT BEST ENHANCEMENT
    # --------------------------------------------------

    final_image, final_mode = (
        select_best_candidate(
            original,
            candidates
        )
    )

    enhancement_accepted = (
        final_mode != "No Enhancement"
    )

    # --------------------------------------------------
    # FINAL IMAGE METRICS
    # --------------------------------------------------

    sharp_before = calculate_sharpness(
        original
    )

    sharp_after = calculate_sharpness(
        final_image
    )

    contrast_before = calculate_contrast(
        original
    )

    contrast_after = calculate_contrast(
        final_image
    )

    brightness_before = calculate_brightness(
        original
    )

    brightness_after = calculate_brightness(
        final_image
    )

    quality_before = quality_score(
        sharp_before,
        contrast_before,
        brightness_before
    )

    quality_after = quality_score(
        sharp_after,
        contrast_after,
        brightness_after
    )

    if quality_before > 0:

        quality_improvement = (
            quality_after -
            quality_before
        ) / quality_before

    else:

        quality_improvement = 0.0

    exposure_improvement = brightness_improvement(
        brightness_before,
        brightness_after
    )

    if sharp_before > 0:

        sharpness_multiplier = (
            sharp_after /
            sharp_before
        )

    else:

        sharpness_multiplier = 1.0

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    print(
        "========================================"
    )

    print(
        "FINAL PIPELINE RESULT"
    )

    print(
        "FINAL MODE:",
        final_mode
    )

    print(
        "ENHANCEMENT ACCEPTED:",
        enhancement_accepted
    )

    print(
        "BRIGHTNESS:",
        brightness_before,
        "→",
        brightness_after
    )

    print(
        "SHARPNESS:",
        sharp_before,
        "→",
        sharp_after
    )

    print(
        "CONTRAST:",
        contrast_before,
        "→",
        contrast_after
    )

    print(
        "QUALITY:",
        quality_before,
        "→",
        quality_after
    )

    print(
        "QUALITY IMPROVEMENT:",
        quality_improvement
    )

    print(
        "========================================"
    )

    # --------------------------------------------------
    # MODEL CONFIDENCE
    # --------------------------------------------------
    #
    # Measured AFTER image-quality selection.
    #
    # It DOES NOT decide enhancement acceptance.
    #

    confidence_before = predict_confidence(
        original
    )

    confidence_after = predict_confidence(
        final_image
    )

    confidence_delta = (
        confidence_after -
        confidence_before
    )

    print(
        "CONF BEFORE:",
        confidence_before
    )

    print(
        "CONF AFTER:",
        confidence_after
    )

    print(
        "CONF DELTA:",
        confidence_delta
    )

    # --------------------------------------------------
    # INTERPRETATION
    # --------------------------------------------------

    interpretation = generate_interpretation(
        sharp_before,
        brightness_before,
        brightness_after,
        quality_before,
        quality_after,
        confidence_delta,
        enhancement_accepted,
        final_mode,
    )

    # --------------------------------------------------
    # ENCODE FINAL IMAGE
    # --------------------------------------------------

    success, buffer = cv2.imencode(
        ".jpg",
        final_image
    )

    if not success:

        raise RuntimeError(
            "Failed to encode final image."
        )

    image_base64 = base64.b64encode(
        buffer
    ).decode("utf-8")

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------

    return {

        "image":
            image_base64,

        "mode":
            final_mode,

        "enhancement_accepted":
            enhancement_accepted,

        "metrics": {

            "brightness_before":
                brightness_before,

            "brightness_after":
                brightness_after,

            "brightness_improvement":
                exposure_improvement,

            "sharpness_before":
                sharp_before,

            "sharpness_after":
                sharp_after,

            "sharpness_multiplier":
                sharpness_multiplier,

            "contrast_before":
                contrast_before,

            "contrast_after":
                contrast_after,

            "quality_before":
                quality_before,

            "quality_after":
                quality_after,

            "quality_improvement":
                quality_improvement,
        },

        "confidence": {

            "before":
                confidence_before,

            "after":
                confidence_after,

            "delta":
                confidence_delta,

            "final":
                confidence_after,
        },

        "interpretation":
            interpretation,
    }
