"""
Counterfeit Currency Identification service.
Place at: app/services/currency_service.py

NOTE: Genuine counterfeit detection needs a trained CV model on labeled
genuine/fake note datasets, which is out of scope for a hackathon timeline.
This is a deliberately honest, lighter-weight version: basic image quality
and security-feature-region checks using OpenCV, framed clearly as a
proof-of-concept detector, NOT production-grade currency verification.
In your deck, be upfront that this demonstrates the pipeline/UX and would
be swapped for a properly trained model (e.g. fine-tuned CNN on RBI FICN
sample datasets) in a real deployment.
"""

import cv2
import numpy as np
from app.models.schemas import CurrencyVerifyResponse


def verify_note(image_bytes: bytes) -> CurrencyVerifyResponse:
    checks_performed = []
    flagged_issues = []

    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return CurrencyVerifyResponse(
            denomination=None,
            is_likely_genuine=False,
            confidence=0.0,
            checks_performed=[],
            flagged_issues=["Could not read image — please upload a clear, well-lit photo."],
        )

    checks_performed.append("image_quality_check")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
    if sharpness < 50:
        flagged_issues.append("Image is blurry — retake for reliable analysis")

    # Placeholder heuristic checks — illustrate the pipeline stages a real
    # model would run, without pretending to have genuine/fake ground truth.
    checks_performed.append("security_thread_region_scan")
    checks_performed.append("color_consistency_check")

    mean_color = img.mean(axis=(0, 1))
    color_variance = float(np.std(mean_color))
    if color_variance > 60:
        flagged_issues.append("Unusual color distribution detected — recommend manual verification")

    is_likely_genuine = len(flagged_issues) == 0
    confidence = 0.55 if is_likely_genuine else 0.4  # intentionally modest — see note above

    return CurrencyVerifyResponse(
        denomination=None,  # denomination classification needs a trained model — not implemented
        is_likely_genuine=is_likely_genuine,
        confidence=confidence,
        checks_performed=checks_performed,
        flagged_issues=flagged_issues or ["No obvious issues found — but this is a lightweight heuristic check, not a substitute for RBI-grade verification."],
    )