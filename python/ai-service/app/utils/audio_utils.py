import subprocess
import os
from typing import Optional
from pathlib import Path


def validate_audio_file(file_path: str, max_size_mb: int = 25) -> bool:
    
    if not os.path.exists(file_path):
        return False
    
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False
    
    return True


def convert_audio(
    input_path: str,
    output_path: Optional[str] = None,
    sample_rate: int = 16000,
    channels: int = 1
) -> str:
    
    if output_path is None:
        output_path = str(Path(input_path).with_suffix('.wav'))
    
    try:
        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-c:a", "pcm_s16le",
            "-y",  # Overwrite output
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
        
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Audio conversion failed: {e.stderr.decode()}")


def get_audio_info(file_path: str) -> dict:
    
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration,size,bit_rate",
            "-show_entries", "stream=codec_name,sample_rate,channels",
            "-of", "json",
            file_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        import json
        return json.loads(result.stdout)
        
    except Exception as e:
        return {"error": str(e)}
