from app.ml.superres_enhancer import enhance_superres
import cv2
import numpy as np


# --------------------------------------------------
# BRIGHTNESS
# --------------------------------------------------

def fix_brightness_lab(img, gamma=0.70):

    lab = cv2.cvtColor(
        img,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)

    l_norm = l / 255.0

    l_gamma = np.power(
        l_norm,
        gamma
    )

    l_out = np.clip(
        l_gamma * 255,
        0,
        255
    ).astype(np.uint8)

    lab = cv2.merge(
        (l_out, a, b)
    )

    return cv2.cvtColor(
        lab,
        cv2.COLOR_LAB2BGR
    )


# --------------------------------------------------
# METRICS
# --------------------------------------------------

def detect_blur(image):

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


def detect_brightness(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.mean(gray)
    )


def detect_contrast(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        np.std(gray)
    )


# --------------------------------------------------
# CONSERVATIVE CONTRAST ENHANCEMENT
# --------------------------------------------------

def enhance_contrast(
    image,
    clip_limit=1.2
):
    """
    Very conservative luminance-only contrast enhancement.

    This is deliberately mild because aggressive contrast
    enhancement can alter pigmentation and lesion appearance.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=clip_limit,
        tileGridSize=(8, 8)
    )

    l = clahe.apply(l)

    result = cv2.cvtColor(
        cv2.merge((l, a, b)),
        cv2.COLOR_LAB2BGR
    )

    return result


# --------------------------------------------------
# CONSERVATIVE DENOISING
# --------------------------------------------------

def reduce_noise(image):
    """
    Mild edge-preserving denoising.

    The goal is to reduce obvious sensor/compression noise
    without destroying lesion boundaries or tiny structures.
    """

    return cv2.bilateralFilter(
        image,
        d=5,
        sigmaColor=20,
        sigmaSpace=20
    )


# --------------------------------------------------
# CANDIDATE GENERATION
# --------------------------------------------------

def generate_enhancement_candidates(image):
    """
    Generate adaptive enhancement candidates.

    The enhancement layer does NOT assume that every image
    needs the same operation.

    Candidates are created according to the detected image
    degradation:

        - darkness
        - blur
        - low contrast
        - noise

    Nothing is automatically accepted here.

    The validation layer decides which candidate is safest.
    """

    if image is None:
        raise ValueError(
            "generate_enhancement_candidates received None image."
        )

    if image.dtype != np.uint8:
        image = image.astype(np.uint8)

    original = image.copy()

    brightness = detect_brightness(
        original
    )

    sharpness = detect_blur(
        original
    )

    contrast = detect_contrast(
        original
    )

    print(
        "DEBUG → brightness:",
        brightness
    )

    print(
        "DEBUG → sharpness:",
        sharpness
    )

    print(
        "DEBUG → contrast:",
        contrast
    )

    candidates = []

    # --------------------------------------------------
    # ORIGINAL
    # --------------------------------------------------

    candidates.append(
        {
            "image": original.copy(),
            "mode": "Original",
            "reason": "Original image"
        }
    )

    # --------------------------------------------------
    # BRIGHTNESS CANDIDATE
    # --------------------------------------------------

    brightness_candidate = None

    if brightness < 40:

        brightness_candidate = fix_brightness_lab(
            original,
            gamma=0.55
        )

    elif brightness < 70:

        brightness_candidate = fix_brightness_lab(
            original,
            gamma=0.70
        )

    elif brightness < 90:

        brightness_candidate = fix_brightness_lab(
            original,
            gamma=0.80
        )

    if brightness_candidate is not None:

        candidates.append(
            {
                "image": brightness_candidate,
                "mode": "Brightness Enhanced",
                "reason": "Low brightness detected"
            }
        )

    # --------------------------------------------------
    # CONTRAST CANDIDATE
    # --------------------------------------------------

    if contrast < 20:

        contrast_candidate = enhance_contrast(
            original,
            clip_limit=1.1
        )

        candidates.append(
            {
                "image": contrast_candidate,
                "mode": "Contrast Enhanced",
                "reason": "Low contrast detected"
            }
        )

    elif contrast < 30:

        contrast_candidate = enhance_contrast(
            original,
            clip_limit=1.2
        )

        candidates.append(
            {
                "image": contrast_candidate,
                "mode": "Mild Contrast Enhanced",
                "reason": "Moderately low contrast detected"
            }
        )

    # --------------------------------------------------
    # NOISE CANDIDATE
    # --------------------------------------------------

    if contrast > 0 and sharpness < 30:

        denoised = reduce_noise(
            original
        )

        candidates.append(
            {
                "image": denoised,
                "mode": "Noise Reduction",
                "reason": "Low-detail image may contain noise"
            }
        )

    # --------------------------------------------------
    # BLUR / SUPER-RESOLUTION CANDIDATE
    # --------------------------------------------------

    if sharpness < 20:

        # Severe blur:
        # NO extra artificial sharpening.
        sr_candidate = enhance_superres(
            original,
            sharpen=False,
            sharpen_strength=0.0
        )

        candidates.append(
            {
                "image": sr_candidate,
                "mode": "AI Super Resolution (severe blur)",
                "reason": "Severe blur detected"
            }
        )

    elif sharpness < 50:

        sr_candidate = enhance_superres(
            original,
            sharpen=True,
            sharpen_strength=0.20
        )

        candidates.append(
            {
                "image": sr_candidate,
                "mode": "AI Super Resolution (moderate blur)",
                "reason": "Moderate blur detected"
            }
        )

    elif sharpness < 80:

        sr_candidate = enhance_superres(
            original,
            sharpen=True,
            sharpen_strength=0.15
        )

        candidates.append(
            {
                "image": sr_candidate,
                "mode": "AI Super Resolution (mild blur)",
                "reason": "Mild blur detected"
            }
        )

    # --------------------------------------------------
    # COMBINED BRIGHTNESS + BLUR CANDIDATE
    # --------------------------------------------------

    if brightness < 90 and sharpness < 50:

        combined = original.copy()

        if brightness < 40:

            combined = fix_brightness_lab(
                combined,
                gamma=0.55
            )

        elif brightness < 70:

            combined = fix_brightness_lab(
                combined,
                gamma=0.70
            )

        else:

            combined = fix_brightness_lab(
                combined,
                gamma=0.80
            )

        combined = enhance_superres(
            combined,
            sharpen=False,
            sharpen_strength=0.0
        )

        candidates.append(
            {
                "image": combined,
                "mode": (
                    "Brightness Enhanced + "
                    "AI Super Resolution"
                ),
                "reason": (
                    "Low brightness and blur detected"
                )
            }
        )

    # --------------------------------------------------
    # DEBUG
    # --------------------------------------------------

    print(
        "DEBUG → generated candidates:",
        len(candidates)
    )

    for index, candidate in enumerate(
        candidates,
        start=1
    ):

        candidate_image = candidate["image"]

        candidate_brightness = detect_brightness(
            candidate_image
        )

        candidate_sharpness = detect_blur(
            candidate_image
        )

        candidate_contrast = detect_contrast(
            candidate_image
        )

        print(
            f"CANDIDATE {index} → "
            f"{candidate['mode']} | "
            f"brightness={candidate_brightness:.2f} | "
            f"sharpness={candidate_sharpness:.2f} | "
            f"contrast={candidate_contrast:.2f}"
        )

    return candidates


# --------------------------------------------------
# EXISTING PIPELINE INTERFACE
# --------------------------------------------------

def enhance_image(image_bytes):

    # --------------------------------------------------
    # DECODE IMAGE
    # --------------------------------------------------

    np_arr = np.frombuffer(
        image_bytes,
        np.uint8
    )

    img = cv2.imdecode(
        np_arr,
        cv2.IMREAD_COLOR
    )

    if img is None:
        raise ValueError(
            "Unable to decode uploaded image."
        )

    original = img.copy()

    # --------------------------------------------------
    # GENERATE ADAPTIVE CANDIDATES
    # --------------------------------------------------

    candidates = generate_enhancement_candidates(
        original
    )

    # --------------------------------------------------
    # TEMPORARY DEFAULT
    # --------------------------------------------------
    #
    # IMPORTANT:
    #
    # The validation layer will eventually choose the
    # best candidate.
    #
    # For now, preserve compatibility with the existing
    # upload route by returning the first non-original
    # candidate when available.
    #
    # We will replace this selection logic in upload.py
    # with proper image-quality validation.
    # --------------------------------------------------

    if len(candidates) > 1:

        selected = candidates[1]

    else:

        selected = candidates[0]

    enhanced = selected["image"]

    mode = selected["mode"]

    # --------------------------------------------------
    # FINAL DEBUG
    # --------------------------------------------------

    new_brightness = detect_brightness(
        enhanced
    )

    new_sharpness = detect_blur(
        enhanced
    )

    new_contrast = detect_contrast(
        enhanced
    )

    print(
        "DEBUG → selected mode:",
        mode
    )

    print(
        "DEBUG → brightness after:",
        new_brightness
    )

    print(
        "DEBUG → sharpness after:",
        new_sharpness
    )

    print(
        "DEBUG → contrast after:",
        new_contrast
    )

    return (
        original,
        candidates,
        mode
    )