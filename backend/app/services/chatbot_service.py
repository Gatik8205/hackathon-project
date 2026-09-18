"""
Chatbot service — Citizen Fraud Shield.
Place at: app/services/chatbot_service.py

Uses Groq (Llama 3.3 70B) to assess whether a described call/message is a
scam, returns a structured verdict with red flags and advice.
"""

import os
import json
from groq import Groq
from app.models.schemas import ChatbotAssessRequest, ChatbotAssessResponse
from app.services import graph_service

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You are a fraud-detection assistant for Indian citizens, part of a public safety platform.
You assess descriptions of phone calls, video calls, or messages for signs of common Indian scam patterns.

SCAM PATTERNS TO DETECT (verdict should lean scam only if these specific elements are present):
- "Digital arrest" scams: caller impersonates CBI, ED, Customs, Police, RBI, or TRAI, claims the
  citizen is under investigation or has committed a crime, and combines this with at least one of:
  demanding continuous video call presence, demanding secrecy/isolation from family, or demanding
  money transfer to "verify innocence," pay a "fine," or avoid arrest.
- OTP / UPI fraud: caller or message asks the citizen to SHARE an OTP, PIN, CVV, or full card number,
  or asks them to install a remote-access app, under pretext of a refund/KYC/verification.
- Investment / task-based scams: promises of guaranteed high returns, asks for upfront payment to
  "unlock" earnings, or pressure to invest secretly and quickly.
- Fake courier/parcel scams: claims of illegal items in a parcel under the citizen's name, combined
  with a demand for payment or transfer to "clear" the matter.
- Lottery/prize scams: claims of winning money/prizes that require an upfront "processing fee."

WHAT IS NOT A SCAM (these are routine, legitimate interactions — verdict should be "likely_safe"):
- Businesses (banks, gyms, hospitals, ISPs, landlords, employers, colleges, delivery services)
  contacting the citizen about services the citizen actually uses or expects — appointment reminders,
  billing notifications, service updates, delivery confirmations, subscription renewals.
- Calls or messages that DO NOT ask for money transfer, OTP/PIN sharing, or claim law-enforcement
  investigation/arrest.
- Friends, family, or known contacts sharing everyday messages, photos, or plans with no financial ask.
- Recruiters, customer support, or companies following up on something the citizen initiated
  (a complaint, application, or order), with no payment or credential request.
- Marketing or promotional calls offering a product/plan upgrade, with no threat or urgency to send money.

DECISION RULE — apply this literally:
- Use "likely_scam" ONLY if the message contains BOTH (a) an authority/urgency/financial-loss claim
  AND (b) an explicit request for money transfer, OTP/PIN/card details, or remote access.
- Use "possibly_scam" if there are some suspicious elements (unusual urgency, unfamiliar caller,
  vague identity) but no explicit request for money/credentials yet.
- Use "likely_safe" if the message describes an ordinary service interaction with no financial ask,
  no impersonation of law enforcement, and no urgency/threat language — even if it involves an
  unsolicited call. Being unsolicited alone does NOT make something a scam.
- Do not default to a scam verdict out of general caution. A wrong "likely_safe" on a truly ambiguous
  case is acceptable; falsely alarming citizens on routine calls erodes trust in this tool and is
  also a failure mode to avoid.

Respond with ONLY a JSON object matching this exact schema, no preamble, no markdown fences:

{
  "verdict": "likely_scam" | "possibly_scam" | "likely_safe",
  "confidence": <float 0-1>,
  "red_flags": [<short strings describing specific red flags found, empty list if none>],
  "advice": "<2-3 sentence plain-language advice for the citizen>",
  "recommended_action": "<concrete next step, e.g. reporting instructions, or 'No action needed' if safe>"
}
"""


def assess_message(request: ChatbotAssessRequest) -> ChatbotAssessResponse:
    user_prompt = f"""Citizen's description (channel: {request.channel}, language: {request.language}):

\"\"\"{request.message}\"\"\"

Assess this for fraud risk and respond with the JSON object only."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        raw_text = response.choices[0].message.content.strip()
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
        # Covers rate limits (429), network errors, etc.
        # Never let the citizen-facing endpoint crash — fail safe with a cautious response,
        # and mark it distinctly so evaluation scripts can exclude these from real accuracy counts.
        data = {
            "verdict": "possibly_scam",
            "confidence": 0.3,
            "red_flags": [f"Assessment service temporarily unavailable ({type(e).__name__})"],
            "advice": "Our automated check is temporarily unavailable. As a general rule: never share "
                       "OTPs, PINs, or transfer money to anyone claiming to be from a government agency "
                       "over call or video call.",
            "recommended_action": "Try again shortly, or report directly at cybercrime.gov.in / call 1930.",
            "service_unavailable": True,
        }

    result = ChatbotAssessResponse(**{k: v for k, v in data.items() if k != "service_unavailable"})

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