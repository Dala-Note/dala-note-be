from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import speech_to_text, ocr, text_to_speech

app = FastAPI(
    title="AI Services API",
    description="FastAPI backend for AI services including Speech-to-Text, OCR, and Text-to-Speech",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(speech_to_text.router, prefix="/api/v1/speech", tags=["Speech-to-Text"])
app.include_router(ocr.router, prefix="/api/v1/ocr", tags=["OCR"])
app.include_router(text_to_speech.router, prefix="/api/v1/tts", tags=["Text-to-Speech"])

@app.get("/")
async def root():
    return {
        "message": "AI Services API",
        "version": "1.0.0",
        "services": ["speech-to-text", "ocr", "text-to-speech"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

