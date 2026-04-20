import sys 
sys.path.append("..")# Agrega el directorio padre al sys.path para permitir la importación de módulos desde ese nivel
from flask import Flask
from flask_cors import CORS
from app_backend.routes.partidos_mundial import partidos_mundial_bp
from app_backend.routes.usuarios import usuarios_bp
from app_backend.routes.ranking import ranking_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(partidos_mundial_bp, url_prefix="/partidos-mundial")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")
app.register_blueprint(ranking_bp, url_prefix="/ranking")


if __name__ == "__main__":
    app.run(port=5000, debug=True)