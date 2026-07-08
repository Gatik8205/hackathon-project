# RakshakAI — Frontend

Next.js (App Router) frontend for the RakshakAI Digital Public Safety Intelligence platform, built for ET AI Hackathon 2026.

## Setup

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000. Make sure the FastAPI backend is running at the URL set in `.env.local` (defaults to `http://127.0.0.1:8000`).

## Pages

- `/` — Overview / feature navigation
- `/chat` — Citizen Fraud Shield (chatbot-style scam assessment)
- `/scam-check` — Scam Session Detector (for law enforcement / telecom)
- `/currency-check` — Currency Verification (image upload)
- `/fraud-network` — Fraud Network Intelligence (D3 force-directed graph)

## Before demoing the fraud network page

The graph starts empty. Ingest the sample fraud reports first:

```bash
curl -X POST http://127.0.0.1:8000/graph/ingest \
  -H "Content-Type: application/json" \
  -d @../ai-public-safety-project/app/data/sample_fraud_reports.json
```

(Adjust the path to wherever `sample_fraud_reports.json` lives in the backend repo.)

## Structure

```
app/                  Next.js App Router pages
components/            Shared UI (Sidebar, Card, badges, FraudGraph)
lib/api.ts             Centralized backend API client + TypeScript types
```

## Design tokens

- Navy `#0B1F3A` — primary
- Cream `#F7F5F0` — background
- Brass `#C9A34E` — accent / CTA
- Alert red `#B23A3A` — warnings, scam flags
- Fonts: Fraunces (display), Inter (body/UI)
