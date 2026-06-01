# backend/app/ml/evaluate_derm.py

import os
import cv2
import numpy as np

from app.ml.enhancement import enhance_image, detect_blur
from app.ml.derm_model import load_model, predict

# path to weights
WEIGHTS_PATH = "app/ml/models/isic_resnet18.pth"

# load model once
model = load_model(WEIGHTS_PATH)


def evaluate(image_path):
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    full_path = os.path.join(base_dir, image_path)

    img = cv2.imread(full_path)
    if img is None:
        print(f"Skipping {image_path} (not found)")
        return None

    # blur check
    sharpness = detect_blur(img)

    # ORIGINAL
    cls_o, conf_o = predict(model, img)

    # ENHANCED
    with open(full_path, "rb") as f:
        image_bytes = f.read()

    _, enhanced, _ = enhance_image(image_bytes)
    cls_e, conf_e = predict(model, enhanced)

    # delta
    delta = conf_e - conf_o

    # PRINT
    print("\n---", image_path, "---")
    print(f"Sharpness  → {round(sharpness, 2)}")
    print(f"Original   → {cls_o} ({round(conf_o, 4)})")
    print(f"Enhanced   → {cls_e} ({round(conf_e, 4)})")
    print(f"Delta      → {round(delta, 4)}")

    if delta > 0.02:
        print("✔ Improvement")
    elif delta < -0.02:
        print("⚠ Degradation")
    else:
        print("~ No significant change")

    return delta


if __name__ == "__main__":

    images = [
        "sample.jpg",
        "data/bad_blur.jpg",
        "data/bad_dark.jpg",
        "data/bad_noise.jpg",
        "data/test/badd.jpeg",
        "data/test/image.jpg"
        
        
    ]

    deltas = []
    improved = 0
    degraded = 0

    for img_path in images:
        delta = evaluate(img_path)

        if delta is None:
            continue

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

def predict_confidence(image):

    _, confidence = predict(model, image)

    return float(confidence)