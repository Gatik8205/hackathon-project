"""
Hard edge cases for stress-testing chatbot_service and scam_service.
These are deliberately ambiguous or tricky — designed to probe failure
modes rather than confirm easy wins. Append to eval_test_cases.py's
existing lists, or import and extend from there.

Design notes on what makes each one hard:
- Partial scam signals (authority claim WITHOUT money ask, or money ask
  WITHOUT authority claim) — tests the "BOTH conditions" decision rule
- Legitimate urgency (real fraud alerts, genuine deadlines) that could
  be mistaken for scam pressure tactics
  - Real scams using softer, low-pressure language instead of obvious threats
- Mixed signals within a single message
"""

HARD_CHATBOT_CASES = [
    # --- Partial signals: authority claim but NO money/credential ask (should be likely_safe or possibly_scam, NOT likely_scam) ---
    {"label": False, "message": "Someone called saying they were from the local police station doing a routine survey about neighborhood safety, asked if we'd noticed any suspicious activity recently. No personal or financial info requested."},
    {"label": False, "message": "I got a message saying 'This is a reminder from RBI's financial literacy program about an upcoming free webinar on fraud awareness.' No links, no requests for details."},

    # --- Partial signals: money/urgency ask but NO authority impersonation (ambiguous — could go either way, testing possibly_scam) ---
    {"label": True, "message": "A message says 'Congratulations! You've been selected for a cashback reward of Rs 5000. Click here and enter your card details to claim it within 24 hours or it expires.'"},
    {"label": True, "message": "Got a call from someone claiming to be my electricity provider saying my bill payment failed and my connection will be cut in 2 hours unless I pay immediately through a link they text me."},

    # --- Real scams using SOFT, low-pressure language (no obvious threats) ---
    {"label": True, "message": "Someone messaged saying they're from my bank's 'customer care team' and my account needs a 'quick KYC re-verification' — asked me to share the OTP that would arrive shortly to 'confirm my identity', very polite and patient about it."},
    {"label": True, "message": "A caller calmly explained he was from Income Tax department doing a 'routine account cross-check' and asked me to verify my PAN and a one-time code sent to my phone, no threats, just said it was 'standard procedure'."},

    # --- Legitimate messages with urgency (could be mistaken for scam pressure) ---
    {"label": False, "message": "My actual bank sent an SMS: 'Your card will be blocked in 48 hours due to pending mandatory KYC update. Please visit your nearest branch with ID proof to complete it.' No link, no OTP request, directs to physical branch."},
    {"label": False, "message": "Got a call from my landlord saying rent is due tomorrow and if it's not paid by end of day there will be a late fee, as per our lease agreement."},
    {"label": False, "message": "My college registrar called urgently saying I need to submit a missing document by 5pm today or my exam form won't be processed this semester."},

    # --- Mixed signals: legitimate-sounding company name but suspicious ask ---
    {"label": True, "message": "Received a call from someone saying they're from 'Amazon Prime Fraud Protection Team', said unauthorized charges were found on my account, and asked me to install AnyDesk so they could 'secure' it remotely."},
    {"label": True, "message": "A message claiming to be from my mobile carrier says my number will be disconnected due to 'document mismatch' and asks me to click a link and complete a video KYC where I show my Aadhaar and bank passbook on camera."},

    # --- Genuinely ambiguous: could reasonably be either (testing possibly_scam usage) ---
    {"label": True, "message": "Got a LinkedIn message from a 'recruiter' offering a data-entry job paying well above market rate, asked me to pay a small refundable 'training kit deposit' before onboarding starts."},
    {"label": False, "message": "A gym membership sales rep called offering a heavily discounted annual plan if I sign up and pay today, mentioned the offer expires tonight — pushy sales tactic but a real gym I've visited before."},
]

HARD_SCAM_SESSION_CASES = [
    # --- Authority claim WITHOUT explicit money demand yet (early-stage scam call, ambiguous) ---
    {"label": True, "transcript": "Caller: Good evening, I am calling from the Cyber Crime Cell regarding a complaint filed against your Aadhaar number in a financial fraud case in Mumbai. I need to verify a few details with you before this escalates further. Please stay on the line.", "claimed_identity": "Cyber Crime Cell", "video_call": False},

    # --- Legitimate but urgent/formal-sounding call (should NOT be flagged) ---
    {"label": False, "transcript": "Caller: This is Rakesh from your housing society's maintenance office. We need to schedule an urgent water tank inspection tomorrow morning due to a contamination report from the municipal corporation. Please confirm if 9 AM works.", "claimed_identity": None, "video_call": False},

    # --- Soft-spoken scam without threats, using politeness as a disarming tactic ---
    {"label": True, "transcript": "Caller: Hello ma'am, this is just a courtesy call from the bank's KYC compliance desk. There's no urgency at all, but whenever convenient, could you confirm the OTP you'll receive shortly so we can update your records? Take your time.", "claimed_identity": "Bank KYC desk", "video_call": False},

    # --- Legitimate call with video request (video alone shouldn't trigger it) ---
    {"label": False, "transcript": "Caller: Hi, this is from the telemedicine clinic, your doctor would like to do a quick video consultation to check on your recovery since your last visit. No payment needed, this is part of your follow-up care.", "claimed_identity": None, "video_call": True},
]
