from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
import os
import tempfile
from pathlib import Path

from ...models.schemas import OCRResponse, OCRDetailedResponse, ErrorResponse
from ...services.ocr_service import ocr_service

router = APIRouter()


@router.post("/extract-text", response_model=OCRResponse)
async def extract_text_from_image(
        image_file: UploadFile = File(..., description="Image file to extract text from"),
        language: str = Form("eng", description="Language code (e.g., 'eng', 'spa', 'fra')")
):

    # Validate file
    if not image_file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}
    file_ext = Path(image_file.filename).suffix.lower()

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
            content = await image_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Extract text from image
        result = await ocr_service.extract_text(
            temp_file_path,
            language=language,
            detailed=False
        )

        return OCRResponse(
            text=result["text"],
            confidence=result.get("confidence")
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


@router.post("/extract-text-detailed", response_model=OCRDetailedResponse)
async def extract_text_from_image_detailed(
        image_file: UploadFile = File(..., description="Image file to extract text from"),
        language: str = Form("eng", description="Language code (e.g., 'eng', 'spa', 'fra')")
):

    # Validate file
    if not image_file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.gif'}
    file_ext = Path(image_file.filename).suffix.lower()

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
            content = await image_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Extract text from image with detailed information
        result = await ocr_service.extract_text(
            temp_file_path,
            language=language,
            detailed=True
        )

        return OCRDetailedResponse(
            text=result["text"],
            confidence=result.get("confidence"),
            words=result.get("words", [])
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


@router.get("/languages")
async def get_available_languages():

    try:
        languages = ocr_service.get_available_languages()
        return {"languages": languages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

