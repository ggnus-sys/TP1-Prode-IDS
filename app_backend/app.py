import sys 
sys.path.append("..")  
from flask import Flask
from flask_cors import CORS
from app_backend.routes.partidos_mundial import partidos_mundial_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(partidos_mundial_bp, url_prefix="/partidos-mundial")


if __name__ == "__main__":
    app.run(port=5000, debug=True)