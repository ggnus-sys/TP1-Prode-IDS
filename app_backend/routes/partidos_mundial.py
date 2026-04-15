from flask import Blueprint, jsonify, request
from app_backend.db import get_connection
import re

partidos_mundial_bp = Blueprint("partidos_mundial", __name__)

FASES_VALIDAS = ["GRUPOS", "DIECISEISAVOS", "OCTAVOS", "CUARTOS", "SEMIS", "FINAL"]
EQUIPOS_VALIDOS = ["México","Sudáfrica","Corea del Sur","República Checa","Canadá","Bosnia y Herzegovina","Estados Unidos",
                   "Paraguay","Catar","Suiza","Brasil","Marruecos","Haití","Escocia","Australia",
                   "Turquía","Alemania","Curazao","Países Bajos","Japón","Costa de Marfil","Ecuador","Suecia","Túnez","España","Islas de Cabo Verde","Bélgica",
                   "Egipto","Arabia Saudí","Uruguay","República Islámica de Irán","Nueva Zelanda","Francia","Senegal","Irak","Noruega","Argentina","Argelia",
                   "Austria","Jordania","Portugal","República Democrática del Congo","Inglaterra","Croacia","Ghana","Panamá","Uzbekistán","Colombia"]

@partidos_mundial_bp.route("/")
def get_partidos():
    
    try:

        equipo = request.args.get("equipo")
        fecha = request.args.get("fecha")
        fase = request.args.get("fase")

        limit = request.args.get("_limit", 10) 
        offset = request.args.get("_offset", 0)


        if fase and (fase not in FASES_VALIDAS): #si existe fase Y si fase no esta en fases validas:
            return jsonify({
            "errors": [{
            "code": "404", 
            "message": "Fase no encontrada", 
            "level": "error", 
            "description": f"La fase '{fase}' no existe en el torneo."
        }]}), 404

        if equipo and (equipo not in EQUIPOS_VALIDOS):
            return jsonify({
            "errors": [{
            "code": "404", 
            "message": "Equipo no encontrado", 
            "level": "error", 
            "description": f"El equipo '{equipo}' no participa del torneo o no existe."
        }]}), 404

        try:
                limit = int(limit)
                offset = int(offset)
        except ValueError:
            return jsonify({"errors": [{"code": "400", "message": "Parámetros inválidos", "level": "error", "description": "_limit y _offset deben ser números enteros"}]}), 400

        conn= get_connection()
        cursor = conn.cursor (dictionary=True)

        query = "SELECT * FROM Partidos_Mundial" #query dinamica
        filtros =[]
        params = [] 

        if equipo:
            filtros.append("(Equipo_Local = %s OR Equipo_Visitante = %s)") #le hace faltan los %s --> por eso agregamos equipo, equipo
            params.extend([equipo, equipo]) #extend permite agregar varios elementos de una lista a otra
             
        if fecha:
            filtros.append("(Fecha = %s)") 
            params.append(fecha)

        if fase:
            filtros.append("(Fase = %s)") 
            params.append(fase)

        if filtros:
            query += " WHERE " + " AND ".join(filtros)

        #query de consulta para ver cuantos registros tenemos

        query_count = "SELECT COUNT(*) as total FROM Partidos_Mundial" #as total hace que el diccionario que devuelve esta query que cuenta, sea {'total':48} 

        if filtros:
            query_count += " WHERE " + " AND ".join(filtros)

        cursor.execute(query_count, params) 
        resultado_count = cursor.fetchone()
        total_registros = resultado_count['total'] #'total' seria la clave asociada al valor de los registros


        #no hay condicional para limit y offset ya que tenemos valores por default, nunca sera NONE

        query += " LIMIT %s OFFSET %s "
        params_final = params + [limit, offset]

        cursor.execute(query,params_final)

        partidos = cursor.fetchall()

        cursor.close()
        conn.close()

        if not partidos:
            return "", 204 

        qs = ""
        if equipo: qs += f"&equipo={equipo}"
        if fecha:  qs += f"&fecha={fecha}"
        if fase:   qs += f"&fase={fase}"

        _links = {
            "self": f"/partidos-mundial/?_limit={limit}&_offset={offset}{qs}"
        }

        # link a la siguiente pagina
        if (offset + limit) < total_registros:
            _links["next"] = f"/partidos-mundial/?_limit={limit}&_offset={offset + limit}{qs}"

        # link a la pagina anterior
        
        if offset > 0:
            offset_previo = (offset - limit)
            if offset_previo < 0:
                offset_previo = 0
        
            _links["prev"] = f"/partidos-mundial/?_limit={limit}&_offset={offset_previo}{qs}" # dentro del if asi evitamos que aparezca prev en la primera pagina

        return jsonify({
            "partidos": partidos,
            "_links": _links
        }), 200
        
    
    except Exception as error_interno:
        return jsonify({"errors": [{"code": "500", "message": "Error interno del servidor", "level": "error", "description": str(error_interno)}]}), 500



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

            cursor.close()
            conn.close()
            return jsonify({
            "errors": [{ 
                "code": "400",
                "level": "error",
                "message": "Partido no encontrado",
                "description": f"El ID {id} no existe en la base de datos."
            }]
            }), 400
        
        cursor.close()
        conn.close()
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

            cursor.close()
            conn.close()
            return jsonify({
            "errors": [{ 
                "code": "404",
                "level": "error",
                "message": "Partido no encontrado",
                "description": f"El ID {id} no existe en la base de datos."
            }]
            }), 404
        
        cursor.close()
        conn.close()
        return '', 204
    except:
        return jsonify({"errors": [{ 
                "code": "500",
                "level": "error",
                "message": "Error en el servidor",
                "description": "Ha ocurrido un error interno en el servidor, corrobore haber ingresado los datos correctamente."
            }]
            }), 500