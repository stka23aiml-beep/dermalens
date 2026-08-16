# backend/app/ml/generate_comparison_figure.py
#
# Builds a matplotlib grid figure comparing original vs enhanced images
# across representative categories (mild/moderate/severe blur, dark, etc.)
# for use in the paper. Deliberately picks one representative image PER
# CATEGORY rather than showing only the most dramatic or most stubborn
# case, so the figure reflects typical behavior, not a cherry-picked or
# worst-case single example.

import os
import glob
import cv2
import numpy as np
import matplotlib.pyplot as plt

from app.ml.enhancement import enhance_image, detect_blur
from app.ml.derm_model import load_model, predict

WEIGHTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "ml", "models", "isic_resnet18.pth"
)
_model = load_model(WEIGHTS_PATH)

# Same gate threshold used in evaluate_derm.py / upload.py -- keep in sync.
DEGRADATION_THRESHOLD = -0.02

# Glob patterns identifying each category by filename prefix, matching the
# same convention used elsewhere (dark_, blur_, motion_, noise_).
CATEGORY_PATTERNS = {
    "Dark": "dark_*",
    "Blurry": "blur_*",
    "Motion Blur": "motion_*",
    "Noisy": "noise_*",
}

EVAL_DIR = "data/eval"
OUTPUT_PATH = "reports/figures/comparison_grid.png"


def predict_confidence(image_np):
    _, confidence = predict(_model, image_np)
    return float(confidence)


def pick_representative_image(category_glob, base_dir):
    """
    Picks ONE representative image for a category: the one closest to the
    MEDIAN severity for that category, not the most extreme case. This
    avoids the figure being dominated by either an unrealistically easy
    case or an unrepresentative worst-case outlier.
    """
    paths = sorted(glob.glob(os.path.join(base_dir, category_glob)))
    if not paths:
        return None

    scored = []
    for p in paths:
        img = cv2.imread(p)
        if img is None:
            continue
        sharpness = detect_blur(img)
        scored.append((sharpness, p))

    if not scored:
        return None

    scored.sort(key=lambda x: x[0])
    median_idx = len(scored) // 2
    return scored[median_idx][1]


def build_figure(base_dir=EVAL_DIR, output_path=OUTPUT_PATH):
    rows = []

    for label, pattern in CATEGORY_PATTERNS.items():
        path = pick_representative_image(pattern, base_dir)
        if path is None:
            print(f"Skipping '{label}': no images found matching {pattern} in {base_dir}")
            continue

        img = cv2.imread(path)
        with open(path, "rb") as f:
            image_bytes = f.read()

        original, enhanced, mode = enhance_image(image_bytes)

        conf_before = predict_confidence(original)
        conf_after = predict_confidence(enhanced)
        delta = conf_after - conf_before
        accepted = delta >= DEGRADATION_THRESHOLD

        final_image = enhanced if accepted else original
        final_conf = conf_after if accepted else conf_before

        rows.append({
            "label": label,
            "filename": os.path.basename(path),
            "original": cv2.cvtColor(original, cv2.COLOR_BGR2RGB),
            "final": cv2.cvtColor(final_image, cv2.COLOR_BGR2RGB),
            "mode": mode,
            "conf_before": conf_before,
            "conf_after": final_conf,
            "accepted": accepted,
        })

    if not rows:
        raise RuntimeError(
            f"No images found in {base_dir}. Check EVAL_DIR points to your "
            f"actual degraded test image folder."
        )

    n = len(rows)
    fig, axes = plt.subplots(n, 2, figsize=(11, 4.5 * n))
    if n == 1:
        axes = axes.reshape(1, 2)

    for i, row in enumerate(rows):
        axes[i, 0].imshow(row["original"])
        axes[i, 0].set_title(
            f"{row['label']} — Original\nconf={row['conf_before']*100:.1f}%",
            fontsize=10
        )
        axes[i, 0].axis("off")

        gate_note = "" if row["accepted"] else " (reverted)"
        axes[i, 1].imshow(row["final"])
        axes[i, 1].set_title(
            f"{row['label']} — Result{gate_note}\n"
            f"conf={row['conf_after']*100:.1f}%  |  {row['mode']}",
            fontsize=9
        )
        axes[i, 1].axis("off")

    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"\nComparison figure saved to {output_path}")


if __name__ == "__main__":
    build_figure()