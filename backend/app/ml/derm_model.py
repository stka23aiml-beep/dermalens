import time

import torch
from torchvision import models, transforms
from PIL import Image
import cv2


# --------------------------------------------------
# MODEL CONFIG
# --------------------------------------------------

NUM_CLASSES = 7


# --------------------------------------------------
# IMAGE TRANSFORM
# --------------------------------------------------

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])


# --------------------------------------------------
# MODEL LOADING
# --------------------------------------------------

def load_model(weights_path):
    print(f"MODEL → loading weights from: {weights_path}")

    model = models.resnet18(weights=None)

    # Must match the 7-class ISIC checkpoint.
    model.fc = torch.nn.Linear(
        model.fc.in_features,
        NUM_CLASSES
    )

    state = torch.load(
        weights_path,
        map_location="cpu"
    )

    model.load_state_dict(state)

    model.eval()

    print("MODEL → loaded successfully")

    return model


# --------------------------------------------------
# PREDICTION
# --------------------------------------------------

def predict(model, image_np):

    start_time = time.perf_counter()

    print(
        f"PREDICT → received image: "
        f"shape={image_np.shape}, "
        f"dtype={image_np.dtype}"
    )

    # OpenCV BGR → RGB → PIL
    image = Image.fromarray(
        cv2.cvtColor(
            image_np,
            cv2.COLOR_BGR2RGB
        )
    )

    print("PREDICT → image converted to PIL")

    # Resize + normalize
    tensor = transform(image).unsqueeze(0)

    print(
        f"PREDICT → tensor ready: "
        f"shape={tuple(tensor.shape)}"
    )

    # CPU inference
    with torch.no_grad():
        output = model(tensor)

    print(
        f"PREDICT → model inference completed "
        f"in {time.perf_counter() - start_time:.2f}s"
    )

    probs = torch.nn.functional.softmax(
        output[0],
        dim=0
    )

    confidence = torch.max(probs).item()
    predicted_class = torch.argmax(probs).item()

    print(
        f"PREDICT → class={predicted_class}, "
        f"confidence={confidence:.6f}"
    )

    return predicted_class, confidence