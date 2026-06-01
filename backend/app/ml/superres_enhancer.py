import cv2
import numpy as np

print("Loading super-resolution model...")

sr = cv2.dnn_superres.DnnSuperResImpl_create()

sr.readModel("weights/EDSR_x2.pb")

sr.setModel("edsr", 2)

print("Model loaded successfully!")


def enhance_superres(image):

    print("Running AI upsampling...")

    h, w = image.shape[:2]

    # resize before SR
    if w > 400:

        scale = 400 / w

        image = cv2.resize(
            image,
            (int(w * scale), int(h * scale))
        )

    # AI super resolution
    result = sr.upsample(image)

    # mild sharpening after SR
    kernel = np.array([
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0]
], dtype=np.float32)

    result = cv2.filter2D(
        result,
        -1,
        kernel
    )

    print("Upsampling complete!")

    return result