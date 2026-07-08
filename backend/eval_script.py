"""
Evaluation script for RakshakAI chatbot and scam detection endpoints.

Usage:
    1. Make sure your backend is running: uvicorn main:app --reload
    2. Place this file + eval_test_cases.py anywhere (e.g. project root)
    3. Run: python eval_script.py

Outputs precision, recall, F1, false positive rate, and a confusion matrix
for both /chatbot/assess and /scam/detect endpoints, plus a markdown table
you can paste directly into your deck.
"""

import time
import requests
from eval_test_cases import CHATBOT_TEST_CASES, SCAM_SESSION_TEST_CASES

API_BASE = "http://127.0.0.1:8000"
DELAY_SECONDS = 6.5  # ~9 requests/min, safely under most Gemini free-tier limits (10-15/min)


def evaluate_chatbot():
    print("\n=== Evaluating /chatbot/assess ===\n")
    tp = fp = tn = fn = 0
    errors = []

    for case in CHATBOT_TEST_CASES:
        time.sleep(DELAY_SECONDS)
        try:
            res = requests.post(
                f"{API_BASE}/chatbot/assess",
                json={"message": case["message"], "channel": "eval"},
                timeout=30,
            )
            if res.status_code != 200:
                errors.append((case["message"][:60], f"{res.status_code}: {res.text[:300]}"))
                continue
            data = res.json()
        except Exception as e:
            errors.append((case["message"][:60], str(e)))
            continue

        # Treat "likely_scam" and "possibly_scam" as a positive (scam) prediction.
        # Only "likely_safe" counts as a negative prediction.
        predicted_scam = data["verdict"] in ("likely_scam", "possibly_scam")
        actual_scam = case["label"]

        if predicted_scam and actual_scam:
            tp += 1
        elif predicted_scam and not actual_scam:
            fp += 1
            print(f"  [FALSE POSITIVE] {case['message'][:70]}...")
            print(f"      -> verdict={data['verdict']} confidence={data['confidence']} red_flags={data['red_flags']}")
        elif not predicted_scam and actual_scam:
            fn += 1
            print(f"  [FALSE NEGATIVE] {case['message'][:70]}...")
        else:
            tn += 1

    print_metrics("Chatbot (Citizen Fraud Shield)", tp, fp, tn, fn, errors)


def evaluate_scam_detector():
    print("\n=== Evaluating /scam/detect ===\n")
    tp = fp = tn = fn = 0
    errors = []

    for case in SCAM_SESSION_TEST_CASES:
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

        if predicted_scam and actual_scam:
            tp += 1
        elif predicted_scam and not actual_scam:
            fp += 1
            print(f"  [FALSE POSITIVE] {case['transcript'][:70]}...")
            print(f"      -> is_scam={data['is_scam_session']} confidence={data['confidence']} patterns={data['matched_patterns']}")
        elif not predicted_scam and actual_scam:
            fn += 1
            print(f"  [FALSE NEGATIVE] {case['transcript'][:70]}...")
        else:
            tn += 1

    print_metrics("Scam Session Detector", tp, fp, tn, fn, errors)


def print_metrics(name, tp, fp, tn, fn, errors):
    total = tp + fp + tn + fn
    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    fpr = fp / (fp + tn) if (fp + tn) else 0
    accuracy = (tp + tn) / total if total else 0

    print(f"\n--- {name} results ---")
    print(f"Total test cases evaluated: {total} (errors: {len(errors)})")
    print(f"Confusion matrix: TP={tp}  FP={fp}  TN={tn}  FN={fn}")
    print(f"Accuracy:             {accuracy:.1%}")
    print(f"Precision:            {precision:.1%}")
    print(f"Recall (sensitivity): {recall:.1%}")
    print(f"F1 score:             {f1:.1%}")
    print(f"False positive rate:  {fpr:.1%}")

    if errors:
        print("\nRequests that errored out (not counted in metrics):")
        for text, err in errors:
            print(f"  - {text}... -> {err}")

    print(f"\nMarkdown table row for deck:")
    print(f"| {name} | {total} | {accuracy:.1%} | {precision:.1%} | {recall:.1%} | {f1:.1%} | {fpr:.1%} |")


if __name__ == "__main__":
    print("RakshakAI — Evaluation Report")
    print("=" * 50)
    print(f"Target API: {API_BASE}")
    print(f"Chatbot test cases: {len(CHATBOT_TEST_CASES)}")
    print(f"Scam session test cases: {len(SCAM_SESSION_TEST_CASES)}")

    evaluate_chatbot()
    evaluate_scam_detector()

    print("\n" + "=" * 50)
    print("Done. Copy the markdown rows above into your deck's evaluation slide.")
    print("Suggested table header:")
    print("| Component | Test cases | Accuracy | Precision | Recall | F1 | False Positive Rate |")