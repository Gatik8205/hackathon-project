"""
Scam session detection service — Digital Arrest Scam Detection & Alerting.
Place at: app/services/scam_service.py

Classifies an active call/session transcript for scam patterns and
assigns an alert priority for downstream telecom/MHA-style alerting.
"""

import os
import json
from google import genai
from app.models.schemas import ScamSessionRequest, ScamSessionResponse
from app.services import graph_service

client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """You are a real-time scam session classifier for a law-enforcement-facing platform in India.
Given a transcript or description of an ongoing call/video-call session, determine if it matches
known "digital arrest" or related fraud session patterns.

Known patterns to detect:
- Caller claims to be CBI, ED, Customs, Narcotics, Police, RBI, or TRAI official
- Claims about a parcel/package containing illegal items (drugs, fake passports) linked to the victim
- Demands the victim stay on video call continuously ("do not disconnect")
- Isolates victim from family/friends, threatens arrest, tells them to keep the matter secret
- Demands money transfer to a "verification account" or for "clearing name"
- Uses fear, urgency, and authority-impersonation together
- Spoofed or suspicious caller ID patterns mentioned by the citizen

Respond with ONLY a JSON object, no preamble, no markdown fences:

{
  "is_scam_session": <true|false>,
  "confidence": <float 0-1>,
  "scam_type": "<digital_arrest | otp_fraud | investment_scam | courier_scam | other | null>",
  "matched_patterns": [<short strings naming which specific patterns were found>],
  "alert_priority": "low" | "medium" | "high" | "critical"
}

alert_priority guidance:
- "critical": active demand for money transfer + impersonation of law enforcement + isolation tactics
- "high": strong pattern match but no money movement confirmed yet
- "medium": some suspicious elements, ambiguous
- "low": minimal or no matching patterns
"""


def classify_session(request: ScamSessionRequest) -> ScamSessionResponse:
    context_lines = [f'Transcript/description:\n"""{request.transcript}"""']
    if request.claimed_identity:
        context_lines.append(f"Caller claimed identity: {request.claimed_identity}")
    if request.caller_number:
        context_lines.append(f"Caller number: {request.caller_number}")
    context_lines.append(f"Video call: {request.video_call}")

    user_prompt = "\n".join(context_lines) + "\n\nClassify this session and respond with the JSON object only."

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
            "is_scam_session": True,
            "confidence": 0.5,
            "scam_type": "other",
            "matched_patterns": ["Automated parsing failed — flagged for manual review"],
            "alert_priority": "medium",
        }
    except Exception as e:
        # Covers rate limits (429), quota exhaustion, network errors, etc.
        # Fail toward caution for a law-enforcement-facing detector.
        data = {
            "is_scam_session": True,
            "confidence": 0.3,
            "scam_type": "other",
            "matched_patterns": [f"Classification service temporarily unavailable ({type(e).__name__})"],
            "alert_priority": "medium",
        }

    result = ScamSessionResponse(**data)

    if result.is_scam_session and request.caller_number:
        try:
            graph_service.auto_ingest_from_detection(
                phone_number=request.caller_number,
                source="scam_session_detector",
                scam_type=result.scam_type,
                complaint_text=request.transcript,
            )
        except Exception:
            pass

    return result