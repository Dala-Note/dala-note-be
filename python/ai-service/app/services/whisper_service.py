import subprocess
import json
import time
import os
from typing import Optional, Dict, Any
from pathlib import Path

from ..core.config import settings
from ..models.transcription import TranscriptionResponse, AudioSegment


class WhisperService:
    
    
    def __init__(self):
        self.model_path = settings.WHISPER_MODEL_PATH
        self.threads = settings.WHISPER_THREADS
        self.processors = settings.WHISPER_PROCESSORS
        self._verify_whisper_installation()
    
    def _verify_whisper_installation(self):
        """Verify whisper.cpp is installed and model exists"""
        try:
            # Check if whisper executable exists
            result = subprocess.run(
                ["which", "whisper"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError("whisper.cpp not found in PATH")
            
            # Check if model file exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Whisper model not found at {self.model_path}")
                
        except Exception as e:
            print(f"Warning: Whisper verification failed: {e}")
    
    async def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
       
        start_time = time.time()
        
        # Build whisper.cpp command
        cmd = [
            "whisper",
            "-m", self.model_path,
            "-f", audio_path,
            "-t", str(self.threads),
            "-p", str(self.processors),
            "-oj",  # Output JSON
        ]
        
        # Add language if specified
        if language:
            cmd.extend(["-l", language])
        
        try:
            # Run whisper.cpp
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse JSON output
            output_json_path = audio_path + ".json"
            
            if os.path.exists(output_json_path):
                with open(output_json_path, 'r') as f:
                    whisper_output = json.load(f)
                
                # Clean up JSON file
                os.unlink(output_json_path)
            else:
                # Fallback: parse stdout
                whisper_output = self._parse_output(result.stdout)
            
            # Get audio duration
            duration = self._get_audio_duration(audio_path)
            
            # Extract segments
            segments = []
            if "transcription" in whisper_output:
                for seg in whisper_output.get("transcription", []):
                    if isinstance(seg, dict):
                        segments.append(AudioSegment(
                            start=seg.get("timestamps", {}).get("from", 0) / 100,
                            end=seg.get("timestamps", {}).get("to", 0) / 100,
                            text=seg.get("text", ""),
                            confidence=None
                        ))
            
            # Build response
            processing_time = time.time() - start_time
            full_text = " ".join([seg.text for seg in segments]) if segments else whisper_output.get("text", "")
            
            return {
                "text": full_text.strip(),
                "language": language or "en",
                "duration": duration,
                "segments": [seg.model_dump() for seg in segments] if segments else None,
                "processing_time": round(processing_time, 2)
            }
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Whisper transcription failed: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Error during transcription: {str(e)}")
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio file duration using ffprobe"""
        try:
            cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return float(result.stdout.strip())
        except:
            return 0.0
    
    def _parse_output(self, output: str) -> Dict[str, Any]:
        """Parse whisper output if JSON parsing fails"""
        return {
            "text": output.strip(),
            "transcription": []
        }
