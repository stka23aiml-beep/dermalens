# backend/app/ml/evaluate_derm.py

import os
import csv
import time
import cv2
import numpy as np

from app.ml.enhancement import enhance_image, detect_blur
from app.ml.derm_model import load_model, predict

from app.evaluation.quality_metrics import (
    calculate_psnr,
    calculate_ssim
)

# path to weights
WEIGHTS_PATH = "app/ml/models/isic_resnet18.pth"

# load model once
model = load_model(WEIGHTS_PATH)

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_OUTPUT_PATH = os.path.join(_BASE_DIR, "reports/evaluation_results.csv")

CATEGORY_PREFIXES = ["dark", "blur", "motion", "noise"]


def predict_confidence(image):
    _, confidence = predict(model, image)
    return float(confidence)


def calculate_contrast(image):
    """
    ASSUMPTION: no existing contrast function was imported, so this uses
    grayscale standard deviation as a simple contrast proxy.
    Swap this out if you already have a proper contrast metric defined
    elsewhere in quality_metrics.py.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return float(gray.std())


def quality_score(sharpness, contrast):
    """
    ASSUMPTION: no formal "quality" definition was given, so this is a
    simple normalized weighted combination of sharpness and contrast
    (60/40 weighting, each scaled by a rough working-range constant).
    Replace the weights/scaling with your paper's actual quality
    definition once you have one -- treat this as a placeholder, not
    something to cite as-is.
    """
    norm_sharpness = min(sharpness / 100.0, 1.0)
    norm_contrast = min(contrast / 80.0, 1.0)
    return round((0.6 * norm_sharpness + 0.4 * norm_contrast) * 100, 2)


def get_category(filename):
    for prefix in CATEGORY_PREFIXES:
        if filename.startswith(prefix + "_"):
            return prefix
    return "original"


def evaluate(image_path):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    full_path = os.path.join(base_dir, image_path)

    img = cv2.imread(full_path)
    if img is None:
        print(f"Skipping {image_path} (not found)")
        return None

    start_time = time.time()

    filename = os.path.basename(image_path)
    category = get_category(filename)

    # ---- BEFORE metrics ----
    sharpness_before = detect_blur(img)
    contrast_before = calculate_contrast(img)
    quality_before = quality_score(sharpness_before, contrast_before)
    cls_o, conf_o = predict(model, img)

    # -----------------------------
    # LOAD ORIGINAL REFERENCE IMAGE
    # -----------------------------
    reference_name = (
        filename
        .replace("dark_", "")
        .replace("blur_", "")
        .replace("motion_", "")
        .replace("noise_", "")
    )

    reference_path = os.path.join(base_dir, "data/eval", reference_name)
    reference = cv2.imread(reference_path)

    # ---- ENHANCEMENT ----
    with open(full_path, "rb") as f:
        image_bytes = f.read()

    # CONFIRMED against enhancement.py: enhance_image returns
    # (original, enhanced, mode) where mode is a string like
    # "Brightness Enhanced + AI Super Resolution" or "No Enhancement".
    _, enhanced, mode = enhance_image(image_bytes)

    # ---- AFTER metrics ----
    sharpness_after = detect_blur(enhanced)
    contrast_after = calculate_contrast(enhanced)
    quality_after = quality_score(sharpness_after, contrast_after)
    cls_e, conf_e = predict(model, enhanced)

    delta = conf_e - conf_o

    # ---- VALIDATION GATE ----
    # Reject the enhancement if it degrades classifier confidence beyond
    # a noise-tolerance threshold (reuses the same 0.02 band used for the
    # improved/degraded/unchanged classification below), and fall back to
    # the original image's prediction. This does NOT prove the original
    # is diagnostically "correct" -- the classifier itself can be wrong --
    # it only avoids accepting an enhancement that measurably hurt the
    # model's confidence.
    DEGRADATION_THRESHOLD = -0.02
    enhancement_accepted = delta >= DEGRADATION_THRESHOLD

    if enhancement_accepted:
        final_cls, final_conf = cls_e, conf_e
    else:
        final_cls, final_conf = cls_o, conf_o

    # ---- FULL-REFERENCE metrics (PSNR / SSIM) ----
    psnr_val = None
    ssim_val = None
    if reference is not None:
        ref_for_metrics = reference
        enh_for_metrics = enhanced

        if ref_for_metrics.shape != enh_for_metrics.shape:
            ref_for_metrics = cv2.resize(
                ref_for_metrics,
                (enh_for_metrics.shape[1], enh_for_metrics.shape[0])
            )

        psnr_val = calculate_psnr(ref_for_metrics, enh_for_metrics)
        ssim_val = calculate_ssim(ref_for_metrics, enh_for_metrics)

    elapsed = time.time() - start_time

    # ---- PRINT ----
    print("\n---", image_path, f"({category}) ---")
    print(f"Mode       → {mode}")
    print(f"Sharpness  → {round(sharpness_before, 2)} → {round(sharpness_after, 2)}")
    print(f"Contrast   → {round(contrast_before, 2)} → {round(contrast_after, 2)}")
    print(f"Quality    → {quality_before} → {quality_after}")
    print(f"Confidence → {cls_o} ({round(conf_o, 4)}) → {cls_e} ({round(conf_e, 4)})")
    print(f"Delta      → {round(delta, 4)}")
    if psnr_val is not None:
        print(f"PSNR       → {round(psnr_val, 4)}")
        print(f"SSIM       → {round(ssim_val, 4)}")
    else:
        print(f"Reference  → not found at {reference_path}, skipping PSNR/SSIM")
    print(f"Time       → {round(elapsed, 3)}s")

    if enhancement_accepted:
        print(f"Gate       → ✔ Enhancement ACCEPTED (using enhanced, conf={round(final_conf,4)})")
    else:
        print(f"Gate       → ✘ Enhancement REJECTED (falling back to original, conf={round(final_conf,4)})")

    if delta > 0.02:
        print("✔ Improvement")
    elif delta < -0.02:
        print("⚠ Degradation")
    else:
        print("~ No significant change")

    return {
        "image": image_path,
        "category": category,
        "mode": mode,
        "sharpness_before": round(sharpness_before, 4),
        "sharpness_after": round(sharpness_after, 4),
        "contrast_before": round(contrast_before, 4),
        "contrast_after": round(contrast_after, 4),
        "quality_before": quality_before,
        "quality_after": quality_after,
        "confidence_before": round(conf_o, 4),
        "confidence_after": round(conf_e, 4),
        "delta": round(delta, 4),
        "enhancement_accepted": enhancement_accepted,
        "final_class": final_cls,
        "final_confidence": round(final_conf, 4),
        "psnr": round(psnr_val, 4) if psnr_val is not None else "",
        "ssim": round(ssim_val, 4) if ssim_val is not None else "",
        "time_sec": round(elapsed, 4),
    }


def write_csv(rows, output_path):
    if not rows:
        print("No rows to write, skipping CSV.")
        return

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    fieldnames = [
        "image", "category", "mode",
        "sharpness_before", "sharpness_after",
        "contrast_before", "contrast_after",
        "quality_before", "quality_after",
        "confidence_before", "confidence_after",
        "delta",
        "enhancement_accepted", "final_class", "final_confidence",
        "psnr", "ssim",
        "time_sec",
    ]

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"\nCSV written to {output_path}")


if __name__ == "__main__":

    images = [
        "sample.jpg",
        "data/bad_blur.jpg",
        "data/bad_dark.jpg",
        "data/bad_noise.jpg",
        "data/test/badd.jpeg",
        "data/test/image.jpg",
    ]

    results = []
    deltas = []
    sharpness_gains = []
    quality_gains = []
    improved = 0
    degraded = 0
    unchanged = 0

    for img_path in images:
        result = evaluate(img_path)

        if result is None:
            continue

        results.append(result)
        deltas.append(result["delta"])
        sharpness_gains.append(result["sharpness_after"] - result["sharpness_before"])
        quality_gains.append(result["quality_after"] - result["quality_before"])

        if result["delta"] > 0.02:
            improved += 1
        elif result["delta"] < -0.02:
            degraded += 1
        else:
            unchanged += 1

    gate_rejected = sum(1 for r in results if not r["enhancement_accepted"])
    gate_accepted = len(results) - gate_rejected

    write_csv(results, CSV_OUTPUT_PATH)

    # FINAL SUMMARY
    if results:
        psnr_vals = [r["psnr"] for r in results if r["psnr"] != ""]
        ssim_vals = [r["ssim"] for r in results if r["ssim"] != ""]

        print("\n========== FINAL REPORT ==========")
        print("Images Evaluated       :", len(results))
        print("Avg Sharpness Gain (abs):", round(float(np.mean(sharpness_gains)), 4))
        print("Avg Quality Gain (abs)  :", round(float(np.mean(quality_gains)), 4))
        print("Avg Confidence Δ        :", round(float(np.mean(deltas)), 4))
        if psnr_vals:
            print("Average PSNR            :", round(float(np.mean(psnr_vals)), 2), "dB")
        if ssim_vals:
            print("Average SSIM            :", round(float(np.mean(ssim_vals)), 4))
        print("Improved                :", improved)
        print("Degraded                :", degraded)
        print("Unchanged               :", unchanged)
        print("Gate Accepted           :", gate_accepted)
        print("Gate Rejected           :", gate_rejected)
        print("===================================")