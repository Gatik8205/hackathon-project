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
- Caller claims to be CBI, ED, Customs, Narcotics, Police, RBI, Cyber Crime Cell, or TRAI official
- Claims about a parcel/package containing illegal items (drugs, fake passports) linked to the victim
- Claims of a criminal complaint, FIR, or financial fraud case filed against the victim
- Demands the victim stay on the call/video call continuously ("do not disconnect", "stay on the line")
- Isolates victim from family/friends, threatens arrest, tells them to keep the matter secret
- Demands money transfer to a "verification account" or for "clearing name"
- Uses fear, urgency, and authority-impersonation together
- Spoofed or suspicious caller ID patterns mentioned by the citizen

IMPORTANT — detect EARLY-STAGE scam calls, not just fully-escalated ones:
Real digital arrest scams often open with ONLY an authority claim plus a case/complaint claim plus a
mild "stay on the line" instruction — the explicit money demand or video-call isolation usually comes
a few minutes LATER in the call, after the victim is already hooked. Do not require the full pattern
(authority + isolation + money demand) before flagging a session. If a caller impersonates a law
enforcement or regulatory authority AND references a case, complaint, or investigation against the
victim by name/ID, classify this as is_scam_session: true even if no money has been demanded yet —
just use a lower alert_priority ("medium") to reflect that the session hasn't escalated to the
highest-risk stage.

A request for a VIDEO CALL alone, or general politeness/calm tone alone, is NEVER sufficient grounds
to flag a session. The deciding factor is always impersonation of an authority (law enforcement,
government, regulatory body) COMBINED with a claim of a case, complaint, fine, or investigation
against the specific victim. A doctor, delivery agent, or customer support rep asking for a video
call to do their normal job is not a scam signal by itself, no matter how it's phrased.

WHAT IS NOT A SCAM SESSION (classify as false — routine, legitimate calls):
- A bank, hospital, ISP, employer, or business following up on a service the citizen actually uses
  or requested (appointment reminders, complaint follow-ups, interview scheduling, billing updates,
  medical follow-ups, video consultations).
- No impersonation of law enforcement, regulatory, or investigative authority.
- No claim of a case, complaint, FIR, or investigation against the citizen.
- No demand for money transfer, OTP, PIN, or credentials.
Being an unsolicited or unfamiliar call, or asking to schedule a video call for a legitimate service
(e.g. telemedicine, customer support), is NOT by itself enough to classify as a scam session.

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
- "high": strong pattern match (authority claim + case/complaint claim + stay-on-line pressure) but
  no money movement confirmed yet — this covers early-stage digital arrest calls
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
        print(f"DEBUG - raw model output: {raw_text}")  # TEMPORARY — remove after confirming
        data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"DEBUG - JSON parse failed: {e}")  # TEMPORARY
        data = {
            "is_scam_session": True,
            "confidence": 0.5,
            "scam_type": "other",
            "matched_patterns": ["Automated parsing failed — flagged for manual review"],
            "alert_priority": "medium",
        }
    except Exception as e:
        print(f"DEBUG - scam_service error: {type(e).__name__}: {e}")  # TEMPORARY
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