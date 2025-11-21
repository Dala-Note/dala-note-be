from gtts import gTTS
import os
from typing import Optional, Dict
import base64
import io
from ..core.config import settings


class TextToSpeechService:
    def __init__(self):
        """Initialize the Text-to-Speech service using gTTS"""
        # Map common language codes to gTTS language codes
        self.language_map = {
            "en-US": "en",
            "en-GB": "en",
            "es-ES": "es",
            "es-US": "es",
            "fr-FR": "fr",
            "de-DE": "de",
            "it-IT": "it",
            "pt-BR": "pt",
            "ja-JP": "ja",
            "ko-KR": "ko",
            "zh-CN": "zh-CN",
            "zh-TW": "zh-TW",
            "ru-RU": "ru",
            "ar-AR": "ar",
            "hi-IN": "hi",
        }

    def _get_language_code(self, lang_code: str) -> str:
        return self.language_map.get(lang_code, lang_code.split('-')[0])

    async def synthesize_speech(
            self,
            text: str,
            language_code: str = "en-US",
            voice_name: Optional[str] = None,
            speaking_rate: float = 1.0,
            pitch: float = 0.0
    ) -> Dict:

        try:
            # Convert language code
            gtts_lang = self._get_language_code(language_code)

            # Use slow mode if speaking rate is less than 0.8
            use_slow = speaking_rate < 0.8

            # Generate speech using gTTS
            tts = gTTS(text=text, lang=gtts_lang, slow=use_slow)

            # Save to a BytesIO object
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Read audio content
            audio_content = audio_buffer.read()

            # Encode audio content as base64
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')

            return {
                "audio_content": audio_base64,
                "format": "mp3",
                "language_code": language_code
            }

        except Exception as e:
            raise Exception(f"Text-to-speech synthesis failed: {str(e)}")

    async def get_voices(self, language_code: Optional[str] = None) -> Dict:

        try:
            # List of supported languages with gTTS
            supported_languages = [
                {"name": "English (US)", "code": "en-US", "gender": "NEUTRAL"},
                {"name": "English (UK)", "code": "en-GB", "gender": "NEUTRAL"},
                {"name": "Spanish (Spain)", "code": "es-ES", "gender": "NEUTRAL"},
                {"name": "Spanish (US)", "code": "es-US", "gender": "NEUTRAL"},
                {"name": "French", "code": "fr-FR", "gender": "NEUTRAL"},
                {"name": "German", "code": "de-DE", "gender": "NEUTRAL"},
                {"name": "Italian", "code": "it-IT", "gender": "NEUTRAL"},
                {"name": "Portuguese (Brazil)", "code": "pt-BR", "gender": "NEUTRAL"},
                {"name": "Japanese", "code": "ja-JP", "gender": "NEUTRAL"},
                {"name": "Korean", "code": "ko-KR", "gender": "NEUTRAL"},
                {"name": "Chinese (Mandarin)", "code": "zh-CN", "gender": "NEUTRAL"},
            ]

            if language_code:
                filtered = [v for v in supported_languages if v["code"] == language_code]
                return {"voices": filtered}

            return {"voices": supported_languages}

        except Exception as e:
            raise Exception(f"Failed to get voices: {str(e)}")


# Global instance
tts_service = TextToSpeechService()

