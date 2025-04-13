import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Télécharger les stopwords si nécessaire
nltk.download('stopwords')



   


def extract_skills(text):
    # Liste préétablie de compétences techniques et soft skills
    skills_list = ["développement web", "intelligence artificielle", "collaboration", "communication", "leadership"]
    
    # Extraction des compétences présentes dans le texte
    extracted_skills = [skill for skill in skills_list if skill.lower() in text.lower()]
    
    return extracted_skills
# summarization.py

import re

nltk.download('punkt')
nltk.download('stopwords')


 

import ollama

def extract_skills_with_llama(text):
    try:
        # Demande à LLaMA d'extraire les compétences techniques
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{"role": "user", "content": f"Extraire les compétences techniques à partir du texte suivant : {text}"}]
        )
        
        # Traitement de la réponse pour extraire les compétences
        skills = []
        for line in response['message']['content'].split('\n'):
            if line.strip():  # Vérifie si la ligne n'est pas vide
                skills.append(line.strip())
        
        return skills
    
    except Exception as e:
        return f"Erreur lors de l'extraction des compétences: {str(e)}"
import ollama
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords(text, lang='fr', max_words=15):
    stop_words = stopwords.words('french' if lang == 'fr' else 'english')
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        stop_words=stop_words,
        max_features=max_words
    )
    vectorizer.fit_transform([text])
    return vectorizer.get_feature_names_out().tolist()

def summarize_concisely(text):
    try:
        response = ollama.chat(
            model="llama3.2:latest",
            messages=[{
                "role": "user",
                "content": f"Résumez ce texte en 3 points clés : {text[:3000]}"
            }]
        )
        return response['message']['content']
    except Exception as e:
        return f"Erreur de génération : {str(e)}"
