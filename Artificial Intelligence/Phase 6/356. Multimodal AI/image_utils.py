import os
from PIL import Image

from config import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE
)


def allowed_file(filename):
    if not filename:
        return False

    if "." not in filename:
        return False

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    return extension in ALLOWED_EXTENSIONS


def validate_image(file):
    if not file:
        return False, "No image was provided."

    if not file.filename:
        return False, "Invalid filename."

    if not allowed_file(file.filename):
        return False, (
            "Unsupported image format. "
            "Use JPG, JPEG, PNG or WEBP."
        )

    file.seek(0, os.SEEK_END)

    file_size = file.tell()

    file.seek(0)

    if file_size > MAX_FILE_SIZE:
        return False, (
            "Image is too large. "
            "Maximum size is 5 MB."
        )

    try:
        image = Image.open(file)

        image.verify()

        file.seek(0)

        return True, "Valid image."

    except Exception:
        return False, "The uploaded file is not a valid image."


def get_image_info(image_path):
    try:
        with Image.open(image_path) as image:
            return {
                "format": image.format,
                "width": image.width,
                "height": image.height,
                "mode": image.mode
            }

    except Exception as error:
        return {
            "error": str(error)
        }