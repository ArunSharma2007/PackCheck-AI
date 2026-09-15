from pathlib import Path
import os
import shutil

import cv2
import pytesseract


TESSERACT_PATH = os.environ.get("TESSERACT_CMD")

if not TESSERACT_PATH:
    TESSERACT_PATH = shutil.which("tesseract")

if not TESSERACT_PATH and os.name == "nt":
    for candidate in (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(
            r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"
        ),
        os.path.expandvars(
            r"%LOCALAPPDATA%\Tesseract-OCR\tesseract.exe"
        )
    ):
        if Path(candidate).exists():
            TESSERACT_PATH = candidate
            break

if TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def ensure_tesseract_available():
    if not TESSERACT_PATH:
        raise RuntimeError(
            "Tesseract OCR is not installed or is not on PATH. "
            "Install Tesseract OCR or set the TESSERACT_CMD environment variable."
        )


def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    processed = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        11
    )

    return processed


def extract_text(image_path):
    ensure_tesseract_available()
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    processed_image = preprocess_image(image)

    text = pytesseract.image_to_string(
        processed_image,
        config="--psm 6"
    )

    return text.strip()


def extract_text_data(image_path):
    ensure_tesseract_available()
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    processed_image = preprocess_image(image)

    data = pytesseract.image_to_data(
        processed_image,
        output_type=pytesseract.Output.DICT
    )

    results = []

    for i in range(len(data["text"])):
        text = data["text"][i].strip()

        if not text:
            continue

        results.append({
            "text": text,
            "x": data["left"][i],
            "y": data["top"][i],
            "width": data["width"][i],
            "height": data["height"][i],
            "confidence": float(data["conf"][i])
        })

    return results


def calculate_readability(image_path):
    data = extract_text_data(image_path)

    if not data:
        return {
            "status": "UNREADABLE",
            "average_confidence": 0
        }

    confidences = [
        item["confidence"]
        for item in data
        if item["confidence"] >= 0
    ]

    if not confidences:
        return {
            "status": "UNREADABLE",
            "average_confidence": 0
        }

    average_confidence = sum(confidences) / len(confidences)

    if average_confidence >= 80:
        status = "GOOD"
    elif average_confidence >= 60:
        status = "MODERATE"
    else:
        status = "POOR"

    return {
        "status": status,
        "average_confidence": round(average_confidence, 2)
    }