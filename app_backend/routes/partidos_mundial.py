from flask import Blueprint, jsonify, request
from app_backend.db import get_connection
import re
from datetime import datetime
partidos_mundial_bp = Blueprint("partidos_mundial", __name__)




def validar_body_partido(cuerpo):

    FASES_VALIDAS = ['GRUPOS', 'DIECISEISAVOS', 'OCTAVOS', 'CUARTOS', 'SEMIS', 'FINAL']

    if cuerpo is None:
        return "El body no cumple con el formato JSON", 400

    equipo_local = cuerpo.get("equipo_local")
    equipo_visitante = cuerpo.get("equipo_visitante")
    fecha = cuerpo.get("fecha")
    fase = cuerpo.get("fase")

    if equipo_local is None or equipo_visitante is None or fecha is None or fase is None:
        return "Faltan campos por asignar",400

    if not isinstance(equipo_local,str) or not isinstance(equipo_visitante,str) or not isinstance(fase,str):
        return "Los nombres de los equipos y la fase deben ser de tipo string",400

    try: 
        datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError:

        return "Formato de fecha inválido",400
    
    if fase not in FASES_VALIDAS:
        return "Fase inválida", 400
        
    return None, None



def validar_body_prediccion(cuerpo):

    if cuerpo is None:
        return "El body no cumple con el formato JSON", 400

    id_usuario = cuerpo.get("id_usuario")
    local = cuerpo.get("local")
    visitante = cuerpo.get("visitante")

    if id_usuario is None or local is None or visitante is None:
        return "Faltan campos por asignar",400

    if not isinstance(id_usuario,int) or not isinstance(local,int) or not isinstance(visitante,int):
        return "Los datos ingresados deben ser de tipo entero (id y goles)",400

    if local < 0 or visitante < 0:
        return "Los goles no pueden ser menores a cero", 400
        
    return None, None



