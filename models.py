import re
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache
import ollama

@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def extract_entities(text):
    patterns = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b',
        'téléphone': r'\+?\d{1,4}[-.\s]?(?:\(\d+\)[-.\s]?)?\d{3}[-.\s]?\d{4}',
        'nom': r'(?i)\b(?:[A-ZÀ-ÂÇÉÈÊËÎÏÔÙÛÜ][a-zà-âçéèêëîïôùûü]+\b[\s-]*){2,}'
    }
    
    entities = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            entities[key] = match.group().strip()
    
    return entities

def mask_sensitive_info(text, entities):
    for value in entities.values():
        if value:
            text = text.replace(value, '[REDACTED]')
    return text

def calculate_similarity(text1, text2):
    model = get_model()
    embedding1 = model.encode(text1, convert_to_tensor=True)
    embedding2 = model.encode(text2, convert_to_tensor=True)
    return round(util.cos_sim(embedding1, embedding2).item() * 100, 2)

def validate_personal_info(info):
    if not info.get('email'):
        raise ValueError("L'email est requis")
