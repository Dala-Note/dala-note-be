from fastapi import APIRouter, HTTPException, Response
from typing import Optional
import base64

from ...models.schemas import TextToSpeechRequest, TextToSpeechResponse, ErrorResponse
from ...services.text_to_speech_service import tts_service

router = APIRouter()


@router.post("/synthesize", response_model=TextToSpeechResponse)
async def synthesize_speech(request: TextToSpeechRequest):

    try:
        # Validate text
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text is too long (max 5000 characters)")

        # Synthesize speech
        result = await tts_service.synthesize_speech(
            text=request.text,
            language_code=request.language_code,
            voice_name=request.voice_name,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch
        )

        return TextToSpeechResponse(
            audio_content=result["audio_content"],
            format=result["format"],
            message="Audio generated successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize-audio")
async def synthesize_speech_audio(request: TextToSpeechRequest):

    try:
        # Validate text
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        if len(request.text) > 5000:
            raise HTTPException(status_code=400, detail="Text is too long (max 5000 characters)")

        # Synthesize speech
        result = await tts_service.synthesize_speech(
            text=request.text,
            language_code=request.language_code,
            voice_name=request.voice_name,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch
        )

        # Decode base64 audio
        audio_bytes = base64.b64decode(result["audio_content"])

        # Return audio file
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_available_voices(language_code: Optional[str] = None):

    try:
        result = await tts_service.get_voices(language_code=language_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

