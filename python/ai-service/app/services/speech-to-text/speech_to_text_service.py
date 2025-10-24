import os
import tempfile
import subprocess
from fastapi import HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.utils.audio_utils import convert_to_wav
from app.utils.file_utils import validate_file_size

class TranscriptionService:
    def __init__(self):
        self.settings = settings
    
    async def transcribe_file(self, file: UploadFile) -> JSONResponse:
        """Transcribe uploaded audio file"""
        temp_file_path = None
        wav_file_path = None
        
        try:
            temp_file_path = await self._save_uploaded_file(file)
            
            wav_file_path = await convert_to_wav(temp_file_path)
            
            transcription = await self._run_whisper(wav_file_path)
            
            return JSONResponse(content={
                "text": transcription.strip(),
                "filename": file.filename
            })
            
        finally:
            
            self._cleanup_files(temp_file_path, wav_file_path)
    
    async def _save_uploaded_file(self, file: UploadFile) -> str:
        """Save uploaded file to temporary location"""
        file_size = 0
        chunk_size = 1024 * 1024
        
        with tempfile.NamedTemporaryFile(
            delete=False, 
            suffix=os.path.splitext(file.filename),[object Object],
        ) as temp_file:
            temp_file_path = temp_file.name
            
            while chunk := await file.read(chunk_size):
                file_size += len(chunk)
                validate_file_size(file_size, self.settings.MAX_FILE_SIZE)
                temp_file.write(chunk)
        
        return temp_file_path
    
    async def _run_whisper(self, wav_file_path: str) -> str:
        """Run whisper.cpp transcription"""
        whisper_executable = self._get_whisper_executable()
        
        try:
            result = subprocess.run([
                whisper_executable,
                '-m', self.settings.MODEL_PATH,
                '-f', wav_file_path,
                '-nt'
            ], capture_output=True, text=True, check=True)
            
            output = result.stdout
            lines = output.split('\n')
            transcription_lines = [
                line.strip() for line in lines 
                if line.strip() and not line.startswith('[')
            ]
            
            return ' '.join(transcription_lines)
            
        except subprocess.CalledProcessError as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Whisper transcription failed: {e.stderr}"
            )
        except FileNotFoundError:
            raise HTTPException(
                status_code=500,
                detail=f"Whisper executable not found at {whisper_executable}"
            )
    
    def _get_whisper_executable(self) -> str:
        """Find the whisper executable"""
        if os.path.exists(self.settings.WHISPER_EXECUTABLE):
            return self.settings.WHISPER_EXECUTABLE
        

        alt_paths = [
            os.path.join(self.settings.WHISPER_CPP_PATH, 'build', 'bin', 'whisper-cli'),
            os.path.join(self.settings.WHISPER_CPP_PATH, 'main'),
            './whisper.cpp/build/bin/whisper-cli'
        ]
        
        for path in alt_paths:
            if os.path.exists(path):
                return path
        
        raise HTTPException(
            status_code=500,
            detail="Whisper executable not found"
        )
    
    def _cleanup_files(self, *file_paths):
        """Clean up temporary files"""
        for file_path in file_paths:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
    
    def get_health_status(self) -> dict:
        """Get health check status"""
        whisper_exec_exists = os.path.exists(self.settings.WHISPER_EXECUTABLE)
        
        if not whisper_exec_exists:
            alt_paths = [
                os.path.join(self.settings.WHISPER_CPP_PATH, 'build', 'bin', 'whisper-cli'),
                os.path.join(self.settings.WHISPER_CPP_PATH, 'main')
            ]
            whisper_exec_exists = any(os.path.exists(p) for p in alt_paths)
        
        return {
            "status": "healthy",
            "whisper_cpp_exists": os.path.exists(self.settings.WHISPER_CPP_PATH),
            "model_exists": os.path.exists(self.settings.MODEL_PATH),
            "whisper_executable_exists": whisper_exec_exists,
            "whisper_executable_path": self.settings.WHISPER_EXECUTABLE
        }
