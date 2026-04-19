from flask import Blueprint, jsonify, request
from app_backend.db import get_connection
import re

usuarios_bp = Blueprint("usuarios", __name__)

# Esto busca el formato: texto + @ + texto + . + texto
EMAIL_REGEX = re.compile(r'^[^@]+@[^@]+\.[^@]+$')

"""
    La funcion verifica que el usuario esté bien ingresado
    :param cuerpo: 
    :return: (None, None) ó (error, codigo) 
"""
def validar_body_de_usuario(cuerpo):

    if cuerpo is None:
        return "El body no cumple con el formato JSON", 400

    nombre = cuerpo.get("nombre")
    email = cuerpo.get("email")
   
    # validaciones
    if nombre is None or email is None:
        return "Los campos son obligatorios",400

    if not isinstance(nombre,str) or not isinstance(email,str):
        return "Los campos deben ser de tipo string",400

    if not nombre.strip():
        return "El nombre no puede estar vacío",400

    if not EMAIL_REGEX.match(email):
        return "El email no es valido",400

    return None, None


# ----------------------------------------
# GET/usuarios
# ----------------------------------------

@usuarios_bp.route("/", methods = ["GET"])
def buscar_usuarios():

    PARAMETROS_PERMITIDOS = ["_limit", "_offset"]

    #mas validaciones
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
                    "description": "_limit debe ser mayor a 0"}]
            }), 400

        conn = get_connection()
        cursor = conn.cursor(dictionary = True)

        cursor.execute("SELECT COUNT(*) as total FROM usuarios")
        total_registros = cursor.fetchone()["total"]

        #que el listado devuelva id y nombre
        cursor.execute("SELECT id, nombre FROM usuarios LIMIT %s OFFSET %s", (limit, offset))
        usuarios = cursor.fetchall()

        if not usuarios:
            return "", 204


        # hateoas y links

        base = "/usuarios/"

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

# ----------------------------------------
# POST/usuarios
# ----------------------------------------

@usuarios_bp.route("/", methods = ["POST"])
def crear_usuario():
    try:
        datos = (request.json)["body"][0] #Odio esta linea de codigo con numero magico, deberemos cambiarlo despues pero por ahora funciona, sino el body no se interpreta bien

        #uso de la función para validar el body !!! + manejo de error (si no queda None, None)
        error, codigo = validar_body_de_usuario(datos)
        if error:
            return jsonify({
                "errors": [{
                    "code": str(codigo),
                    "message": "Datos inválidos",
                    "level": "error",
                    "description": error
                }]
            }), codigo

        nombre = datos["nombre"].strip()
        email = datos["email"].strip()

        conn = get_connection()
        cursor = conn.cursor()

        #chequeo mail duplicado
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({
                "errors": [{
                "code": 409,
                "message": "Conflicto",
                "level": "error",
                "description": f"Ya existe un usuario con ese mail {email}"}]
            }),409

        cursor.execute("INSERT INTO usuarios (nombre, email) VALUES (%s,%s)", (nombre,email))
        conn.commit()

        return "",201

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

# ----------------------------------------
# GET/usuarios/id
# ----------------------------------------

@usuarios_bp.route("/<int:id>", methods = ["GET"])
def buscar_usuario_id(id):

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        #busca el usuario con ese id y guarda el resultado, devuelve id, nombre y mail
        cursor.execute("SELECT id, nombre, email FROM usuarios WHERE id = %s", (id,))

        usuario = cursor.fetchone()

        #error si no existe ID

        if usuario is None:
            return jsonify({
                "errors": [{
                    "code": "404",
                    "message": "Usuario no encontrado",
                    "level": "error",
                    "description": f"No existe un usuario con ID: {id}"}]
            }), 404

        return jsonify(usuario), 200

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


# ----------------------------------------
# PUT/usuarios/id
# ----------------------------------------

@usuarios_bp.route("/<int:id>", methods=['PUT'])
def actualizar_usuario(id):
    try:
        datos = request.json

        # uso de la función para validar el body !!! + manejo de error (si no queda None, None)
        error, codigo = validar_body_de_usuario(datos)
        if error:
            return jsonify({
                "errors": [{
                    "code": str(codigo),
                    "message": "Datos inválidos",
                    "level": "error",
                    "description": error
                }]
            }), codigo

        nombre = datos["nombre"].strip()
        email = datos["email"].strip()

        conn = get_connection()
        cursor = conn.cursor()

        #chequeo de existencia usuario
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
        if cursor.fetchone() is None:
            return jsonify({
                "errors": [{
                    "code": "404",
                    "message": "Usuario no encotnrado",
                    "level": "error",
                    "description": f"No existe un usuario con id {id}"}]
            }), 404

        #chequeo mail duplicado
        cursor.execute("SELECT id FROM usuarios WHERE email = %s AND id != %s", (email, id))
        if cursor.fetchone():
            return jsonify({
                "errors": [{
                    "code": 409,
                    "message": "Conflicto",
                    "level": "error",
                    "description": f"Ya existe un usuario con ese mail {email}"}]
            }), 409

        #actualizacion
        cursor.execute("UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s", (nombre, email, id))
        conn.commit()

        return "", 204

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


# ----------------------------------------
# DELETE/usuarios/id
# ----------------------------------------

@usuarios_bp.route("/<int:id>", methods = ["DELETE"])
def eliminar_usuario(id):

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""DELETE FROM usuarios WHERE id = %s""", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            #osea que no hay usuarios con ese ID
            return jsonify({
                "error": [{
                    "code": "404",
                    "message": "Usuario no encontrado",
                    "level": "error",
                    "description": f"No existe un usuario con ID: {id}"
                }]
            }), 404

        return "", 204

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