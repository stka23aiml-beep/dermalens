import cv2
import numpy as np


def fix_brightness_lab(img, gamma=0.85):

    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    l, a, b = cv2.split(lab)

    l_norm = l / 255.0

    l_gamma = np.power(l_norm, gamma)

    l_out = np.clip(
        l_gamma * 255,
        0,
        255
    ).astype(np.uint8)

    lab = cv2.merge((l_out, a, b))

    return cv2.cvtColor(
        lab,
        cv2.COLOR_LAB2BGR
    )


def detect_blur(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    return float(
        cv2.Laplacian(gray, cv2.CV_64F).var()
    )


def enhance_image(image_bytes):

    # decode image
    np_arr = np.frombuffer(
        image_bytes,
        np.uint8
    )

    img = cv2.imdecode(
        np_arr,
        cv2.IMREAD_COLOR
    )

    original = img.copy()

    # metrics
    sharpness = detect_blur(img)

    brightness = np.mean(
        cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    )

    print("DEBUG → brightness:", brightness)

    print("DEBUG → sharpness:", sharpness)

    # default
    enhanced = img.copy()

    mode = "No Enhancement"

    # VERY DARK IMAGE
    if brightness < 50:

        enhanced = fix_brightness_lab(
            img,
            gamma=0.9
        )

        mode = "Brightness Enhanced"

    # BLURRY IMAGE
    elif sharpness < 80:

        # STEP 1 — Moderate unsharp masking
        gaussian = cv2.GaussianBlur(
            img,
            (9, 9),
            10.0
        )

        sharpened = cv2.addWeighted(
            img,
            1.4,
            gaussian,
            -0.4,
            0
        )

        # STEP 2 — CLAHE local contrast enhancement
        lab = cv2.cvtColor(
            sharpened,
            cv2.COLOR_BGR2LAB
        )

        l, a, b = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=1.2,
            tileGridSize=(8, 8)
        )

        cl = clahe.apply(l)

        merged = cv2.merge((cl, a, b))

        enhanced = cv2.cvtColor(
            merged,
            cv2.COLOR_LAB2BGR
        )

        mode = "Restored"

    return original, enhanced, mode