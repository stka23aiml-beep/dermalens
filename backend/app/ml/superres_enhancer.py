from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np


# --------------------------------------------------
# MODEL PATH
# --------------------------------------------------

WEIGHTS_PATH = (
    Path(__file__).resolve().parent / "weights" / "EDSR_x2.pb"
)


# --------------------------------------------------
# REAL-ESRGAN MODEL PATH
# --------------------------------------------------

REALESRGAN_WEIGHTS_PATH = (
    Path(__file__).resolve().parent
    / "realesrgan_weights"
    / "realesr-general-x4v3.pth"
)


# --------------------------------------------------
# PERFORMANCE
# --------------------------------------------------

# EDSR is expensive on CPU.
# Only use it directly for genuinely small images.
MAX_EDSR_SIZE = 128


# Real-ESRGAN is deliberately NOT used automatically.
# Your CPU test took ~85 seconds on a large image.
USE_REALESRGAN_BY_DEFAULT = False


# --------------------------------------------------
# EDSR MODEL
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_sr_model():

    if not WEIGHTS_PATH.exists():

        raise FileNotFoundError(
            f"Super-resolution weights not found at "
            f"{WEIGHTS_PATH}"
        )

    print(
        "SR MODEL → loading weights from:",
        WEIGHTS_PATH
    )

    sr = cv2.dnn_superres.DnnSuperResImpl_create()

    sr.readModel(
        str(WEIGHTS_PATH)
    )

    sr.setModel(
        "edsr",
        2
    )

    print(
        "SR MODEL → loaded successfully"
    )

    return sr


# --------------------------------------------------
# REAL-ESRGAN MODEL
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_realesrgan_model():

    if not REALESRGAN_WEIGHTS_PATH.exists():

        raise FileNotFoundError(
            f"Real-ESRGAN weights not found at "
            f"{REALESRGAN_WEIGHTS_PATH}"
        )

    try:

        import torch

        from realesrgan import RealESRGANer

        from realesrgan.archs.srvgg_arch import (
            SRVGGNetCompact
        )

    except ImportError as exc:

        raise ImportError(
            "Real-ESRGAN dependencies are not available."
        ) from exc

    print(
        "REAL-ESRGAN → loading weights from:",
        REALESRGAN_WEIGHTS_PATH
    )

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    model = SRVGGNetCompact(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_conv=32,
        upscale=4,
        act_type="prelu"
    )

    upsampler = RealESRGANer(
        scale=4,
        model_path=str(
            REALESRGAN_WEIGHTS_PATH
        ),
        model=model,
        tile=128,
        tile_pad=10,
        pre_pad=0,
        half=False,
        device=device,
    )

    print(
        "REAL-ESRGAN → loaded successfully"
    )

    return upsampler


# --------------------------------------------------
# BASIC HELPERS
# --------------------------------------------------

def _blend_with_original(
    original,
    enhanced,
    strength
):
    """
    Blend enhancement with the original image.

    strength:
        0.0 = completely original
        1.0 = completely enhanced

    Keeping this below 1.0 prevents the enhancement
    from completely replacing the source image.
    """

    strength = float(
        np.clip(
            strength,
            0.0,
            1.0
        )
    )

    if strength <= 0:

        return original.copy()

    if strength >= 1:

        return enhanced.copy()

    blended = cv2.addWeighted(
        original,
        1.0 - strength,
        enhanced,
        strength,
        0
    )

    return blended


# --------------------------------------------------
# ADAPTIVE CLAHE
# --------------------------------------------------

def _adaptive_clahe(
    image,
    strength=0.25
):
    """
    Conservative CLAHE enhancement.

    CLAHE is retained, but its effect is intentionally
    limited because aggressive local contrast enhancement
    can exaggerate skin texture and image noise.
    """

    lab = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2LAB
    )

    l, a, b = cv2.split(
        lab
    )

    clahe = cv2.createCLAHE(
        clipLimit=1.15,
        tileGridSize=(8, 8)
    )

    l_enhanced = clahe.apply(
        l
    )

    clahe_result = cv2.cvtColor(
        cv2.merge(
            (
                l_enhanced,
                a,
                b
            )
        ),
        cv2.COLOR_LAB2BGR
    )

    return _blend_with_original(
        image,
        clahe_result,
        strength
    )


# --------------------------------------------------
# ADAPTIVE SHARPEN
# --------------------------------------------------

def _adaptive_sharpen(
    image,
    strength=0.10
):
    """
    Very mild unsharp masking.

    This is deliberately conservative to avoid
    amplifying skin texture and compression artifacts.
    """

    if strength <= 0:

        return image.copy()

    blurred = cv2.GaussianBlur(
        image,
        (0, 0),
        sigmaX=1.0
    )

    sharpened = cv2.addWeighted(
        image,
        1.0 + strength,
        blurred,
        -strength,
        0
    )

    return np.clip(
        sharpened,
        0,
        255
    ).astype(np.uint8)


