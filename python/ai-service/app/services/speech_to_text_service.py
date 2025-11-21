import whisper
import os
from typing import Optional, Dict
import tempfile
from pathlib import Path


class SpeechToTextService:
    def __init__(self, model_name: str = "base"):

        self.model_name = model_name
        self.model = None

    def load_model(self):
        if self.model is None:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)

    async def transcribe_audio(
            self,
            audio_path: str,
            language: Optional[str] = None,
            task: str = "transcribe"
    ) -> Dict:

        self.load_model()

        try:
            # Transcribe the audio
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                verbose=False
            )

            return {
                "text": result["text"].strip(),
                "language": result.get("language"),
                "segments": [
                    {
                        "start": seg["start"],
                        "end": seg["end"],
                        "text": seg["text"].strip()
                    }
                    for seg in result.get("segments", [])
                ]
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

    async def transcribe_audio_simple(
            self,
            audio_path: str,
            language: Optional[str] = None
    ) -> str:

        result = await self.transcribe_audio(audio_path, language)
        return result["text"]


# Global instance
speech_service = SpeechToTextService()

