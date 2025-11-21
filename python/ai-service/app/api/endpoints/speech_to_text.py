from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
import os
import tempfile
from pathlib import Path

from ...models.schemas import SpeechToTextResponse, DetailedTranscriptionResponse, ErrorResponse
from ...services.speech_to_text_service import speech_service
from ...core.config import settings

router = APIRouter()


@router.post("/transcribe", response_model=SpeechToTextResponse)
async def transcribe_audio(
        audio_file: UploadFile = File(..., description="Audio file to transcribe"),
        language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'es', 'fr')"),
        task: str = Form("transcribe", description="Either 'transcribe' or 'translate'")
):

    # Validate file
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    allowed_extensions = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'}
    file_ext = Path(audio_file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
        )

    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Transcribe audio
        result = await speech_service.transcribe_audio_simple(
            temp_file_path,
            language=language
        )

        return SpeechToTextResponse(
            text=result,
            language=language
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary file
        if temp_file:
            try:
                os.unlink(temp_file_path)
            except:
                pass


@router.post("/transcribe-detailed", response_model=DetailedTranscriptionResponse)
async def transcribe_audio_detailed(
        audio_file: UploadFile = File(..., description="Audio file to transcribe"),
        language: Optional[str] = Form(None, description="Language code (e.g., 'en', 'es', 'fr')"),
        task: str = Form("transcribe", description="Either 'transcribe' or 'translate'")
):

    # Validate file
    if not audio_file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    allowed_extensions = {'.mp3', '.mp4', '.mpeg', '.mpga', '.m4a', '.wav', '.webm', '.ogg', '.flac'}
    file_ext = Path(audio_file.filename).suffix.lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
        )

    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Transcribe audio with detailed information
        result = await speech_service.transcribe_audio(
            temp_file_path,
            language=language,
            task=task
        )

        return DetailedTranscriptionResponse(
            text=result["text"],
            language=result.get("language"),
            segments=result.get("segments", [])
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Clean up temporary file
        if temp_file:
            try:
                os.unlink(temp_file_path)
            except:
                pass

