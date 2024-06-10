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
        if int(row["ano_vigencia_i"]) < 2019:
            row["ano_vigencia_i"] = "2019"
        if int(row["derecho"]) > 0:
            result.append(row)
    return result


def handle_8(adquirentes, enajenantes, propiedad, value):
    result = []
    for adquirente in adquirentes:
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
    for enajenante in enajenantes:
        row = {
            'comuna': propiedad["comuna"],
            'manzana': propiedad["manzana"],
            'predio': propiedad["predio"],
            'run': enajenante['RUNRUT'],
            'derecho': enajenante['derecho'],
            'fojas': value['fojas'],
            'fecha_inscripcion': value['fecha_inscripcion'],
            'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
            'numero_inscripcion': value['numero_inscripcion'],
            'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
        }
        result.append(row)
    return result


def calcular_derechos(multipropietario_temp, value):
    derechos = {}
    total_enajenado = 0
    total_adquirido = 0
    fantasmas = {}

    # Crear un diccionario inicial de derechos a partir de multipropietario_temp
    print("TEMP PRE ERROR")
    print(multipropietario_temp[0]["run"])
    for prop in multipropietario_temp:
        run = prop['run']
        derecho = int(prop['derecho'])
        if run in derechos:
            derechos[run] += derecho
        else:
            derechos[run] = derecho

    # Procesar enajenantes
    for enajenante in value["enajenantes"]:
        run = enajenante["RUNRUT"]
        derecho = int(enajenante["derecho"])
        total_enajenado += derecho
        if run in derechos:
            derechos[run] -= derecho
        else:
            derechos[run] = -derecho

        # Verificar si el enajenante tiene un porcentaje negativo
        if derechos[run] < 0:
            derechos[run] = 0
            fantasmas[run] = True

    # Procesar adquirentes
    for adquirente in value["adquirentes"]:
        run = adquirente["RUNRUT"]
        derecho = int(adquirente["derecho"])
        total_adquirido += derecho
        if run in derechos:
            derechos[run] += derecho
        else:
            derechos[run] = derecho

    total_derechos_post_transaccion = sum(derechos.values())
    if total_derechos_post_transaccion > 100:
        factor_ajuste = 100 / total_derechos_post_transaccion
        for run in derechos:
            derechos[run] = round(derechos[run] * factor_ajuste)
    elif total_derechos_post_transaccion < 100:
        sobrante = 100 - total_derechos_post_transaccion
        personas_cero_participacion = [
            run for run, derecho in derechos.items() if derecho == 0]
        if len(personas_cero_participacion) > 0:
            # Repartir el sobrante entre las personas con participación 0
            sobrante_por_persona = sobrante / len(personas_cero_participacion)
            for run in personas_cero_participacion:
                derechos[run] += sobrante_por_persona

    # Derechos a MULTI, se puede separar
    multipropietarios = []

    for run, derecho in derechos.items():
        multipropietario_data = {}
        # Buscar datos en multipropietario_temp si existen
        for temp_prop in multipropietario_temp:
            if temp_prop['run'] == run:
                multipropietario_data.update(temp_prop)
                break
        # Actualizar con datos de value si existen y no están ya en multipropietario_temp
        if 'run' not in multipropietario_data:
            # Verificar en enajenantes de value
            for value_prop in value["enajenantes"]:
                if value_prop["RUNRUT"] == run:
                    multipropietario_data.update({
                        'run': run,
                        'derecho': int(value_prop['derecho']),
                        'fecha_inscripcion': value['fecha_inscripcion'],
                        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
                        'numero_inscripcion': value['numero_inscripcion'],
                        'ano_vigencia_i': int(value['fecha_inscripcion'][:4]),
                        'status': value['status']
                    })
                    break
            # Verificar en adquirentes de value si no se encontró en enajenantes
            if 'run' not in multipropietario_data:
                for value_prop in value["adquirentes"]:
                    if value_prop["RUNRUT"] == run:
                        multipropietario_data.update({
                            'run': run,
                            'derecho': int(value_prop['derecho']),
                            'fecha_inscripcion': value['fecha_inscripcion'],
                            'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
                            'numero_inscripcion': value['numero_inscripcion'],
                            'ano_vigencia_i': int(value['fecha_inscripcion'][:4]),
                            'status': value['status']
                        })
                        break
        # Asignar el derecho ajustado
        multipropietario_data['derecho'] = derecho
        if int(multipropietario_data['derecho']) > 0:
            multipropietarios.append(multipropietario_data)
    # print(multipropietarios)
    return multipropietarios, total_enajenado, total_adquirido


