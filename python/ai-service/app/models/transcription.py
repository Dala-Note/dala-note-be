from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class AudioSegment(BaseModel):
    
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    text: str = Field(..., description="Transcribed text for this segment")
    confidence: Optional[float] = Field(None, description="Confidence score")


class TranscriptionRequest(BaseModel):
    
    language: Optional[str] = Field(None, description="Language code (e.g., 'en', 'es')")
    translate: bool = Field(False, description="Translate to English")
    word_timestamps: bool = Field(False, description="Include word-level timestamps")


class TranscriptionResponse(BaseModel):
    
    text: str = Field(..., description="Full transcribed text")
    language: str = Field(..., description="Detected or specified language")
    duration: float = Field(..., description="Audio duration in seconds")
    segments: Optional[List[AudioSegment]] = Field(None, description="Transcription segments")
    processing_time: float = Field(..., description="Time taken to process in seconds")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of transcription")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a test transcription.",
                "language": "en",
                "duration": 5.2,
                "segments": [
                    {
                        "start": 0.0,
                        "end": 5.2,
                        "text": "Hello, this is a test transcription.",
                        "confidence": 0.95
                    }
                ],
                "processing_time": 1.3,
                "timestamp": "2025-10-26T12:00:00Z"
            }
        }
