import cv2
import numpy as np


def calculate_sharpness(image):
    """
    Measures high-frequency detail using Laplacian variance.

    Higher values generally indicate more visible edges/detail,
    but very high values can also come from noise or artifacts.
    """
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()
    )


def calculate_contrast(image):
    """
    Measures global grayscale contrast.
    """
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        gray.std()
    )


def calculate_brightness(image):
    """
    Measures mean luminance.

    OpenCV images are BGR. We convert to grayscale and
    calculate the mean intensity on a 0-255 scale.

    Rough interpretation:
        0-40   -> very dark
        40-70  -> dark
        70-90  -> somewhat dark
        90-180 -> generally usable
        >180   -> potentially very bright
    """
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        gray.mean()
    )


def detect_blur(image):
    """
    Semantic alias for sharpness-based blur detection.
    """
    return calculate_sharpness(image)


def brightness_improvement(
    brightness_before,
    brightness_after
):
    """
    Measures whether brightness moved toward a useful range.

    For dark images, an increase is beneficial.

    For already-bright images, excessive brightening is not
    considered an improvement.
    """

    # Very dark image
    if brightness_before < 40:

        target = 100.0

        before_distance = abs(
            brightness_before - target
        )

        after_distance = abs(
            brightness_after - target
        )

        return (
            before_distance -
            after_distance
        )

    # Dark image
    elif brightness_before < 70:

        target = 110.0

        before_distance = abs(
            brightness_before - target
        )

        after_distance = abs(
            brightness_after - target
        )

        return (
            before_distance -
            after_distance
        )

    # Slightly dark image
    elif brightness_before < 90:

        target = 120.0

        before_distance = abs(
            brightness_before - target
        )

        after_distance = abs(
            brightness_after - target
        )

        return (
            before_distance -
            after_distance
        )

    # Already reasonably exposed.
    # Don't reward unnecessary brightness changes.
    return 0.0


def quality_score(
    sharpness,
    contrast,
    brightness=None
):
    """
    Composite image-quality score.

    This is intentionally conservative.

    Sharpness:
        50%

    Contrast:
        30%

    Brightness:
        20%

    Brightness is optional for backwards compatibility.
    """

    # --------------------------------------------------
    # SHARPNESS
    # --------------------------------------------------

    sharp_norm = min(
        sharpness / 500.0,
        1.0
    )

    # --------------------------------------------------
    # CONTRAST
    # --------------------------------------------------

    contrast_norm = min(
        contrast / 100.0,
        1.0
    )

    # --------------------------------------------------
    # BRIGHTNESS
    # --------------------------------------------------

    if brightness is None:

        brightness_norm = 0.5

    else:

        # Peak usefulness around ~120.
        #
        # This avoids rewarding an image simply because
        # it became brighter.
        brightness_distance = abs(
            brightness - 120.0
        )

        brightness_norm = max(
            0.0,
            1.0 - (
                brightness_distance / 120.0
            )
        )

    # --------------------------------------------------
    # FINAL SCORE
    # --------------------------------------------------

    score = (
        0.50 * sharp_norm
        +
        0.30 * contrast_norm
        +
        0.20 * brightness_norm
    )

    return float(
        score * 100.0
    )