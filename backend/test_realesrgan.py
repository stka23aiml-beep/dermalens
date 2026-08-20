import time
from pathlib import Path

import cv2
import torch

from realesrgan import RealESRGANer
from realesrgan.archs.srvgg_arch import SRVGGNetCompact


MODEL_PATH = Path(
    "app/ml/realesrgan_weights/realesr-general-x4v3.pth"
)

INPUT_PATH = Path(
    "test_images/WhatsApp Image 2026-08-17 at 10.17.27.jpeg"
)

OUTPUT_PATH = Path(
    "test_images/realesrgan_test.jpg"
)


def main():

    print(
        "DEVICE:",
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print("MODEL:", MODEL_PATH)
    print("INPUT:", INPUT_PATH)

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Input image not found: {INPUT_PATH}"
        )

    image = cv2.imread(
        str(INPUT_PATH),
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            "Could not read input image."
        )

    h, w = image.shape[:2]

    print(
        f"INPUT SIZE: {w}x{h}"
    )

    # --------------------------------------------------
    # REAL-ESRGAN GENERAL X4V3 ARCHITECTURE
    # --------------------------------------------------

    model = SRVGGNetCompact(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_conv=32,
        upscale=4,
        act_type="prelu"
    )

    # --------------------------------------------------
    # REAL-ESRGAN
    # --------------------------------------------------

    upsampler = RealESRGANer(
        scale=4,
        model_path=str(MODEL_PATH),
        model=model,
        tile=128,
        tile_pad=10,
        pre_pad=0,
        half=False,
        device=torch.device("cpu"),
    )

    print("START REAL-ESRGAN...")

    start = time.time()

    output, _ = upsampler.enhance(
        image,
        outscale=2
    )

    elapsed = time.time() - start

    output_h, output_w = output.shape[:2]

    print(
        f"OUTPUT SIZE: {output_w}x{output_h}"
    )

    print(
        f"PROCESSING TIME: {elapsed:.2f} seconds"
    )

    success = cv2.imwrite(
        str(OUTPUT_PATH),
        output
    )

    if not success:
        raise RuntimeError(
            "Failed to save output image."
        )

    print(
        "OUTPUT SAVED:",
        OUTPUT_PATH
    )


if __name__ == "__main__":
    main()