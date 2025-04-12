import re
from sentence_transformers import SentenceTransformer, util
from functools import lru_cache

# Chargement du modèle SentenceTransformer avec cache pour optimiser les performances
@lru_cache(maxsize=1)
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

# models.py
def extract_entities(text):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    phone_pattern = r'\+?\d{1,4}[-.\s]?(?:\(\d+\)[-.\s]?)?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    phone = phone_match.group() if phone_match else ''
    name_pattern = r'(?i)\b(?:[A-ZÀ-ÂÇÉÈÊËÎÏÔÙÛÜ][a-zà-âçéèêëîïôùûü]+\b[\s-]*){2,}'

    # Recherche dans tout le texte
    email_match = re.search(email_pattern, text)
   
    name_match = re.findall(name_pattern, text)  # Trouve toutes les occurrences

    # Prend le premier nom trouvé
    name = name_match[0].strip() if name_match else ''

    return {
        'nom': name,
        'email': email_match.group().lower() if email_match else '',
        'téléphone': phone
    }

# Calcul de la similarité entre le CV et l'offre d'emploi
def calculate_similarity(text1: str, text2: str) -> float:
    model = get_model()
    emb1 = model.encode(text1[:1000], convert_to_tensor=True)  # Limite la taille du texte
    emb2 = model.encode(text2[:1000], convert_to_tensor=True)
    score = util.cos_sim(emb1, emb2).item()
    return round(score * 100, 2)

# Validation des informations personnelles (nom et email obligatoires)
def validate_personal_info(info):
    if not info.get("nom") or not info.get("email"):
        raise ValueError("Le champ 'nom' ou 'email' est vide.")
