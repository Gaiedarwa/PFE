from flask import Flask
from routes import init_routes
from json_encoder import CustomJSONEncoder

def create_app():
    app = Flask(__name__)
    app.json_encoder = CustomJSONEncoder
    init_routes(app)
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
