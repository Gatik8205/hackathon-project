from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import scam, currency, graph, chatbot

app = FastAPI(
    title="RakshakAI Backend",
    description="AI Public Safety Intelligence Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scam.router)
app.include_router(currency.router)
app.include_router(graph.router)
app.include_router(chatbot.router)


@app.get("/")
def root():
    return {
        "status": "Backend Running 🚀",
        "project": "RakshakAI",
        "version": "1.0.0"
    }