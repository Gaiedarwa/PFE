# utils.py

import re

def clean_text(text):
    """
    Nettoie le texte en supprimant les espaces superflus et les caractères spéciaux.
    """
    text = text.replace("\n", " ").strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,-]', '', text)
    return text.lower()
