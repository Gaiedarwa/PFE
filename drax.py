# drax.py
from flask import Flask
from flask_cors import CORS
import os
from database import connect_mongo
from routes import init_routes

# Création de l'application Flask
def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration du dossier d'upload
    UPLOAD_FOLDER = "uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Connexion à MongoDB
    app.db = connect_mongo()

    # Initialisation des routes
    init_routes(app)

    return app

# Lancement de l'application Flask
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