def actualizar_ano_vigencia_f(elementos, ano_actual):
    elementos_temp = []
    for elemento in elementos:
        if elemento:
            if (elemento.get("ano_vigencia_f") is None) and (int(elemento.get("ano_vigencia_i")) < ano_actual):
                elemento["ano_vigencia_f"] = ano_actual - 1
                elementos_temp.append(elemento)
    return elementos_temp


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
            """print("---------------------------------------------------------------------------------------------------")
            print(f"Datos de la propiedad: C: {propiedad['comuna']}, M: {
                  propiedad['manzana']}, P: {propiedad['predio']}")
            print("---------------------------------------------------------------------------------------------------")
            print("Multipropietarios Previa")
            print(multipropietario)
            print("---------------------------------------------------------------------------------------------------")
            print(defaultdict_item) """
            # Fin del código de debuggeo
            if multipropietario is not None:
                multipropietario_temp = multipropietario
            else:
                multipropietario_temp = []

            for key, value in defaultdict_item.items():
                if value["status"] != "invalido" or value["rectificado"]:
                    print("CNE: " + str(value["cne"]))
                    print("MULTIPROPIETARIO ITER")
                    print(multipropietario_temp)
                    print("VALUE")
                    print(value)
                    # print("Temp inicial")
                    # print(multipropietario_temp)
                    if int(value['fecha_inscripcion'][0:4]) <= 2019:
                        ano = 2019
                    else:
                        ano = int(value['fecha_inscripcion'][0:4])
                    # print(ano)
                    if value['cne'] == 99:
                        multipropietario_temp = actualizar_ano_vigencia_f(
                            multipropietario_temp, ano)
                        print("CALCULOCALCULOCALCULOCALCULOCALCULOCALCULOCALCULO")
                        lista_multi = handle_99(value, propiedad)
                        for multi in lista_multi:
                            multipropietario_temp.append(multi)
                        # Imprimir el resultado para verificación
                    elif value['cne'] == 8:
                        # print("PRE")
                        # print(multipropietario_temp)
                        # print("POST")
                        calculo_derechos, suma_derecho_enajenantes, suma_derecho_adquirentes = calcular_derechos(
                            multipropietario_temp, value)
                        multipropietario_temp = actualizar_ano_vigencia_f(
                            multipropietario_temp, ano)
                        print("CALCULOCALCULOCALCULOCALCULOCALCULOCALCULOCALCULO")
                        print(calculo_derechos)
                        for multi in calculo_derechos:
                            multipropietario_temp.append(multi)

                        if (suma_derecho_adquirentes == 0 or suma_derecho_adquirentes == 100):
                            print("Caso ADQ = 0 o = 100")
                        print("---------------------------------------------")
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


@controlador_multipropietarios_bp.route('/buscar', methods=['POST'])
def buscar_datos():
    # Obtener los datos del JSON
    comuna = request.json.get("comuna")
    manzana = request.json.get("manzana")
    predio = request.json.get("predio")
    ano = request.json.get("ano")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Consulta SQL para obtener los elementos que coincidan con los criterios
    query = """
    SELECT * 
    FROM Multipropietario 
    WHERE comuna = %s 
    AND manzana = %s 
    AND predio = %s 
    AND (ano_vigencia_f >= %s OR ano_vigencia_f IS NULL)
    """
    cursor.execute(query, (comuna, manzana, predio, ano))
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


@controlador_multipropietarios_bp.route('/reproces', methods=['POST'])
def reprocesar_tabla():
    comuna = int(request.json.get("comuna"))
    manzana = int(request.json.get("manzana"))
    predio = int(request.json.get("predio"))
    ano = str(request.json.get("ano"))
    if ano == "":
        ano = "1000"
    algoritmo([{'comuna': comuna, 'manzana': manzana,
              'predio': predio, 'fecha_inscripcion': ano}])
    return "reprocesado completo"
