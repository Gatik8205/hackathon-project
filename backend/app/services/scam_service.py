"""
Scam session detection service — Digital Arrest Scam Detection & Alerting.
Place at: app/services/scam_service.py

Classifies an active call/session transcript for scam patterns and
assigns an alert priority for downstream telecom/MHA-style alerting.
"""

import os
import json
from groq import Groq
from app.models.schemas import ScamSessionRequest, ScamSessionResponse
from app.services import graph_service

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-20b"

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

WHAT IS NOT A SCAM SESSION (classify as false — routine, legitimate calls):
- A bank, hospital, ISP, employer, or business following up on a service the citizen actually uses
  or requested (appointment reminders, complaint follow-ups, interview scheduling, billing updates).
- No impersonation of law enforcement or government authority.
- No demand for money transfer, OTP, PIN, or credentials.
- No urgency, threat, or isolation language.
Being an unsolicited or unfamiliar call is NOT by itself enough to classify as a scam session.

Respond with ONLY a JSON object, no preamble, no markdown fences:

{
  "is_scam_session": <true|false>,
  "confidence": <float 0-1>,
  "scam_type": "<digital_arrest | otp_fraud | investment_scam | courier_scam | other | null>",
  "matched_patterns": [<short strings naming which specific patterns were found, empty list if none>],
  "alert_priority": "low" | "medium" | "high" | "critical"
}

alert_priority guidance:
- "critical": active demand for money transfer + impersonation of law enforcement + isolation tactics
- "high": strong pattern match but no money movement confirmed yet
- "medium": some suspicious elements, ambiguous
- "low": minimal or no matching patterns (use this for legitimate calls, with is_scam_session: false)
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
            "is_scam_session": True,
            "confidence": 0.5,
            "scam_type": "other",
            "matched_patterns": ["Automated parsing failed — flagged for manual review"],
            "alert_priority": "medium",
        }
    except Exception as e:
        # Covers rate limits (429), network errors, etc.
        # Fail toward caution for a law-enforcement-facing detector.
        data = {
            "is_scam_session": True,
            "confidence": 0.3,
            "scam_type": "other",
            "matched_patterns": [f"Classification service temporarily unavailable ({type(e).__name__})"],
            "alert_priority": "medium",
            "service_unavailable": True,
        }

    result = ScamSessionResponse(**{k: v for k, v in data.items() if k != "service_unavailable"})

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