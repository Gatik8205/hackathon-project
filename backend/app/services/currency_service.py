"""
Counterfeit Currency Identification service.
Place at: app/services/currency_service.py

Loads the trained MobileNetV2 classifier (currency_classifier_final.pt) and
runs real inference on uploaded note images. Trained with 5-fold cross-
validation on a balanced real/fake dataset (133 real, 132 fake — 19 real
photos + synthetic augmentation, 12 real fake photos + synthetic
degradation-based augmentation).

Reported cross-validation performance (see training notebook for full
methodology): 95.47% +/- 2.82% overall accuracy, 91.82% +/- 5.90% real-class
accuracy, 99.26% +/- 1.48% fake-class accuracy.

NOTE: the fake class includes synthetic degraded images (blur, color shift,
compression artifacts) since real counterfeit note photos are scarce. This
is disclosed for transparency — real-world performance on genuine
counterfeit notes has not been separately validated and may differ.
"""

import os
import io
import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
from app.models.schemas import CurrencyVerifyResponse

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "currency_classifier_final.pt")
IMG_SIZE = 224

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_transform = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# Labels match training: 0 = real, 1 = fake
CLASS_NAMES = ["real", "fake"]


def _build_model() -> nn.Module:
    model = models.mobilenet_v2(weights=None)  # weights loaded from our trained checkpoint, not ImageNet
    model.classifier[1] = nn.Linear(model.last_channel, 2)
    return model


def _load_model() -> nn.Module:
    model = _build_model()
    state_dict = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state_dict)
    model.to(device)
    model.eval()
    return model


# Load once at module import time — avoids reloading the model on every request
try:
    _model = _load_model()
    _model_load_error = None
except Exception as e:
    _model = None
    _model_load_error = str(e)


def verify_note(image_bytes: bytes) -> CurrencyVerifyResponse:
    if _model is None:
        return CurrencyVerifyResponse(
            denomination=None,
            is_likely_genuine=False,
            confidence=0.0,
            checks_performed=[],
            flagged_issues=[f"Model failed to load on server startup: {_model_load_error}"],
        )

    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return CurrencyVerifyResponse(
            denomination=None,
            is_likely_genuine=False,
            confidence=0.0,
            checks_performed=[],
            flagged_issues=["Could not read image — please upload a clear, well-lit photo."],
        )

    checks_performed = ["cnn_authenticity_classification"]

    input_tensor = _transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = _model(input_tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        pred_idx = int(torch.argmax(probs).item())
        confidence = float(probs[pred_idx].item())

    predicted_label = CLASS_NAMES[pred_idx]
    is_likely_genuine = predicted_label == "real"

    flagged_issues = []
    if not is_likely_genuine:
        flagged_issues.append(
            f"Model classified this note as likely fake (confidence {confidence:.0%}). "
            "This is a proof-of-concept classifier trained on a small dataset "
            "(133 real / 132 fake images, partly synthetic) — treat as indicative only "
            "and verify through official banking channels for anything conclusive."
        )
    else:
        flagged_issues.append(
            f"No issues flagged (confidence {confidence:.0%}). This is a proof-of-concept "
            "classifier — not a substitute for RBI-grade verification."
        )

    return CurrencyVerifyResponse(
        denomination=None,  # denomination classification not covered by this model
        is_likely_genuine=is_likely_genuine,
        confidence=confidence,
        checks_performed=checks_performed,
        flagged_issues=flagged_issues,
    )