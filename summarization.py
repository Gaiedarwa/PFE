import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Télécharger les stopwords si nécessaire
nltk.download('stopwords')



# Fonction pour extraire les mots-clés d'un texte
def extract_keywords(text, max_words=10):
    stop_words_fr = set(stopwords.words('french'))
    
    vectorizer = TfidfVectorizer(stop_words=list(stop_words_fr), ngram_range=(1, 2), max_features=50)
    tfidf_matrix = vectorizer.fit_transform([text])
    
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sorting = tfidf_matrix.sum(axis=0).A1.argsort()[::-1]
    
    return [feature_names[i] for i in tfidf_sorting[:max_words]]


def extract_skills(text):
    # Liste préétablie de compétences techniques et soft skills
    skills_list = ["développement web", "intelligence artificielle", "collaboration", "communication", "leadership"]
    
    # Extraction des compétences présentes dans le texte
    extracted_skills = [skill for skill in skills_list if skill.lower() in text.lower()]
    
    return extracted_skills
# summarization.py
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
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

def summarize_concisely(text):
    try:
        # Extraction des compétences techniques avec LLaMA
        skills = extract_skills_with_llama(text)
        
        # Génération du résumé
        if skills:
            summary = f"Compétences clés : {', '.join(skills[:10])}"  # Limite à 10 compétences
        else:
            summary = "Compétences clés : Aucune compétence technique détectée."
        
        return summary
    
    except Exception as e:
        return f"Erreur lors de la génération du résumé: {str(e)}"
