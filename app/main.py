"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import health, chat, session
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Telemed Agents",
    description="Agentic AI Chatbot for Telemedicine",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(session.router, tags=["Session"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Telemed Agents API",
        "version": "0.1.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
