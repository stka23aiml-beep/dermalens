# backend/app/ml/evaluate_derm.py

import os
import cv2
import numpy as np
import pandas as pd


from app.ml.enhancement import enhance_image, detect_blur
from app.ml.derm_model import load_model, predict

from app.ml.metrics import (
    calculate_sharpness,
    calculate_contrast,
    quality_score
)

# path to weights
WEIGHTS_PATH = "app/ml/models/isic_resnet18.pth"

# load model once
model = load_model(WEIGHTS_PATH)

def evaluate(image_path):

    base_dir = os.path.dirname(
        os.path.dirname(
            os.path.dirname(__file__)
        )
    )

    full_path = os.path.join(
        base_dir,
        image_path
    )

    img = cv2.imread(full_path)

    if img is None:

        print(
            f"Skipping {image_path} (not found)"
        )

        return None

    # ORIGINAL METRICS
    sharp_before = calculate_sharpness(img)

    contrast_before = calculate_contrast(
        img
    )

    quality_before = quality_score(
        sharp_before,
        contrast_before
    )

    # ORIGINAL PREDICTION
    cls_o, conf_o = predict(
        model,
        img
    )

    # ENHANCE IMAGE
    with open(full_path, "rb") as f:

        image_bytes = f.read()

    _, enhanced, mode = enhance_image(
        image_bytes
    )

    # ENHANCED METRICS
    sharp_after = calculate_sharpness(
        enhanced
    )

    contrast_after = calculate_contrast(
        enhanced
    )

    quality_after = quality_score(
        sharp_after,
        contrast_after
    )

    # ENHANCED PREDICTION
    cls_e, conf_e = predict(
        model,
        enhanced
    )

    delta = conf_e - conf_o

    print("\n---", image_path, "---")

    print(
        f"Sharpness: {round(sharp_before,2)} -> {round(sharp_after,2)}"
    )

    print(
        f"Quality: {round(quality_before,2)} -> {round(quality_after,2)}"
    )

    print(
        f"Confidence: {round(conf_o,4)} -> {round(conf_e,4)}"
    )

    print(
        f"Delta: {round(delta,4)}"
    )


    filename = os.path.basename(image_path)

    if filename.startswith("dark_"):
        category = "dark"

    elif filename.startswith("blur_"):
        category = "blur"

    elif filename.startswith("motion_"):
        category = "motion"

    elif filename.startswith("noise_"):
        category = "noise"

    else:
        category = "original"

    return {

        "image": image_path,

        "category": category,

        "mode": mode,

        "sharpness_before":
        sharp_before,

        "sharpness_after":
        sharp_after,

        "contrast_before":
        contrast_before,

        "contrast_after":
        contrast_after,

        "quality_before":
        quality_before,

        "quality_after":
        quality_after,

        "confidence_before":
        conf_o,

        "confidence_after":
        conf_e,

        "confidence_delta":
        delta
    }




if __name__ == "__main__":

    images = []

    for file in os.listdir("data/eval"):

        images.append(
            f"data/eval/{file}"
        )

    deltas = []
    improved = 0
    degraded = 0

    results = []

    for img_path in images:

        result = evaluate(img_path)

        if result is None:
            continue

        results.append(result)

        delta = result["confidence_delta"]

        deltas.append(delta)

        if delta > 0.02:
            improved += 1

        elif delta < -0.02:
            degraded += 1

    # 🔥 FINAL SUMMARY
    if deltas:
        print("\n========== SUMMARY ==========")
        print("Avg Δ        :", round(float(np.mean(deltas)), 4))
        print("Improved     :", improved)
        print("Degraded     :", degraded)
        print("Total Images :", len(deltas))
  
    

    os.makedirs(
        "evaluation_results",
        exist_ok=True
    )

    df = pd.DataFrame(results)

    dark_df = df[df["category"] == "dark"]
    blur_df = df[df["category"] == "blur"]
    motion_df = df[df["category"] == "motion"]
    noise_df = df[df["category"] == "noise"]
    original_df = df[df["category"] == "original"]

    df.to_csv(
        "evaluation_results/eval_results.csv",
        index=False
    )
    dark_df.to_csv(
    "evaluation_results/dark_results.csv",
        index=False
    )

    blur_df.to_csv(
        "evaluation_results/blur_results.csv",
        index=False
    )

    motion_df.to_csv(
        "evaluation_results/motion_results.csv",
        index=False
    )

    noise_df.to_csv(
        "evaluation_results/noise_results.csv",
        index=False
    )

    original_df.to_csv(
    "evaluation_results/original_results.csv",
    index=False
)

    print(
        "\nSaved evaluation_results/eval_results.csv"
    )



def predict_confidence(image):

    _, confidence = predict(model, image)

    return float(confidence)