"""
Runs the hard/ambiguous edge cases separately from the main eval_script.py
suite, so you can report "clean cases: 100%, hard cases: X%" rather than
one blended number. This distinction is more credible in a report/deck
than a single score.

Usage:
    1. Place this file and hard_eval_cases.py in the same folder as
       eval_script.py (your backend project root).
    2. Make sure your backend is running: uvicorn main:app --reload
    3. Run: python eval_hard_cases.py
"""

import time
import requests
from hard_eval_cases import HARD_CHATBOT_CASES, HARD_SCAM_SESSION_CASES

API_BASE = "http://127.0.0.1:8000"
DELAY_SECONDS = 1  # Groq's free tier is much more generous than Gemini's was


def evaluate_hard_chatbot():
    print("\n=== Evaluating HARD /chatbot/assess cases ===\n")
    tp = fp = tn = fn = 0
    errors = []

    for case in HARD_CHATBOT_CASES:
        time.sleep(DELAY_SECONDS)
        try:
            res = requests.post(
                f"{API_BASE}/chatbot/assess",
                json={"message": case["message"], "channel": "eval-hard"},
                timeout=30,
            )
            if res.status_code != 200:
                errors.append((case["message"][:60], f"{res.status_code}: {res.text[:300]}"))
                continue
            data = res.json()
        except Exception as e:
            errors.append((case["message"][:60], str(e)))
            continue

        predicted_scam = data["verdict"] in ("likely_scam", "possibly_scam")
        actual_scam = case["label"]

        tag = "CORRECT" if predicted_scam == actual_scam else "WRONG"
        print(f"  [{tag}] expected={'scam' if actual_scam else 'safe'} got={data['verdict']} conf={data['confidence']}")
        print(f"           {case['message'][:90]}...")

        if predicted_scam and actual_scam:
            tp += 1
        elif predicted_scam and not actual_scam:
            fp += 1
        elif not predicted_scam and actual_scam:
            fn += 1
        else:
            tn += 1

    print_metrics("HARD Chatbot cases", tp, fp, tn, fn, errors)


def evaluate_hard_scam_session():
    print("\n=== Evaluating HARD /scam/detect cases ===\n")
    tp = fp = tn = fn = 0
    errors = []

    for case in HARD_SCAM_SESSION_CASES:
        time.sleep(DELAY_SECONDS)
        try:
            res = requests.post(
                f"{API_BASE}/scam/detect",
                json={
                    "transcript": case["transcript"],
                    "claimed_identity": case.get("claimed_identity"),
                    "video_call": case.get("video_call", False),
                },
                timeout=30,
            )
            if res.status_code != 200:
                errors.append((case["transcript"][:60], f"{res.status_code}: {res.text[:300]}"))
                continue
            data = res.json()
        except Exception as e:
            errors.append((case["transcript"][:60], str(e)))
            continue

        predicted_scam = data["is_scam_session"]
        actual_scam = case["label"]

        tag = "CORRECT" if predicted_scam == actual_scam else "WRONG"
        print(f"  [{tag}] expected={'scam' if actual_scam else 'safe'} got={predicted_scam} conf={data['confidence']}")
        print(f"           {case['transcript'][:90]}...")

        if predicted_scam and actual_scam:
            tp += 1
        elif predicted_scam and not actual_scam:
            fp += 1
        elif not predicted_scam and actual_scam:
            fn += 1
        else:
            tn += 1

    print_metrics("HARD Scam Session cases", tp, fp, tn, fn, errors)


def print_metrics(name, tp, fp, tn, fn, errors):
    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    fpr = fp / (fp + tn) if (fp + tn) else 0
    accuracy = (tp + tn) / total if total else 0

    print(f"\n--- {name} results ---")
    print(f"Total: {total} (errors: {len(errors)})")
    print(f"Confusion matrix: TP={tp}  FP={fp}  TN={tn}  FN={fn}")
    print(f"Accuracy:  {accuracy:.1%}")
    print(f"Precision: {precision:.1%}")
    print(f"Recall:    {recall:.1%}")
    print(f"F1:        {f1:.1%}")
    print(f"FPR:       {fpr:.1%}")

    if errors:
        print("\nErrors:")
        for text, err in errors:
            print(f"  - {text}... -> {err}")


if __name__ == "__main__":
    print("RakshakAI — HARD Edge Case Evaluation")
    print("=" * 50)
    evaluate_hard_chatbot()
    evaluate_hard_scam_session()
    print("\n" + "=" * 50)
    print("Compare these numbers against your original 40-case run.")
    print("A drop here (vs. the clean 100%) is expected and healthy —")
    print("it shows where the model's decision rule needs sharpening.")
