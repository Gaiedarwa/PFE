import pytesseract
import fitz
from PIL import Image
import io
import re

# Configuration de Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# Fonction pour nettoyer le texte
# services.py
def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    return text  # Supprime uniquement les espaces superflus


# Fonction pour extraire du texte d'un fichier PDF
def extract_text_from_pdf(file):
    from pdfminer.high_level import extract_text
    return clean_text(extract_text(file))

# Fonction pour extraire du texte d'une image
def extract_text_from_image(file):
    image = Image.open(io.BytesIO(file.read()))
    return clean_text(pytesseract.image_to_string(image, lang="fra"))

# Fonction de traitement du document (PDF ou image)
def process_document(file):
    if file.filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file)
    elif file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        return extract_text_from_image(file)
    return ""
