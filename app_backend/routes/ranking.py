from flask import Blueprint, jsonify, request
from app_backend.db import get_connection


ranking_bp = Blueprint("ranking", __name__)



@ranking_bp.route("/", methods = ["GET"])
def get_ranking():

    PARAMETROS_PERMITIDOS = ["_limit", "_offset"]

    try:
        for key in request.args.keys():
            if key not in PARAMETROS_PERMITIDOS:
                return jsonify({
                    "errors": [{
                        "code": "400",
                        "message": "Parametro desconocido",
                        "level": "error",
                        "description": f"El parametro '{key}' no es valido"
                    }]
                }), 400


        limit = request.args.get("_limit", 10)
        offset = request.args.get("_offset", 0)

        try:
            limit = int(limit)
            offset = int(offset)

        except ValueError:
            return jsonify({
                "errors": [{
                "code": "400",
                "message": "Parametro desconocido",
                "level": "error",
                "description": "_limit y _offset deben ser enteros"
                }]
            }), 400

        if limit < 1:
            return jsonify({
                "errors": [{
                    "code": "400",
                    "message": "valor invalido",
                    "level": "error",
                    "description": "_limit debe ser mayor a 0"}]
            }), 400

        if offset < 0:
            return jsonify({
                "errors":[{
                    "code": "400",
                    "message": "valor invalido",
                    "level": "error",
                    "description": "_offset debe ser mayor a 0"}]
            }), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary = True)

        cursor.execute("SELECT partidos_mundial.goles_local, partidos_mundial.goles_visitante, goles_visitante_prediccion, goles_local_prediccion, id_usuario FROM predicciones INNER JOIN partidos_mundial on predicciones.id_partido = partidos_mundial.id")
        tabla_comparacion_resultados = cursor.fetchall()
        
        for fila in tabla_comparacion_resultados:
            if (fila["goles_visitante_prediccion"] == fila["goles_visitante"] and fila["goles_local_prediccion"] == fila["goles_local"]):
                cursor.execute("UPDATE usuarios SET puntos = puntos + 3 WHERE id = %s and puntos = 0", (fila["id_usuario"],))
                conn.commit()


            elif (fila["goles_visitante_prediccion"] >= fila["goles_local_prediccion"] and fila["goles_visitante"] >= fila["goles_local"]) or (fila["goles_visitante_prediccion"] <= fila["goles_local_prediccion"] and fila["goles_visitante"] <= fila["goles_local"]):
                cursor.execute("UPDATE usuarios SET puntos = puntos + 1 WHERE id = %s and puntos = 0", (fila["id_usuario"],))
                conn.commit()


        #que el listado devuelva id y nombre
        cursor.execute("SELECT id,nombre, puntos FROM usuarios ORDER BY puntos ASC LIMIT %s OFFSET %s", (limit, offset))
        usuarios = cursor.fetchall()

        if not usuarios:
            return "", 204


        # hateoas y links

        base = "/usuarios/"
        total_registros = cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total_registros = cursor.fetchone()["total"]
        ultimo_offset = max(0, ((total_registros - 1) // limit)* limit)

        _links = {
            "_first": {"href" : f"{base}?_limit={limit}&_offset=0"},
            "_last" : {"href" : f"{base}?_limit={limit}&_offset={ultimo_offset}"}
        }

        if offset > 0:
            offset_anterior = max(0, offset - limit)
            _links["_prev"] = {"href" : f"{base}?_limit={limit}&_offset={offset_anterior}"}

        if offset + limit < total_registros:
            _links["_next"] = {"href" : f"{base}?_limit={limit}&_offset={offset + limit}"}

        return jsonify({
            "usuarios": usuarios,
            "_links": _links
        }), 200

    except Exception as e:
        return jsonify({
            "errors": [{
                "code": "500",
                "message": "Error interno del servidor",
                "level": "error",
                "description": str(e)
            }]
        }), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