# ----------------------------------------
# GET/ partidos
# ----------------------------------------
@partidos_mundial_bp.route("/", methods=["GET"])
def get_partidos():


    PARAMETROS_PERMITIDOS = ['equipo', 'fecha', 'fase', '_limit', '_offset']



    try:

        equipo = request.args.get("equipo")
        fecha = request.args.get("fecha")
        fase = request.args.get("fase")

        limit = request.args.get("_limit", 10) 
        offset = request.args.get("_offset", 0)

        conn= get_connection()
        cursor = conn.cursor (dictionary=True)


        for key in request.args.keys():
            if key not in PARAMETROS_PERMITIDOS:
                return jsonify({
                    "errors": [{
                        "code": "400",
                        "message": "Parámetro desconocido",
                        "level" : "error",
                        "description": f"El parámetro '{key}' no es válido para busqueda."
                    }]
                }), 400




        if fase:
            cursor.execute("SELECT COUNT(*) as count FROM partidos_mundial WHERE fase = %s", (fase,))
    
            if cursor.fetchone()['count'] == 0:
                return jsonify({
                    "errors": [{
                        "code": "404", 
                        "message": "Partido no encontrado", 
                        "level" : "error",
                        "description": f"No hay registros de partidos para la fase '{fase}'."
                    }]
                }), 404

        if equipo:
            cursor.execute("SELECT COUNT(*) as count FROM partidos_mundial WHERE equipo_local = %s OR equipo_visitante = %s", (equipo, equipo))
    
            if cursor.fetchone()['count'] == 0:
                return jsonify({
                        "errors": [{
                        "code": "404", 
                        "message": "Partido no encontrado",
                        "level" : "error", 
                        "description": f"El equipo '{equipo}' no existe en la base de datos."
                    }]
                }), 404
            

        if fecha:

            try:
         
                datetime.strptime(fecha, '%Y-%m-%d')

            except ValueError:

                return jsonify({
                    "errors": [{
                    "code": "400", 
                    "message": "Formato de fecha inválido", 
                    "level" : "error",
                    "description": "Usá el formato AAAA-MM-DD (ej: 2026-06-16)"
                    }]
                }), 400





            cursor.execute("SELECT COUNT(*) as count FROM partidos_mundial WHERE fecha = %s", (fecha,))
    
            if cursor.fetchone()['count'] == 0:
  
                return jsonify({
                        "errors": [{
                        "code": "404", 
                        "message": "Partido no encontrado",
                        "level" : "error", 
                        "description": f"No hay registros de partidos para la fecha '{fecha}'."
                    }]
                }), 404

        try:
            limit = int(limit)
            offset = int(offset)
        except ValueError:
            return jsonify({"errors":
                    [{"code": "400",
                      "message": "Parámetros inválidos",
                      "level": "error",
                      "description": "_limit y _offset deben ser números enteros"}]
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


        query = "SELECT id,equipo_local, equipo_visitante, fecha, fase FROM partidos_mundial" #query dinamica
        filtros =[]
        params = [] 

        if equipo:
            filtros.append("(equipo_local = %s OR equipo_visitante = %s)") #le hace faltan los %s --> por eso agregamos equipo, equipo
            params.extend([equipo, equipo]) #extend permite agregar varios elementos de una lista a otra
             
        if fecha:
            filtros.append("(fecha = %s)") 
            params.append(fecha)

        if fase:
            filtros.append("(fase = %s)") 
            params.append(fase)

        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        #query de consulta para ver cuantos registros tenemos

        query_count = "SELECT COUNT(*) as total FROM partidos_mundial" #as total hace que el diccionario que devuelve esta query que cuenta, sea {'total':48} 

        if filtros:
            query_count += " WHERE " + " AND ".join(filtros)

        cursor.execute(query_count, params)
        total_registros = cursor.fetchone()['total'] #'total' seria la clave asociada al valor de los registros


        #no hay condicional para limit y offset ya que tenemos valores por default, nunca sera NONE

        query += " LIMIT %s OFFSET %s "
        params_final = params + [limit, offset]

        cursor.execute(query,params_final)

        partidos = cursor.fetchall()



        if not partidos:
            
            return "", 204 

        if total_registros % limit == 0:
            ultimo_offset = (total_registros // limit - 1) * limit 

        else:

            ultimo_offset = (total_registros // limit) * limit 

        _links = {
            "_first": {"href": f"/partidos-mundial/?_limit={limit}&_offset=0"},
            "_last":  {"href": f"/partidos-mundial/?_limit={limit}&_offset={ultimo_offset}"}
        }

        if offset > 0:
            offset_previo = offset - limit
            if offset_previo < 0:
                offset_previo = 0
            _links["_prev"] = {"href": f"/partidos-mundial/?_limit={limit}&_offset={offset_previo}"}

        if (offset + limit) < total_registros:
            _links["_next"] = {"href": f"/partidos-mundial/?_limit={limit}&_offset={offset + limit}"}
        return jsonify({
            "partidos": partidos,
            "_links": _links
        }), 200
        
    
    except Exception as error_interno:
        return jsonify({"errors": [{"code": "500", "message": "Error interno del servidor", "level": "error", "description": str(error_interno)}]}), 500



    finally:

        if 'cursor' in locals() and cursor:
            cursor.close()

        if 'conn' in locals() and conn:
            conn.close()






@partidos_mundial_bp.route("/", methods = ["POST"])
def crear_usuario():
    try:
        datos = request.json

        error, codigo = validar_body_partido(datos)
        if error:
            return jsonify({
                "errors": [{
                    "code": str(codigo),
                    "message": "Datos inválidos",
                    "level": "error",
                    "description": error
                }]
            }), codigo

        equipo_local= datos["equipo_local"].strip()
        equipo_visitante = datos["equipo_visitante"].strip()
        fecha = datos["fecha"].strip()
        fase = datos["fase"].strip()

        conn = get_connection()
        cursor = conn.cursor()

        #chequeo mail duplicado
        cursor.execute("SELECT id FROM partidos_mundial WHERE equipo_local = %s AND equipo_visitante = %s AND fecha = %s AND fase = %s", (equipo_local, equipo_visitante, fecha, fase))
        if cursor.fetchone():
            return jsonify({
                "errors": [{
                "code": 409,
                "message": "Conflicto",
                "level": "error",
                "description": f"El partido a crear ya existe"}]
            }),409

        cursor.execute("INSERT INTO partidos_mundial (equipo_local, equipo_visitante, fecha, fase) VALUES (%s,%s,%s,%s)", (equipo_local,equipo_visitante, fecha, fase))
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
# GET/partidos/id  este con resltados
# ----------------------------------------
@partidos_mundial_bp.route("/<int:id>",methods= ['GET'])
def buscar_partido_id(id):
    
    try:
        #establecer conexion con la db
        conn= get_connection()
        cursor= conn.cursor(dictionary=True)
    
        #busca el partido con ese id y guarda el resultado
        cursor.execute("SELECT * FROM partidos_mundial WHERE id = %s",(id,))
        registro= cursor.fetchone()
    
        #si no existe el id devuelve error
        if registro is None:
            return jsonify ({"errors":[{"code" : "404", "Message":"Try other ID", "level": "Error","Description":"ID Not Found" }]}),404

        partido_respuesta = {
            "id": registro["id"],
            "equipo_local": registro["equipo_local"],
            "equipo_visitante": registro["equipo_visitante"],
            "fecha": registro["fecha"],
            "fase": registro["fase"]
        }

        if registro["goles_local"] is not None and registro["goles_visitante"] is not None:
            partido_respuesta["resultado"] = {
                "local": registro["goles_local"],
                "visitante": registro["goles_visitante"]
            }



    #ESTO DEVUELVE EN FORMA DICCIONARIO CON RESULTADOS DEPENDIENDO DE SI ES O NO NULL
        return jsonify(partido_respuesta),200
  
  
    #a cualquier error no esperado le suelta este mensaje   
    #str(e) devuelve en formato json el mensaje de error propio de la pagina 
    except Exception as e:
        return jsonify({"errors": [{"code": "500", "message": "Internal Server Error", "level": "error", "description": str(e)}]}), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()







# ----------------------------------------
# PUT/partidos/id
# ----------------------------------------

@partidos_mundial_bp.route('/<int:id>', methods=['PUT'])
def update_full(id):
   
    try:
        data = request.json
        conn = get_connection()
        cursor = conn.cursor()
        
        sql = """UPDATE partidos_mundial 
                 SET fecha = %s, equipo_local = %s, equipo_visitante = %s, fase = %s 
                 WHERE ID = %s"""
        values = (data['fecha'], data['equipo_local'], data['equipo_visitante'], data['fase'], id)
        
        cursor.execute(sql, values)
        conn.commit()

        if cursor.rowcount == 0:

            return jsonify({
            "errors": [{ 
                "code": "400",
                "level": "error",
                "message": "Partido no encontrado",
                "description": f"El ID {id} no existe en la base de datos."
            }]
            }), 400
        

        return '', 204
    except:

        return jsonify({
            "errors": [{ 
                "code": "500",
                "level": "error",
                "message": "Error en el servidor",
                "description": "Ha ocurrido un error interno en el servidor, corrobore haber ingresado los datos correctamente."
            }]
            }), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()



# ----------------------------------------
# PATCH/partidos/ id
# ----------------------------------------
@partidos_mundial_bp.route('/<int:id>', methods=['PATCH'])
def update_partial(id):


    try:
        data = request.json
        

        if data is None:
            return jsonify({"errors": [{"code": "400", "message": "El body no cumple con el formato JSON"}]}), 400

  
        valid_types = {
            "fecha": str,
            "equipo_local": str,
            "equipo_visitante": str,
            "fase": str
        }

        for field, value in data.items():

            if field not in valid_types:
                return jsonify({"errors": [{"code": "400", "level": "error", "description": f"El campo {field} no es válido", "message": "Campo invalido"}]}), 400

            if not isinstance(value, valid_types[field]):
                return jsonify({"errors": [{"code": "400", "level": "error", "description": f"El campo '{field}' debe ser de tipo {valid_types[field].__name__}", "message": "Tipo de dato invalido"}]}), 400

            if field == "fecha" and not re.match(r"^\d{4}-\d{2}-\d{2}$", value):
                return jsonify({"errors": [{"code": "400", "level": "error", "description": "Formato de fecha inválido. Use YYYY-MM-DD", "message" : "Fecha invalida"}]}), 400



        conn = get_connection()
        cursor = conn.cursor()


        fields = []
        values = []
        for key, value in data.items():
            fields.append(f"{key} = %s")
            values.append(value)
        
        values.append(id)
        sql = f"UPDATE partidos_mundial SET {', '.join(fields)} WHERE ID = %s"
        
        cursor.execute(sql, values)
        conn.commit()

        if cursor.rowcount == 0:

            return jsonify({
            "errors": [{ 
                "code": "404",
                "level": "error",
                "message": "Partido no encontrado",
                "description": f"El ID {id} no existe en la base de datos."
            }]
            }), 404

        return '', 204
    except:
        return jsonify({"errors": [{ 
                "code": "500",
                "level": "error",
                "message": "Error en el servidor",
                "description": "Ha ocurrido un error interno en el servidor, corrobore haber ingresado los datos correctamente."
            }]
            }), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()





# ----------------------------------------
# DELETE/ partidos/id
# ----------------------------------------

@partidos_mundial_bp.route("/<int:id>",methods= ['DELETE'])
def eliminar_partido_id(id):
    
    try:
        #establecer coneccion con la db
        conn= get_connection()
        cursor= conn.cursor(dictionary=True)
    
        #busca el partido con ese id y guarda el resultado
        cursor.execute("DELETE FROM partidos_mundial WHERE id = %s",(id,))

        conn.commit()

        resultado= cursor.rowcount
    
        #si no existe el id devuelve error
        if resultado == 0:
            return jsonify ({"errors":[{"code" : "404", "Message":"Try other ID", "level": "Error","Description":"ID Not Found" }]}),404



    #esto devuelve en manera de diccionario segun esta escrito en la base de datos
        return jsonify(resultado),204  
  
  
    #a cualquier error no esperado le suelta este mensaje   
    #str(e) devuelve en formato json el mensaje de error propio de la pagina 
    except Exception as e:
        return jsonify({"errors": [{"code": "500", "message": "Internal Server Error", "level": "error", "description": str(e)}]}), 500

    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()



# ----------------------------------------
# PUT/ partidos/id/resultado  carga o actualiza res
# ----------------------------------------


@partidos_mundial_bp.route("/<int:id>/resultados", methods = ['PUT'])
def actualizar_resultado(id):

    try:
        data = request.json

        if data is None:
            return jsonify({"errors": [{"code": "400",
                            "message": "El body no cumple con el formato JSON",
                            "level": "error",
                            "description": "El body debe ser un objeto JSON valido"}]
                            }), 400

        local = data.get("local")
        visitante = data.get("visitante")

        #validaciones bad request

        if local is None or visitante is None:
            return jsonify({"errors": [{"code": "400",
                                "message": "Campos requeridos",
                                "level": "error",
                                "description": "Campos 'local' y 'visitante' son requeridos"}]
                    }), 400

        if not isinstance(local, int) or not isinstance(visitante, int):
            return jsonify({"errors": [{"code": "400",
                                "message": "Tipo de dato invalido",
                                "level": "error",
                                "description": "Los campos 'local' y 'visitante' deben ser enteros"}]
                    }), 400

        if local < 0 or visitante < 0:
            return jsonify({"errors": [{"code": "400",
                                "message": "Valor invalido",
                                "level": "error",
                                "description": "Los campos 'local' y 'visitante' deben ser positivos"}]
                    }), 400

        conn = get_connection()
        cursor = conn.cursor()

        #chequeo existencia partido
        cursor.execute("SELECT id FROM partidos_mundial WHERE id = %s",(id,))
        if cursor.fetchone() is None:
            return jsonify({"errors": [{"code": "404",
                                "message": "Partido no encontrado",
                                "level": "error",
                                "description": f"No existe un partido con ID: {id}"}]
                    }), 404

        #actualiza resultado
        cursor.execute("UPDATE partidos_mundial SET goles_local = %s, goles_visitante = %s WHERE id = %s",
        (local,visitante, id))
        conn.commit()

        return '',204

    except Exception as e:
        return jsonify({"errors": [{"code": "500",
                                    "message": "Error interno del servidor",
                                    "level": "error",
                                    "description": str(e)}]
                        }), 500


    finally:

        if 'cursor' in locals() and cursor:
            cursor.close()

        if 'conn' in locals() and conn:
            conn.close()




@partidos_mundial_bp.route("/<int:id>/prediccion", methods = ["POST"])

def crear_prediccion(id):
    try:
        datos = request.json

        error, codigo = validar_body_prediccion(datos)
        if error:
            return jsonify({
                "errors": [{
                    "code": str(codigo),
                    "message": "Datos inválidos",
                    "level": "error",
                    "description": error
                }]
            }), codigo

        id_usuario = datos["id_usuario"]
        local = datos["local"]
        visitante = datos["visitante"]

        conn = get_connection()
        cursor = conn.cursor(dictionary = True)


        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id_usuario,))
        if cursor.fetchone() is None:
            return jsonify({
                "errors": [{
                "code": 404,
                "message": "Usuario desconocido",
                "level": "error",
                "description": f"No existe un usuario con el id {id_usuario}"}]
            }),404

        cursor.execute("SELECT * FROM partidos_mundial WHERE id = %s", (id,))
        partido_prediccion = cursor.fetchone()

        print(partido_prediccion)

        if partido_prediccion is None:
            return jsonify({
                "errors": [{
                "code": 404,
                "message": "Partido desconocido",
                "level": "error",
                "description": f"No existe un partido con el id {id}"}]
            }),404

        if partido_prediccion["goles_local"] != None or partido_prediccion["goles_visitante"] != None:
            return jsonify({
                "errors": [{
                "code": 400,
                "message": "Partido ya jugado",
                "level": "error",
                "description": f"El partido con el id {id} ya se jugo"}]
            }),400
        

        cursor.execute("SELECT * FROM predicciones WHERE id_usuario = %s AND id_partido = %s" , (id_usuario, id))

        if cursor.fetchone():
            return jsonify({
                "errors": [{
                "code": 400,
                "message": "Prediccion ya registrada",
                "level": "error",
                "description": f"Ya predijiste ese partido"}]
            }),400
        



        cursor.execute("INSERT INTO predicciones (id_partido, id_usuario, goles_local, goles_visitante) VALUES (%s,%s,%s,%s)", (id,id_usuario, local, visitante))    
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

