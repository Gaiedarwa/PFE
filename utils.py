# utils.py

import re
from PyPDF2 import PdfReader
def clean_text(text):
    """
    Nettoie le texte en supprimant les espaces superflus et les caractères spéciaux.
    """
    text = text.replace("\n", " ").strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,-]', '', text)
    return text.lower()


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text
def remove_sensitive_data(text: str) -> str:
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}', '[EMAIL]', text)
    text = re.sub(r'\b\d{2,4}[-.\s]??\d{2,4}[-.\s]??\d{2,4}', '[PHONE]', text)
    text = re.sub(r'\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b', '[NAME]', text)
    return text