# --------------------------------------------------
# CONSERVATIVE DENOISING
# --------------------------------------------------

def _adaptive_denoise(
    image,
    strength=0.25
):
    """
    Conservative denoising.

    The purpose is to reduce random sensor/compression
    noise BEFORE sharpening or restoration.

    It deliberately avoids aggressive smoothing because
    small lesion structures and pigmentation must survive.
    """

    strength = float(
        np.clip(
            strength,
            0.0,
            1.0
        )
    )

    if strength <= 0:

        return image.copy()

    # Small bilateral filter preserves edges much better
    # than aggressive Gaussian smoothing.
    filtered = cv2.bilateralFilter(
        image,
        d=5,
        sigmaColor=20,
        sigmaSpace=20
    )

    return _blend_with_original(
        image,
        filtered,
        strength
    )


# --------------------------------------------------
# FULL-RESOLUTION ENHANCEMENT
# --------------------------------------------------

def _lightweight_enhancement(
    image,
    enhancement_strength=0.25,
    sharpen_strength=0.10,
    denoise_strength=0.0
):
    """
    Full-resolution adaptive enhancement.

    Keeps the original resolution and applies:

        optional denoising
        +
        conservative local contrast
        +
        very mild sharpening

    The original image remains dominant.
    """

    # --------------------------------------------------
    # DENOISE FIRST
    # --------------------------------------------------

    if denoise_strength > 0:

        denoised = _adaptive_denoise(
            image,
            strength=denoise_strength
        )

    else:

        denoised = image.copy()

    # --------------------------------------------------
    # LOCAL CONTRAST
    # --------------------------------------------------

    contrast_enhanced = _adaptive_clahe(
        denoised,
        strength=enhancement_strength
    )

    # --------------------------------------------------
    # VERY LIGHT SHARPENING
    # --------------------------------------------------

    sharpened = _adaptive_sharpen(
        contrast_enhanced,
        strength=sharpen_strength
    )

    # --------------------------------------------------
    # FINAL ORIGINAL-BLEND
    # --------------------------------------------------

    result = _blend_with_original(
        image,
        sharpened,
        strength=min(
            enhancement_strength,
            0.30
        )
    )

    return result


# --------------------------------------------------
# EDSR
# --------------------------------------------------

def _edsr_enhancement(
    image,
    sharpen=True,
    sharpen_strength=0.10
):
    """
    EDSR enhancement for small images.

    No destructive downscaling is performed here.
    """

    sr = get_sr_model()

    h, w = image.shape[:2]

    print(
        f"SR → EDSR input: {w}x{h}"
    )

    result = sr.upsample(
        image
    )

    print(
        "SR → EDSR output:",
        f"{result.shape[1]}x{result.shape[0]}"
    )

    # --------------------------------------------------
    # OPTIONAL VERY LIGHT SHARPENING
    # --------------------------------------------------

    if sharpen and sharpen_strength > 0:

        result = _adaptive_sharpen(
            result,
            strength=sharpen_strength
        )

    # --------------------------------------------------
    # EDSR BLEND
    # --------------------------------------------------

    original_resized = cv2.resize(
        image,
        (
            result.shape[1],
            result.shape[0]
        ),
        interpolation=cv2.INTER_CUBIC
    )

    result = _blend_with_original(
        original_resized,
        result,
        strength=0.35
    )

    return result


# --------------------------------------------------
# REAL-ESRGAN CANDIDATE
# --------------------------------------------------

def _realesrgan_enhancement(
    image,
    outscale=2
):
    """
    Optional Real-ESRGAN restoration candidate.

    This is NOT part of the default pipeline because
    CPU inference is expensive.

    It can be explicitly requested for experimentation.
    """

    upsampler = get_realesrgan_model()

    print(
        "REAL-ESRGAN → running candidate"
    )

    output, _ = upsampler.enhance(
        image,
        outscale=outscale
    )

    print(
        "REAL-ESRGAN → output:",
        f"{output.shape[1]}x{output.shape[0]}"
    )

    return output


# --------------------------------------------------
# ADAPTIVE SUPER RESOLUTION
# --------------------------------------------------

