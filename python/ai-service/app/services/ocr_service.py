import pytesseract
from PIL import Image
import os
from typing import Optional, Dict, List
from ..core.config import settings


class OCRService:
    def __init__(self):
        # Set Tesseract command path if specified in config
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    async def extract_text(
            self,
            image_path: str,
            language: str = "eng",
            detailed: bool = False
    ) -> Dict:

        try:
            # Open the image
            image = Image.open(image_path)

            if detailed:
                # Get detailed data including bounding boxes and confidence
                data = pytesseract.image_to_data(
                    image,
                    lang=language,
                    output_type=pytesseract.Output.DICT
                )

                # Extract text
                text = pytesseract.image_to_string(image, lang=language)

                # Process word-level data
                words = []
                n_boxes = len(data['text'])
                for i in range(n_boxes):
                    if int(data['conf'][i]) > 0:  # Filter out low confidence
                        words.append({
                            'text': data['text'][i],
                            'confidence': float(data['conf'][i]),
                            'left': int(data['left'][i]),
                            'top': int(data['top'][i]),
                            'width': int(data['width'][i]),
                            'height': int(data['height'][i])
                        })

                # Calculate average confidence
                confidences = [w['confidence'] for w in words if w['confidence'] > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0

                return {
                    "text": text.strip(),
                    "confidence": round(avg_confidence, 2),
                    "words": words
                }
            else:
                # Simple text extraction
                text = pytesseract.image_to_string(image, lang=language)
                return {
                    "text": text.strip(),
                    "confidence": None
                }

        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")

    async def extract_text_simple(
            self,
            image_path: str,
            language: str = "eng"
    ) -> str:

        result = await self.extract_text(image_path, language)
        return result["text"]

    def get_available_languages(self) -> List[str]:

        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            return ["eng"]  # Return default if unable to get languages


# Global instance
ocr_service = OCRService()

