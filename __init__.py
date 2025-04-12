from flask import Flask
from flask_cors import CORS
import os
from database import connect_mongo
from routes import init_routes

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration de l'upload
    UPLOAD_FOLDER = "uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Connexion à MongoDB
    app.db = connect_mongo()

    # Initialisation des routes
    init_routes(app)

    return app
