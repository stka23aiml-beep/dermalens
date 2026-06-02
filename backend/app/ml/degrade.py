import cv2
import os
import numpy as np

input_folder = "data/clean"

output_folder = "data/degraded"

os.makedirs(output_folder, exist_ok=True)


def add_gaussian_blur(img):

    return cv2.GaussianBlur(
        img,
        (11, 11),
        5
    )


def add_motion_blur(img):

    kernel = np.zeros((15, 15))

    kernel[7, :] = np.ones(15)

    kernel = kernel / 15

    return cv2.filter2D(
        img,
        -1,
        kernel
    )


def add_low_light(img):

    dark = (img * 0.4).astype(np.uint8)

    return dark


def add_noise(img):

    noise = np.random.normal(
        0,
        20,
        img.shape
    )

    noisy = np.clip(
        img + noise,
        0,
        255
    ).astype(np.uint8)

    return noisy


def add_jpeg_compression(img):

    encode_param = [
        int(cv2.IMWRITE_JPEG_QUALITY),
        15
    ]

    _, encimg = cv2.imencode(
        ".jpg",
        img,
        encode_param
    )

    compressed = cv2.imdecode(
        encimg,
        1
    )

    return compressed


for file in os.listdir(input_folder):

    path = os.path.join(
        input_folder,
        file
    )

    img = cv2.imread(path)

    if img is None:
        continue

    # Apply degradations
    blurred = add_gaussian_blur(img)

    motion = add_motion_blur(img)

    dark = add_low_light(img)

    noisy = add_noise(img)

    compressed = add_jpeg_compression(img)

    # Save all outputs
    cv2.imwrite(
        os.path.join(
            output_folder,
            f"blur_{file}"
        ),
        blurred
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            f"motion_{file}"
        ),
        motion
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            f"dark_{file}"
        ),
        dark
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            f"noise_{file}"
        ),
        noisy
    )

    cv2.imwrite(
        os.path.join(
            output_folder,
            f"jpeg_{file}"
        ),
        compressed
    )

print("Dataset degradation complete!")