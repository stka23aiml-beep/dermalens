# backend/app/evaluation/quality_metrics.py
#
# Full-reference image quality metrics (PSNR, SSIM) comparing an enhanced
# image against a clean ground-truth reference. Requires scikit-image --
# add `scikit-image` to requirements.txt if it isn't already there.

import numpy as np

from skimage.metrics import peak_signal_noise_ratio, structural_similarity


def calculate_psnr(reference, enhanced):
    """
    Peak Signal-to-Noise Ratio between two images.

    Args:
        reference: ground-truth image, BGR uint8 numpy array (cv2 format)
        enhanced:  enhanced image, BGR uint8 numpy array (cv2 format),
                   same shape as reference

    Returns:
        PSNR in dB (float). Higher is better. Identical images -> inf,
        which is clamped to 100.0 to keep downstream averaging finite.
    """
    ref = reference.astype(np.float64)
    enh = enhanced.astype(np.float64)

    if ref.shape != enh.shape:
        raise ValueError(
            f"calculate_psnr: shape mismatch {ref.shape} vs {enh.shape} -- "
            "resize images to match before calling this function"
        )

    value = peak_signal_noise_ratio(ref, enh, data_range=255)

    if np.isinf(value):
        return 100.0

    return float(value)


def calculate_ssim(reference, enhanced):
    """
    Structural Similarity Index between two images.

    Args:
        reference: ground-truth image, BGR uint8 numpy array (cv2 format)
        enhanced:  enhanced image, BGR uint8 numpy array (cv2 format),
                   same shape as reference

    Returns:
        SSIM in [0, 1] (float). Higher is better / more structurally similar.
    """
    if reference.shape != enhanced.shape:
        raise ValueError(
            f"calculate_ssim: shape mismatch {reference.shape} vs {enhanced.shape} -- "
            "resize images to match before calling this function"
        )

    # Color image (H, W, 3) -> channel_axis=-1 tells skimage to compute
    # SSIM per-channel and average, rather than collapsing to grayscale.
    value = structural_similarity(
        reference,
        enhanced,
        channel_axis=-1,
        data_range=255
    )

    return float(value)