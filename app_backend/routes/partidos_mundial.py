from flask import Blueprint, jsonify, request
from app_backend.db import get_connection

partidos_mundial_bp = Blueprint("Partidos_Mundial", __name__)

@partidos_mundial_bp.route("/")
def get_partidos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Partidos_Mundial")
    partidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(partidos)