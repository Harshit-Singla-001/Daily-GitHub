import os

import pytesseract

from PIL import Image, ImageOps, ImageFilter

from config import TESSERACT_CMD


def configure_tesseract():
    if TESSERACT_CMD and os.path.exists(
        TESSERACT_CMD
    ):
        pytesseract.pytesseract.tesseract_cmd = (
            TESSERACT_CMD
        )
        return True

    return False


def preprocess_image(image):
    image = image.convert("RGB")

    width, height = image.size

    if width < 1200:
        scale = 1200 / width

        image = image.resize(
            (
                int(width * scale),
                int(height * scale)
            )
        )

    grayscale = ImageOps.grayscale(
        image
    )

    grayscale = ImageOps.autocontrast(
        grayscale
    )

    grayscale = grayscale.filter(
        ImageFilter.SHARPEN
    )

    return grayscale


def extract_text_from_image(
    image_path
):
    if not configure_tesseract():
        return {
            "success": False,
            "error": (
                "Tesseract OCR was not found. "
                "Install Tesseract or set "
                "TESSERACT_CMD in .env."
            )
        }

    try:
        with Image.open(image_path) as image:

            processed_image = preprocess_image(
                image
            )

            text = pytesseract.image_to_string(
                processed_image,
                config="--psm 6"
            )

        return {
            "success": True,
            "text": text,
            "method": "Tesseract OCR"
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }


def extract_text_from_pil_image(
    image
):
    if not configure_tesseract():
        return {
            "success": False,
            "error": (
                "Tesseract OCR was not found."
            )
        }

    try:
        processed_image = preprocess_image(
            image
        )

        text = pytesseract.image_to_string(
            processed_image,
            config="--psm 6"
        )

        return {
            "success": True,
            "text": text,
            "method": "Tesseract OCR"
        }

    except Exception as error:
        return {
            "success": False,
            "error": str(error)
        }