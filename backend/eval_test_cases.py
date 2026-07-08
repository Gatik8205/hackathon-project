"""
Labeled test cases for evaluating chatbot_service and scam_service.
label: true = is a scam, false = is not a scam
"""

CHATBOT_TEST_CASES = [
    # --- SCAMS (label = True) ---
    {"label": True, "message": "Someone called claiming to be from CBI, said there's a case against me involving money laundering, and told me to stay on video call while they 'verify' my bank details before I get arrested."},
    {"label": True, "message": "A man on video call said he was a Customs officer and that a parcel with my name had illegal drugs in it. He told me not to disconnect and to transfer money to a 'verification account' to clear my name."},
    {"label": True, "message": "I got a call saying my Aadhaar card is linked to a crime and I need to pay a fine immediately via UPI or police will come to arrest me."},
    {"label": True, "message": "Someone from 'TRAI' called saying my SIM will be blocked in 2 hours due to illegal activity, and forwarded me to a fake 'cyber cell officer' on video call demanding I don't tell my family."},
    {"label": True, "message": "Got a WhatsApp message saying I won a lottery from KBC, need to pay processing fee of Rs 25000 to claim Rs 25 lakh prize."},
    {"label": True, "message": "A caller pretending to be from my bank asked for the OTP I just received to 'verify a suspicious transaction' on my account."},
    {"label": True, "message": "Someone offered me a work-from-home job where I just like YouTube videos and get paid, but first I need to pay a 500 rupee registration fee and then keep investing more to unlock withdrawals."},
    {"label": True, "message": "Man claiming to be ED officer said my bank account is under investigation for money laundering and I must transfer all funds to a 'safe government account' for 24 hours."},
    {"label": True, "message": "I received a call saying I need to update my KYC immediately or my account will be frozen, they asked me to share my debit card PIN and OTP over the phone."},
    {"label": True, "message": "Caller said he's from courier company and a package with fake passports was intercepted with my address on it, connected me to 'police' on video call who demanded money to close the case quietly."},
    {"label": True, "message": "Someone messaged saying they're a stockbroker with insider tips, promised guaranteed 300% returns if I invest through their app immediately, told me to keep it secret from family."},
    {"label": True, "message": "Person on call claimed to be from Income Tax department, said I owe back taxes and will be arrested tomorrow unless I pay right now through a link they sent."},
    {"label": True, "message": "Video call from someone in police uniform saying my son was in an accident and they need money transferred immediately for hospital bail, told me not to call anyone else to verify."},
    {"label": True, "message": "Got a call from 'RBI officer' saying my bank account is being used for fraud and I must move my money to a new 'secure' account they provide within an hour."},
    {"label": True, "message": "Someone pretending to be a relative in distress on WhatsApp video (blurry) asked me to urgently transfer money because they lost their wallet abroad."},

    # --- NOT SCAMS (label = False) ---
    {"label": False, "message": "My bank sent an SMS saying my monthly statement is ready, I can view it by logging into their official app."},
    {"label": False, "message": "I got a call from my gym reminding me my membership is expiring next week."},
    {"label": False, "message": "My electricity provider sent an email about a scheduled maintenance outage in my area next Tuesday."},
    {"label": False, "message": "A delivery person called to confirm my address before delivering a package I actually ordered from Amazon."},
    {"label": False, "message": "My friend called to ask if I want to grab coffee this weekend."},
    {"label": False, "message": "I received a notification from my bank's official app that my salary was credited today."},
    {"label": False, "message": "A telemarketer called offering me a new mobile data plan from my existing telecom provider."},
    {"label": False, "message": "My doctor's clinic called to remind me about my appointment tomorrow morning."},
    {"label": False, "message": "I got an email newsletter from a company I subscribed to about their new product launch."},
    {"label": False, "message": "My landlord called to discuss the rent renewal for next year."},
    {"label": False, "message": "Customer support from my internet provider called back regarding a complaint I raised yesterday about slow speeds."},
    {"label": False, "message": "My college sent an email with the exam schedule for next semester."},
    {"label": False, "message": "A recruiter reached out on LinkedIn about a genuine job opening at a company I recognize, no payment requested."},
    {"label": False, "message": "My credit card company called to ask if I wanted to upgrade to a premium card, no personal details requested over call."},
    {"label": False, "message": "I received a WhatsApp message from my sister sharing family photos from a recent trip."},
]

SCAM_SESSION_TEST_CASES = [
    # --- SCAM SESSIONS (label = True) ---
    {"label": True, "transcript": "Caller: I am Inspector Sharma from CBI. You are under investigation for money laundering. Stay on this video call, do not disconnect, or you will be arrested within the hour. Transfer 5 lakh rupees to this account to prove your innocence.", "claimed_identity": "CBI officer", "video_call": True},
    {"label": True, "transcript": "This is Customs department. A parcel addressed to you contains banned substances. We are connecting you to law enforcement now. Do not hang up or tell anyone, this is a confidential investigation. You must pay a clearance fee immediately.", "claimed_identity": "Customs officer", "video_call": True},
    {"label": True, "transcript": "Sir this is your bank's fraud prevention team, we detected suspicious activity, please share the OTP sent to your phone right now so we can block the transaction.", "claimed_identity": "Bank fraud team", "video_call": False},
    {"label": True, "transcript": "I am calling from the Enforcement Directorate. Your account has been flagged in a money laundering case linked to a terror funding network. Move all your savings to this secure government holding account within 30 minutes or face arrest.", "claimed_identity": "ED officer", "video_call": True},
    {"label": True, "transcript": "Hello this is TRAI, your number will be disconnected in 2 hours due to illegal SIM activity. I am transferring your call to cyber crime cell. Please stay on video and do not tell your family about this investigation.", "claimed_identity": "TRAI / Cyber cell", "video_call": True},

    # --- NOT SCAM SESSIONS (label = False) ---
    {"label": False, "transcript": "Hi, this is Priya from XYZ Bank customer service, calling to follow up on the complaint you raised last week about your debit card. Has the issue been resolved?", "claimed_identity": "Bank customer service", "video_call": False},
    {"label": False, "transcript": "Good afternoon, this is a reminder call from City Hospital about your appointment scheduled for tomorrow at 10 AM with Dr. Mehta.", "claimed_identity": None, "video_call": False},
    {"label": False, "transcript": "Hello, I'm calling from your internet service provider regarding the router replacement you requested. When would be a good time for our technician to visit?", "claimed_identity": None, "video_call": False},
    {"label": False, "transcript": "Hi this is HR from the company you applied to, we'd like to schedule your interview for next Monday at 3 PM. No payment or fees involved.", "claimed_identity": "HR recruiter", "video_call": False},
    {"label": False, "transcript": "This is your electricity board calling to inform you about the new online bill payment portal launch. No action needed from your side right now.", "claimed_identity": None, "video_call": False},
]
