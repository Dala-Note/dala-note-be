from pydantic import BaseModel, Field
from typing import Optional, List


# Speech to Text Models
class SpeechToTextResponse(BaseModel):
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None


class TranscriptionSegment(BaseModel):
    start: float
    end: float
    text: str


class DetailedTranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    segments: List[TranscriptionSegment] = []
    duration: Optional[float] = None


# OCR Models
class OCRResponse(BaseModel):
    text: str
    confidence: Optional[float] = None


class OCRDetailedResponse(BaseModel):
    text: str
    words: List[dict] = []
    confidence: Optional[float] = None


# Text to Speech Models
class TextToSpeechRequest(BaseModel):
    text: str = Field(..., description="Text to convert to speech")
    language_code: str = Field(default="en-US", description="Language code (e.g., en-US, es-ES)")
    voice_name: Optional[str] = Field(default=None, description="Specific voice name")
    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0, description="Speaking rate (0.25 to 4.0)")
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0, description="Voice pitch (-20.0 to 20.0)")


class TextToSpeechResponse(BaseModel):
    audio_content: str  # Base64 encoded audio
    format: str = "mp3"
    message: str = "Audio generated successfully"


# General Models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None

