from bson import ObjectId
from flask import request, jsonify
from services import process_document, clean_text, remove_sensitive_data, summarize_skills, detect_experience_level, get_embedding
from models import extract_entities, validate_personal_info, calculate_similarity
from summarization import summarize_concisely, extract_keywords
from technical_test import generate_tests, select_random_test, get_user_input
from database import cv_collection, offers_collection
import redis
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import logging
import random

# Configure logging (optional, but helpful)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration Redis pour le cache
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

# Vérification de la taille du fichier
def file_too_large(file, max_size_mb=5):
    file.seek(0, 2)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    return size_mb > max_size_mb

# Initialisation des routes Flask
def init_routes(app):
    @app.route('/job-offers', methods=['POST'])
    def create_job_offer():
        try:
            file = request.files.get("offer")
            text = request.form.get("text")
            
            if not file and not text:
                return jsonify({"error": "Veuillez fournir un fichier ou un texte"}), 400

            # Traitement du document
            offer_text = process_document(file) if file else clean_text(text)
            
            # Extraction des métadonnées
            keywords = extract_keywords(offer_text)
            description = summarize_concisely(offer_text)
            
            # Détermination du niveau (senior/junior)
            senior_keywords = ["senior", "expérience", "chef", "lead"]
            junior_keywords = ["junior", "débutant", "stagiaire"]
            
            if any(keyword.lower() in offer_text.lower() for keyword in senior_keywords):
                niveau = "Senior"
            elif any(keyword.lower() in offer_text.lower() for keyword in junior_keywords):
                niveau = "Junior"
            else:
                niveau = "Non spécifié"
            
            # Sauvegarde dans la base
            offer_data = {
                "text": offer_text,
                "keywords": keywords,
                "description": description,
                "niveau": niveau,
                "created_at": datetime.utcnow()
            }
            
            try:
                saved = offers_collection.insert_one(offer_data)
                return jsonify({
                    "_id": str(saved.inserted_id),
                    "description": description,
                    "keywords": keywords,
                    "niveau": niveau
                }), 201
            except DuplicateKeyError:
                return jsonify({"error": "Offre déjà existante"}), 400

        except Exception as e:
            logging.error(f"Error in create_job_offer: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/job-offers', methods=['GET'])
    def get_all_offers():
        try:
            offers = list(offers_collection.find())
            for offer in offers:
                offer["_id"] = str(offer["_id"])
            return jsonify(offers)
        except Exception as e:
            logging.error(f"Error in get_all_offers: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/job-offers/<offer_id>', methods=['GET'])
    def get_offer_by_id(offer_id):
        try:
            offer = offers_collection.find_one({"_id": ObjectId(offer_id)})
            if not offer:
                return jsonify({"error": "Offre non trouvée"}), 404
            offer["_id"] = str(offer["_id"])
            return jsonify(offer)
        except Exception as e:
            logging.error(f"Error in get_offer_by_id: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/apply', methods=['POST'])
    def apply_to_offer():
        try:
            file_cv = request.files.get("cv")
            text_cv = request.form.get("text_cv")
            offer_id = request.form.get("offer_id")

            if not (file_cv or text_cv) or not offer_id:
                return jsonify({"error": "Veuillez fournir un CV et un ID d'offre"}), 400

            # Traitement du CV
            cv_text = process_document(file_cv) if file_cv else clean_text(text_cv)

            # Récupérer l'offre depuis la base
            offer = offers_collection.find_one({"_id": ObjectId(offer_id)})
            if not offer:
                return jsonify({"error": "Offre non trouvée"}), 404

            # Supprimer les données sensibles
            clean_cv = remove_sensitive_data(cv_text)
            clean_offer = remove_sensitive_data(offer["text"])

            # Extraire les compétences + expérience
            skills_cv = summarize_skills(clean_cv)
            skills_offer = summarize_skills(clean_offer)
            exp_cv = detect_experience_level(clean_cv)
            exp_offer = detect_experience_level(clean_offer)

            # Fusionner pour l'embedding
            cv_input = f"{skills_cv} {exp_cv}"
            offer_input = f"{skills_offer} {exp_offer}"

            # Vérifier le cache sur le texte traité
            cache_key = f"similarity:{offer_id}:{cv_input[:100]}"
            cached_score = redis_client.get(cache_key)

            if cached_score:
                score = float(cached_score)
            else:
                emb_cv = get_embedding(cv_input)
                emb_offer = get_embedding(offer_input)
                score = calculate_similarity(emb_cv, emb_offer)
                redis_client.setex(cache_key, 300, score)  # Cache pour 5 min

            # Logique de sélection
            if score >= 70:
                tests = generate_tests(offer["keywords"][:5], offer["niveau"])
                # Sauvegarde de la postulation
                postulation_data = {
                    "cv_text": cv_text,
                    "offer_id": offer_id,
                    "score": score,
                    "tests": random.sample(tests, min(10, len(tests))),
                    "created_at": datetime.utcnow()
                }
                saved = cv_collection.insert_one(postulation_data)
                postulation_data["_id"] = str(saved.inserted_id)
                return jsonify({
                    "status": "success",
                    "score": score,
                    "tests": postulation_data["tests"]
                })
            else:
                return jsonify({
                    "status": "rejected",
                    "score": score,
                    "message": "Score insuffisant"
                })

        except Exception as e:
            logging.error(f"Error in apply_to_offer: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/postulations', methods=['GET'])
    def get_all_postulations():
        try:
            postulations = list(cv_collection.find())
            for postulation in postulations:
                postulation["_id"] = str(postulation["_id"])
            return jsonify(postulations)
        except Exception as e:
            logging.error(f"Error in get_all_postulations: {str(e)}")
            return jsonify({"error": str(e)}), 500

    @app.route('/postulations/<postulation_id>', methods=['GET'])
    def get_postulation_by_id(postulation_id):
        try:
            postulation = cv_collection.find_one({"_id": ObjectId(postulation_id)})
            if not postulation:
                return jsonify({"error": "Postulation non trouvée"}), 404
            postulation["_id"] = str(postulation["_id"])
            return jsonify(postulation)
        except Exception as e:
            logging.error(f"Error in get_postulation_by_id: {str(e)}")
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
            logging.error(f"Error in generate_test: {str(e)}")
            return jsonify({"error": str(e)}), 500
