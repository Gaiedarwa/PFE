from flask import request, jsonify
from services import process_document, clean_text
from models import extract_entities, validate_personal_info
from models import calculate_similarity
from summarization import summarize_concisely, extract_keywords
from database import cv_collection
from technical_test import generate_tests, select_random_test, get_user_input
import re

# Vérification de la taille du fichier
def file_too_large(file, max_size_mb=5):
    file.seek(0, 2)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    return size_mb > max_size_mb

# Initialisation des routes Flask
def init_routes(app):
    @app.route('/similarity', methods=['POST'])
    def similarity():
        try:
            file_cv = request.files.get("cv")
            file_job = request.files.get("job")
            text_cv = request.form.get("text_cv")
            text_job = request.form.get("text_job")

            if not (file_cv or text_cv) or not (file_job or text_job):
                return jsonify({"error": "Veuillez fournir un CV et une offre d'emploi (fichier ou texte)."}), 400

            if file_cv and file_too_large(file_cv):
                return jsonify({"error": "Fichier CV trop volumineux."}), 400
            if file_job and file_too_large(file_job):
                return jsonify({"error": "Fichier offre trop volumineux."}), 400

            # Traitement des fichiers ou du texte
            cv_text = process_document(file_cv) if file_cv else clean_text(text_cv)
            job_text = process_document(file_job) if file_job else clean_text(text_job)

            # Extraction des informations personnelles du CV
            personal_info = extract_entities(cv_text)

            # Validation alternative si les champs sont vides
            if not personal_info.get('email'):
                backup_email = re.findall(r'\S+@\S+', cv_text)
                if backup_email:
                    personal_info['email'] = backup_email[0]

            # Validation des informations personnelles
            try:
                validate_personal_info(personal_info)
            except ValueError as e:
                return jsonify({"error": str(e)}), 400

            # Génération des résumés concis et mots-clés
            cv_summary = summarize_concisely(cv_text)
            job_keywords = extract_keywords(job_text)

            # Calcul du score de similarité (après nettoyage du texte)
            score = calculate_similarity(cv_text, job_text)

            # Détermination du niveau en fonction du score
            niveau = "Senior" if score >= 70 else "Junior"

            # Génération des tests techniques
            competencies_str, difficulty_str = get_user_input(job_keywords[:5], niveau)
            tests_techniques = generate_tests(competencies_str, difficulty_str)
            selected_test = select_random_test(tests_techniques)

            # Création de la réponse à retourner
            response_data = {
                "cv": {
                    "nom": personal_info.get("nom"),
                    "email": personal_info.get("email"),
                    "téléphone": personal_info.get("téléphone"),
                    "résumé": cv_summary,
                    "score": score,
                    "accepte": "oui" if score >= 70 else "non"
                },
                "job_offer": {
                    "mots_cles": job_keywords,
                    "niveau": niveau,
                    "description": f"Recherche un candidat avec des compétences en {', '.join(job_keywords[:5])}"
                },
                "test_technique": selected_test
            }

            # Sauvegarde dans la base de données
            saved = cv_collection.insert_one(response_data)
            response_data["_id"] = str(saved.inserted_id)

            return jsonify(response_data)

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/generate_test', methods=['POST'])
    def generate_test():
        try:
            competencies = request.json.get("competencies")
            difficulty = request.json.get("difficulty")

            if not competencies or not difficulty:
                return jsonify({"error": "Les champs 'competencies' et 'difficulty' sont requis."}), 400

            # Vérification que les compétences sont bien formatées
            if isinstance(competencies, list):
                competencies_str = ", ".join(competencies)
            else:
                competencies_str = competencies

            difficulty_str = difficulty.capitalize()

            tests = generate_tests(competencies_str, difficulty_str)

            if not tests:
                return jsonify({"error": "Aucun test généré."}), 500

            return jsonify({"tests": tests})

        except Exception as e:
            return jsonify({"error": str(e)}), 500
