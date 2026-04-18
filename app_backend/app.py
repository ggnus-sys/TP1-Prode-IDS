import sys 
sys.path.append("..")  
from flask import Flask
from flask_cors import CORS
from app_backend.routes.partidos_mundial import partidos_mundial_bp
from app_backend.routes.usuarios import usuarios_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(partidos_mundial_bp, url_prefix="/partidos-mundial")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")

if __name__ == "__main__":
    app.run(port=5000, debug=True)