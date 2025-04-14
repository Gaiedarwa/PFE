import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Télécharger les stopwords si nécessaire
nltk.download('stopwords')

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
        import ollama
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
