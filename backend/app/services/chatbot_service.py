"""
Chatbot service — Citizen Fraud Shield.
Place at: app/services/chatbot_service.py

Uses Gemini (google-genai) to assess whether a described call/message is a
scam, returns a structured verdict with red flags and advice.
"""

import os
import json
from google import genai
from app.models.schemas import ChatbotAssessRequest, ChatbotAssessResponse
from app.services import graph_service

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """You are a fraud-detection assistant for Indian citizens, part of a public safety platform.
You assess descriptions of phone calls, video calls, or messages for signs of common Indian scam patterns.

SCAM PATTERNS TO DETECT:
- "Digital arrest" scams: callers impersonating CBI, ED, Customs, Police, TRAI, or RBI, claiming the
  citizen is under investigation, demanding they stay on video call, isolating them from family,
  and demanding money transfer to "verify" innocence or avoid arrest.
- OTP / UPI fraud: requests for OTP, PIN, CVV, or remote screen access under pretext of a refund,
  KYC update, or account verification.
- Investment / task-based scams: promises of high/guaranteed returns for small "tasks", crypto, or
  stock tips, especially with secrecy or urgency.
- Fake courier/parcel scams: claims of illegal items found in a parcel under the citizen's name,
  demanding payment to "clear" it.
- Lottery/prize scams: claims of winning money that require an upfront "processing fee."
- Fake relative/emergency scams: urgent requests for money from someone claiming to be a relative
  in distress, especially over poor-quality video/audio.

WHAT IS **NOT** A SCAM (respond likely_safe for these, do not hedge):
- Routine business calls/messages: appointment reminders, delivery confirmations, bill notifications,
  service renewal reminders, newsletters — where NO money, OTP, PIN, or urgent action is demanded.
- Genuine customer service follow-ups on a complaint or request the citizen actually made.
- Job/recruitment outreach with NO upfront payment requested.
- Messages from known contacts (family, friends) sharing ordinary content (photos, plans) with no
  money request or urgency.
- Marketing/telemarketing offers for real products/services with no impersonation of authority and
  no request for sensitive credentials.
The presence of a phone call or message alone is NOT suspicious. Most calls are legitimate.
Only flag a red flag if it is a SPECIFIC pattern from the list above — not merely "this was unsolicited"
or "I cannot fully verify this."

Respond with ONLY a JSON object matching this exact schema, no preamble, no markdown fences:

{
  "verdict": "likely_scam" | "possibly_scam" | "likely_safe",
  "confidence": <float 0-1>,
  "red_flags": [<short strings describing specific red flags found, empty list if none>],
  "advice": "<2-3 sentence plain-language advice for the citizen>",
  "recommended_action": "<concrete next step, e.g. reporting instructions, or 'No action needed' if safe>"
}

VERDICT GUIDANCE:
- "likely_scam": Clear match to one or more scam patterns above (e.g. impersonating authority +
  urgency + money/credential request).
- "possibly_scam": Some concerning elements present but ambiguous or incomplete information — NOT
  simply "any call could theoretically be a scam."
- "likely_safe": No specific scam pattern present. Use this confidently for routine, ordinary
  interactions. Do not default to "possibly_scam" just to be cautious when there is no actual
  red flag from the list above.
- recommended_action should mention reporting to cybercrime.gov.in or the 1930 helpline only when
  the verdict is likely_scam or possibly_scam.
"""


def assess_message(request: ChatbotAssessRequest) -> ChatbotAssessResponse:
    user_prompt = f"""Citizen's description (channel: {request.channel}, language: {request.language}):

\"\"\"{request.message}\"\"\"

Assess this for fraud risk and respond with the JSON object only."""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "response_mime_type": "application/json",
            },
        )
        raw_text = response.text.strip()
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        data = {
            "verdict": "possibly_scam",
            "confidence": 0.5,
            "red_flags": ["Unable to fully parse assessment — manual review recommended"],
            "advice": "We couldn't complete a full automated assessment. Please do not share OTPs, "
                       "PINs, or transfer money, and verify independently by calling the organization "
                       "back on their official number.",
            "recommended_action": "Report the incident at cybercrime.gov.in or call 1930 if money was lost.",
        }
    except Exception as e:
        # Covers rate limits (429), quota exhaustion, network errors, etc.
        # Never let the citizen-facing endpoint crash — fail safe with a cautious response.
        print(f"DEBUG - chatbot_service error: {type(e).__name__}: {e}")
        data = {
            "verdict": "possibly_scam",
            "confidence": 0.3,
            "red_flags": [f"Assessment service temporarily unavailable ({type(e).__name__})"],
            "advice": "Our automated check is temporarily unavailable. As a general rule: never share "
                       "OTPs, PINs, or transfer money to anyone claiming to be from a government agency "
                       "over call or video call.",
            "recommended_action": "Try again shortly, or report directly at cybercrime.gov.in / call 1930.",
        }

    result = ChatbotAssessResponse(**data)

    # Wire this detection into the fraud network graph if it's flagged as a
    # scam and we have a phone number to link it on. Never let this block
    # or fail the citizen-facing response.
    if result.verdict in ("likely_scam", "possibly_scam") and request.phone_number:
        try:
            graph_service.auto_ingest_from_detection(
                phone_number=request.phone_number,
                source="citizen_fraud_shield",
                complaint_text=request.message,
            )
        except Exception:
            pass  # graph ingestion is best-effort, should never break the main response

    return result