def enhance_superres(
    image,
    sharpen=True,
    sharpen_strength=0.10,
    denoise_strength=0.0,
    use_realesrgan=False
):
    """
    Adaptive enhancement.

    Small images:
        EDSR x2 with conservative blending.

    Large images:
        Full-resolution adaptive CLAHE,
        optional denoising,
        very mild sharpening.

    Real-ESRGAN:
        Available as an explicit candidate,
        but disabled by default.

    The original image is never aggressively replaced.
    """

    if image is None:

        raise ValueError(
            "enhance_superres received None image."
        )

    if image.dtype != np.uint8:

        image = image.astype(
            np.uint8
        )

    h, w = image.shape[:2]

    print(
        f"SR → original size: {w}x{h}"
    )

    longest_side = max(
        h,
        w
    )

    # --------------------------------------------------
    # OPTIONAL REAL-ESRGAN
    # --------------------------------------------------

    if use_realesrgan:

        print(
            "SR → using Real-ESRGAN candidate"
        )

        return _realesrgan_enhancement(
            image,
            outscale=2
        )

    # --------------------------------------------------
    # SMALL IMAGE → EDSR
    # --------------------------------------------------

    if longest_side <= MAX_EDSR_SIZE:

        print(
            "SR → using adaptive EDSR"
        )

        return _edsr_enhancement(
            image,
            sharpen=sharpen,
            sharpen_strength=min(
                sharpen_strength,
                0.15
            )
        )

    # --------------------------------------------------
    # LARGE IMAGE → FULL RESOLUTION
    # --------------------------------------------------

    print(
        "SR → image too large for CPU EDSR"
    )

    print(
        "SR → using adaptive full-resolution enhancement"
    )

    # --------------------------------------------------
    # ADAPTIVE STRENGTH
    # --------------------------------------------------

    adaptive_strength = float(
        np.clip(
            enhancement_strength_from_image(
                image
            ),
            0.10,
            0.30
        )
    )

    adaptive_sharpen = min(
        max(
            sharpen_strength,
            0.0
        ),
        0.12
    )

    adaptive_denoise = min(
        max(
            denoise_strength,
            0.0
        ),
        0.40
    )

    print(
        f"SR → contrast strength: "
        f"{adaptive_strength:.2f}"
    )

    print(
        f"SR → sharpen strength: "
        f"{adaptive_sharpen:.2f}"
    )

    print(
        f"SR → denoise strength: "
        f"{adaptive_denoise:.2f}"
    )

    return _lightweight_enhancement(
        image,
        enhancement_strength=adaptive_strength,
        sharpen_strength=adaptive_sharpen,
        denoise_strength=adaptive_denoise
    )


# --------------------------------------------------
# IMAGE-BASED ENHANCEMENT STRENGTH
# --------------------------------------------------

def enhancement_strength_from_image(
    image
):
    """
    Estimate how aggressively the image needs
    local enhancement.

    The goal is NOT to maximize sharpness.

    Lower-quality / darker images get slightly more
    enhancement, while already-clear images stay close
    to the original.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(
        np.mean(gray)
    )

    contrast = float(
        np.std(gray)
    )

    # --------------------------------------------------
    # BRIGHTNESS FACTOR
    # --------------------------------------------------

    if brightness < 50:

        brightness_factor = 0.30

    elif brightness < 80:

        brightness_factor = 0.24

    elif brightness < 110:

        brightness_factor = 0.18

    else:

        brightness_factor = 0.12

    # --------------------------------------------------
    # CONTRAST FACTOR
    # --------------------------------------------------

    if contrast < 25:

        contrast_factor = 0.30

    elif contrast < 40:

        contrast_factor = 0.22

    elif contrast < 55:

        contrast_factor = 0.16

    else:

        contrast_factor = 0.10

    # --------------------------------------------------
    # COMBINE
    # --------------------------------------------------

    strength = (
        brightness_factor
        + contrast_factor
    ) / 2.0

    return float(
        np.clip(
            strength,
            0.10,
            0.30
        )
    )


# --------------------------------------------------
# NOISE ESTIMATION
# --------------------------------------------------

def estimate_noise(
    image
):
    """
    Estimate high-frequency noise using the difference
    between the image and a small Gaussian-smoothed
    version.

    This is deliberately a heuristic metric, not a
    medical/noise classifier.
    """

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (3, 3),
        0
    )

    residual = (
        gray.astype(np.float32)
        -
        blurred.astype(np.float32)
    )

    return float(
        np.std(residual)
    )


# --------------------------------------------------
# BLUR SEVERITY
# --------------------------------------------------

def estimate_blur(
    image
):
    """
    Laplacian-variance blur indicator.

    Lower values generally indicate less visible
    high-frequency structure.

    This is only a heuristic and can also respond to
    noise/texture.
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


# --------------------------------------------------
# CANDIDATE GENERATION
# --------------------------------------------------

