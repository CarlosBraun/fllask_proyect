from controladores.controlador_requests import *

controlador_multipropietarios_bp = Blueprint(
    'controlador_multipropietarios', __name__)


def handle_99(value, propiedad):
    result = []
    for adquirente in value['adquirentes']:
        row = {
            'comuna': propiedad["comuna"],
            'manzana': propiedad["manzana"],
            'predio': propiedad["predio"],
            'run': adquirente['RUNRUT'],
            'derecho': adquirente['derecho'],
            'fojas': value['fojas'],
            'fecha_inscripcion': value['fecha_inscripcion'],
            'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
            'numero_inscripcion': value['numero_inscripcion'],
            'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
        }
        result.append(row)
    return result


def actualizar_ano_vigencia_f(elementos, ano_actual):
    for lista in elementos:
        for elemento in lista:
            if elemento.get("ano_vigencia_f") is None:
                elemento["ano_vigencia_f"] = ano_actual
    return elementos


def algoritmo(datos):
    datos_multipopietarios = request_multipropietario_data(datos)
    data = request_algorithm_data(datos)
    for lista in data:
        contador = 0
        for defaultdict_item in lista:
            propiedad = datos[contador]
            limpiar_multipropietario(propiedad)
            multipropietario = datos_multipopietarios[contador]
            # Código usado para debuggear a base de prints
            print("---------------------------------------------------------------------------------------------------")
            print(f"Datos de la propiedad: C: {propiedad['comuna']}, M: {
                  propiedad['manzana']}, P: {propiedad['predio']}")
            print("---------------------------------------------------------------------------------------------------")
            print("Multipropietarios Previa")
            print(multipropietario)
            print("---------------------------------------------------------------------------------------------------")
            # Fin del código de debuggeo
            if multipropietario is not None:
                multipropietario_temp = multipropietario
            else:
                multipropietario_temp = []

            for key, value in defaultdict_item.items():
                print("Temp inicial")
                print(multipropietario_temp)
                if int(value['fecha_inscripcion'][0:4]) <= 2019:
                    ano = 2019
                else:
                    ano = int(value['fecha_inscripcion'][0:4])
                print(ano)
                if value['cne'] == 99:
                    actualizar_ano_vigencia_f(multipropietario_temp, ano)
                    multipropietario_temp.append(handle_99(value, propiedad))
                    # Imprimir el resultado para verificación
                elif value['cne'] == 8:
                    print("cne 8")

                # ingresar a la multi
            print("Temp definitivo")
            print(multipropietario_temp)
            ingresar_multipropietarios(multipropietario_temp)

            contador += 1

    return data


@controlador_multipropietarios_bp.route('/', methods=['GET'])
def obtener_datos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Multipropietario')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(rows)


@controlador_multipropietarios_bp.route('/clean', methods=['GET'])
def borrar_datos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Multipropietario')
        conn.commit()  # Confirmar la transacción
        mensaje = {'mensaje': 'Datos borrados exitosamente'}
    except Exception as e:
        conn.rollback()  # Revertir la transacción en caso de error
        mensaje = {'error': str(e)}
    finally:
        cursor.close()
        conn.close()
    return jsonify(mensaje)
