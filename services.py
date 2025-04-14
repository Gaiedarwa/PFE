import pytesseract
import fitz
from PIL import Image
import io
import re

# Configuration de Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Fonction pour nettoyer le texte
def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Fonction pour extraire du texte d'un fichier PDF
def extract_text_from_pdf(file):
    from pdfminer.high_level import extract_text
    return clean_text(extract_text(file))

# Fonction pour extraire du texte d'une image
def extract_text_from_image(file):
    image = Image.open(io.BytesIO(file.read()))
    return clean_text(pytesseract.image_to_string(image, lang="fra"))

import pytesseract
import fitz
from PIL import Image
import io
import tempfile

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def process_document(file):
    if not file:
        return ""
    
    if file.filename.lower().endswith('.pdf'):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            with fitz.open(tmp.name) as doc:
                return " ".join([page.get_text() for page in doc])
    
    elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image = Image.open(io.BytesIO(file.read()))
        return pytesseract.image_to_string(image, lang='fra+eng')
    
    return ""
def remove_sensitive_data(text: str) -> str:
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', '[EMAIL]', text)
    text = re.sub(r'\b\d{2,4}[-.\s]??\d{2,4}[-.\s]??\d{2,4}', '[PHONE]', text)
    text = re.sub(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b', '[NAME]', text)
    return text