def generate_enhancement_candidates(
    image
):
    """
    Generate conservative enhancement candidates.

    IMPORTANT:
        The original image is always candidate 0.

    The pipeline can therefore fall back to the original
    only after all reasonable candidates have been evaluated.
    """

    candidates = []

    # --------------------------------------------------
    # ORIGINAL
    # --------------------------------------------------

    candidates.append(
        (
            "Original",
            image.copy()
        )
    )

    # --------------------------------------------------
    # IMAGE CONDITIONS
    # --------------------------------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(
        gray.mean()
    )

    contrast = float(
        gray.std()
    )

    blur = estimate_blur(
        image
    )

    noise = estimate_noise(
        image
    )

    print(
        "CANDIDATES → brightness:",
        brightness
    )

    print(
        "CANDIDATES → contrast:",
        contrast
    )

    print(
        "CANDIDATES → blur:",
        blur
    )

    print(
        "CANDIDATES → noise:",
        noise
    )

    # --------------------------------------------------
    # LOW LIGHT CANDIDATE
    # --------------------------------------------------

    if brightness < 90:

        if brightness < 40:

            gamma = 0.55

        elif brightness < 70:

            gamma = 0.70

        else:

            gamma = 0.80

        lab = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2LAB
        )

        l, a, b = cv2.split(
            lab
        )

        l_norm = l / 255.0

        l_gamma = np.power(
            l_norm,
            gamma
        )

        l_out = np.clip(
            l_gamma * 255,
            0,
            255
        ).astype(
            np.uint8
        )

        brightness_candidate = cv2.cvtColor(
            cv2.merge(
                (
                    l_out,
                    a,
                    b
                )
            ),
            cv2.COLOR_LAB2BGR
        )

        # Keep some original information.
        brightness_candidate = _blend_with_original(
            image,
            brightness_candidate,
            0.80
        )

        candidates.append(
            (
                "Brightness Correction",
                brightness_candidate
            )
        )

    # --------------------------------------------------
    # NOISE CANDIDATE
    # --------------------------------------------------

    if noise > 8:

        denoised = _adaptive_denoise(
            image,
            strength=0.35
        )

        candidates.append(
            (
                "Conservative Denoising",
                denoised
            )
        )

    # --------------------------------------------------
    # LOW CONTRAST CANDIDATE
    # --------------------------------------------------

    if contrast < 55:

        contrast_candidate = _adaptive_clahe(
            image,
            strength=0.20
        )

        candidates.append(
            (
                "Local Contrast Enhancement",
                contrast_candidate
            )
        )

    # --------------------------------------------------
    # BLUR CANDIDATE
    # --------------------------------------------------

    if blur < 80:

        # Denoise first if the image is noisy.
        blur_input = image

        if noise > 8:

            blur_input = _adaptive_denoise(
                image,
                strength=0.25
            )

        blur_candidate = enhance_superres(
            blur_input,
            sharpen=blur >= 20,
            sharpen_strength=(
                0.05
                if blur < 20
                else 0.08
            ),
            denoise_strength=0.0,
            use_realesrgan=False
        )

        candidates.append(
            (
                "Conservative Blur Restoration",
                blur_candidate
            )
        )

    # --------------------------------------------------
    # COMBINED CANDIDATE
    # --------------------------------------------------

    if (
        brightness < 90
        and
        (
            blur < 80
            or
            noise > 8
            or
            contrast < 55
        )
    ):

        combined = image.copy()

        # Brightness first.
        if brightness < 90:

            if brightness < 40:

                gamma = 0.55

            elif brightness < 70:

                gamma = 0.70

            else:

                gamma = 0.80

            lab = cv2.cvtColor(
                combined,
                cv2.COLOR_BGR2LAB
            )

            l, a, b = cv2.split(
                lab
            )

            l_norm = l / 255.0

            l_gamma = np.power(
                l_norm,
                gamma
            )

            l_out = np.clip(
                l_gamma * 255,
                0,
                255
            ).astype(
                np.uint8
            )

            combined = cv2.cvtColor(
                cv2.merge(
                    (
                        l_out,
                        a,
                        b
                    )
                ),
                cv2.COLOR_LAB2BGR
            )

        # Denoise second.
        if noise > 8:

            combined = _adaptive_denoise(
                combined,
                strength=0.25
            )

        # Contrast third.
        if contrast < 55:

            combined = _adaptive_clahe(
                combined,
                strength=0.15
            )

        # Very mild detail recovery last.
        if blur < 80:

            combined = _adaptive_sharpen(
                combined,
                strength=0.05
            )

        combined = _blend_with_original(
            image,
            combined,
            0.70
        )

        candidates.append(
            (
                "Combined Adaptive Enhancement",
                combined
            )
        )

    print(
        "CANDIDATES → generated:",
        len(candidates)
    )

    for name, _ in candidates:

        print(
            "CANDIDATE →",
            name
        )

    return candidates