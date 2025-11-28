from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
import os
import tempfile

from ...core.config import settings
from ...services.whisper_service import WhisperService

router = APIRouter(prefix="/transcribe", tags=["transcription"])
whisper_service = WhisperService()


@router.post("")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: Optional[str] = None,
    background_tasks: BackgroundTasks = None
):
    
    # Validate file type
    allowed_extensions = {'.wav', '.mp3', '.m4a', '.ogg', '.flac', '.webm'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Create temporary file
    temp_file = None
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp:
            content = await file.read()
            temp.write(content)
            temp_file = temp.name
        
        # Transcribe audio
        result = await whisper_service.transcribe(
            audio_path=temp_file,
            language=language
        )
        
        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(cleanup_temp_file, temp_file)
        
        return JSONResponse(content=result)
    
    except Exception as e:
        # Cleanup on error
        if temp_file and os.path.exists(temp_file):
            os.unlink(temp_file)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def transcribe_audio_stream(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    
    # Implementation for streaming transcription
    raise HTTPException(status_code=501, detail="Streaming not yet implemented")


def cleanup_temp_file(file_path: str):
    
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        print(f"Error cleaning up temp file: {e}")
