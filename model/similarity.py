import re
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer, util
from langchain_ollama import OllamaLLM
import spacy

# Optionally, load a spaCy model (for English or French, etc.)
# For English:
nlp = spacy.load("en_core_web_sm")
# For French, you might use: spacy.load("fr_core_news_sm")

def extract_text_from_pdf(pdf_path):
    try:
        reader = PdfReader(pdf_path)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction du texte du PDF : {e}")

def extract_key_sentences(text):
    try:
        llm = OllamaLLM(model="llama3.2")
        prompt = f"Extrayez les technical and soft skills \n\n{text}\n\nPhrases clés :"
        response = llm.invoke(prompt)
        return response.strip()
    
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction des compétences : {e}")

def extract_profile_name_using_llm(cv_text):
    try:
        llm = OllamaLLM(model="llama3.2")
        prompt = (
            "Extrait uniquement le nom et le prénom du candidat à partir du CV suivant. "
            "Retourne uniquement le nom complet au format 'Prénom Nom'.\n\n"
            f"CV:\n\n{cv_text}\n\nNom et Prénom :"
        )
        response = llm.invoke(prompt)
        return response.strip()
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction du nom avec LLM : {e}")

def extract_profile_name_with_ner(cv_text):
    # Using spaCy to detect PERSON entities in the text
    doc = nlp(cv_text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()
    return "N/A"

def extract_profile_name(cv_text):
    # Combine both approaches: first try LLM, then fallback to spaCy NER if needed.
    name = extract_profile_name_using_llm(cv_text)
    if name == "N/A" or not name:
        name = extract_profile_name_with_ner(cv_text)
    return name

def extract_candidate_email(cv_text):
    try:
        llm = OllamaLLM(model="llama3.2")
        prompt = (
            f"Extrait uniquement l'adresse email du candidat à partir du CV suivant :\n\n"
            f"{cv_text}\n\nEmail :"
        )
        response = llm.invoke(prompt)
        return response.strip()
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction de l'email : {e}")

def extract_candidate_phone(cv_text):
    try:
        # Try regex first
        phone_regex = re.compile(r'(\+?\d{1,3}[\s\-]?\(?\d+\)?(?:[\s\-]?\d+){5,}|\b\d{8}\b)')
        match = phone_regex.search(cv_text)
        if match:
            return match.group(1).strip()
        # Fallback to LLM if regex doesn't find anything
        llm = OllamaLLM(model="llama3.2")
        prompt = (
            "Extrait uniquement le numéro de téléphone du candidat à partir du CV suivant. "
            "Le numéro doit être renvoyé uniquement sous forme de chiffres et symboles, "
            "au format international (ex : '+33 6 12 34 56 78') ou sous forme simple (ex: 56314582), "
            "sans texte additionnel :\n\n"
            f"CV:\n\n{cv_text}\n\nTéléphone:"
        )
        response = llm.invoke(prompt)
        return response.strip()
    except Exception as e:
        raise ValueError(f"Erreur lors de l'extraction du numéro de téléphone : {e}")

def generate_profile_summary(cv_text, job_text):
    try:
        llm = OllamaLLM(model="llama3.2")
        prompt = (
            f"À partir du CV suivant :\n\n{cv_text}\n\n"
            f"et de l'offre d'emploi suivante :\n\n{job_text}\n\n"
            f"Rédige un résumé très court, en une ou deux phrases maximum, qui met en avant les compétences et l'expérience du candidat de façon concrète :"
        )
        response = llm.invoke(prompt)
        summary = response.strip()
        # Limiter à deux lignes maximum
        lines = summary.splitlines()
        summary_short = " ".join(lines[:2]).strip()
        return summary_short
    except Exception as e:
        raise ValueError(f"Erreur lors de la génération du résumé : {e}")

def calculate_similarity(job_pdf_path, cv_pdf_path):
    try:
        job_text = extract_text_from_pdf(job_pdf_path)
        cv_text = extract_text_from_pdf(cv_pdf_path)
        if not job_text or not cv_text:
            raise ValueError("Impossible d'extraire le texte des fichiers PDF.")

        job_skills = extract_key_sentences(job_text)
        cv_skills = extract_key_sentences(cv_text)

        model = SentenceTransformer('all-MiniLM-L6-v2')
        job_embedding = model.encode(job_skills, convert_to_tensor=True)
        cv_embedding = model.encode(cv_skills, convert_to_tensor=True)
        cosine_sim = util.cos_sim(job_embedding, cv_embedding)
        similarity = float(cosine_sim.cpu().numpy()[0][0]) * 100.0
        similarity = round(similarity, 2)

        profile_name = extract_profile_name(cv_text)
        candidate_email = extract_candidate_email(cv_text)
        candidate_phone = extract_candidate_phone(cv_text)
        profile_summary = generate_profile_summary(cv_text, job_text)

        result = {
            "nom": profile_name,
            "email": candidate_email,
            "téléphone": candidate_phone,
            "score": similarity,
            "résumé": profile_summary
        }
        return result
    except Exception as e:
        raise ValueError(f"Erreur lors du calcul de la similarité : {e}")

if __name__ == "__main__":
    job_pdf = "chemin/vers/offre.pdf"  # Replace with your job offer PDF path
    cv_pdf = "chemin/vers/cv.pdf"        # Replace with your CV PDF path
    output = calculate_similarity(job_pdf, cv_pdf)
    print(output)
