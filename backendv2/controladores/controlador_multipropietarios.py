'''
En este módulo
'''
from controladores.controlador_requests import (
    obtener_conexion_db,
    obtener_multipropietario_data,
    request_algorithm_data,
    limpiar_multipropietario,
    ingresar_multipropietarios
)
from controladores.controlador_queries import (
    generar_query_obtener_multipropietarios,
    generar_query_busqueda_multipropietario,
    generar_query_borrar_multipropietario
    )
from flask import Blueprint, jsonify, request
from mysql.connector import Error
controlador_multipropietarios_bp = Blueprint(
    'controlador_multipropietarios', __name__)

def construir_fila_adquirente(adquirente, propiedad, value):
    '''Construye una fila con los datos del adquirente y la propiedad.'''
    return {
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

def validar_y_ajustar_fila(row):
    '''Valida y ajusta los datos de la fila según las reglas de negocio.'''
    return row if int(row["derecho"]) > 0 else None

def procesar_resolucion_de_patrimonio(value, propiedad):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 99'''
    result = []
    for adquirente in value['adquirentes']:
        row = construir_fila_adquirente(adquirente, propiedad, value)
        row = validar_y_ajustar_fila(row)
        if row is not None:
            result.append(row)
    return result

def construir_fila_general(persona, propiedad, value):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho': persona['derecho'],
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }


def procesar_compra_venta(adquirentes, enajenantes, propiedad, value):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 8'''
    result = []
    for adquirente in adquirentes:
        row = construir_fila_general(adquirente, propiedad, value)
        result.append(row)
    for enajenante in enajenantes:
        row = construir_fila_general(enajenante, propiedad, value)
        result.append(row)
    return result


def inicializar_derechos(multipropietario_temp):
    '''
    Inicializa el diccionario de derechos a partir de los datos de multipropietario_temp.
    '''
    derechos = {}
    for prop in multipropietario_temp:
        run = prop['run']
        derecho = int(prop['derecho'])
        if run in derechos:
            derechos[run] += derecho
        else:
            derechos[run] = derecho
    return derechos

def calcular_derechos_enajenantes(enajenantes, derechos, total_enajenado):
    '''
    Procesa la lista de enajenantes, actualizando el diccionario de derechos,
    el total enajenado y detectando derechos negativos.
    '''
    for enajenante in enajenantes:
        run = enajenante["RUNRUT"]
        derecho = int(enajenante["derecho"])
        total_enajenado += derecho
        if run in derechos:
            derechos[run] -= derecho
        else:
            derechos[run] = -derecho
    return total_enajenado

def calcular_derechos_adquirentes(adquirentes, derechos, total_adquirido):
    '''
    Procesa la lista de adquirentes, actualizando el diccionario de derechos
    y el total adquirido.
    '''
    for adquirente in adquirentes:
        run = adquirente["RUNRUT"]
        derecho = int(adquirente["derecho"])
        total_adquirido += derecho
        if run in derechos:
            derechos[run] += derecho
        else:
            derechos[run] = derecho
    return total_adquirido

def calcular_derechos_totales(multipropietario_temp, value):
    '''
    Retorna el cálculo del total de lo enajenado y de lo adquirido.
    '''
    derechos = inicializar_derechos(multipropietario_temp)
    total_enajenado = 0
    total_adquirido = 0
    total_enajenado = calcular_derechos_enajenantes(value["enajenantes"], derechos, total_enajenado)
    total_adquirido = calcular_derechos_adquirentes(value["adquirentes"], derechos, total_adquirido)

    return derechos ,total_enajenado, total_adquirido





###    CODIGO POR REFACTORIZAR




def calcular_derechos(multipropietario_temp, value, propiedad):
    '''Retorna el calculo de los derechos de cada rut en una propiedad'''
    # Bloque de código para inicializar variables
    data = calcular_derechos_totales(multipropietario_temp, value)
    derechos, total_enajenado, total_adquirido = data
    total_derechos_post_transaccion = sum(derechos.values())



    if total_derechos_post_transaccion > 100:
        ajustar_distribución()
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
    print(derechos)
    print(multipropietario_temp)

    for run, derecho in derechos.items():
        multipropietario_data = {}
        # Buscar datos en multipropietario_temp si existen
        for temp_prop in multipropietario_temp:
            if temp_prop['run'] == run:
                print(temp_prop)
                multipropietario_data.update(temp_prop)
                break
        # Actualizar con datos de value si existen y no están ya en multipropietario_temp
        print(run)
        print(multipropietario_data)
        if 'run' not in multipropietario_data:
            # Verificar en enajenantes de value
            for value_prop in value["enajenantes"]:
                print(value_prop)
                if value_prop["RUNRUT"] == run:
                    multipropietario_data.update({
                        'comuna': propiedad["comuna"],
                        'manzana': propiedad["manzana"],
                        'predio': propiedad["predio"],
                        'fojas': value['fojas'],
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
                            'comuna': propiedad["comuna"],
                            'manzana': propiedad["manzana"],
                            'predio': propiedad["predio"],
                            'fojas': value['fojas'],
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
    print("MULTIMULTIMULTIMULTIMULTIMULTIMULTIMULTIMULTI")
    print(multipropietarios)
    return multipropietarios, total_enajenado, total_adquirido


def actualizar_ano_vigencia_f(elementos, ano):
    '''Retorna el diccionario actualizado con el ano_vigencia_f actualizado'''
    elementos_temp = []
    for elemento in elementos:
        if elemento:
            ano_vigencia_f = elemento.get("ano_vigencia_f")
            if (ano_vigencia_f is None) and (int(ano_vigencia_f) < ano):
                elemento["ano_vigencia_f"] = ano - 1
                elementos_temp.append(elemento)
    return elementos_temp


def algoritmo(datos):
    '''Es el algoritmo central, procesa los formularios y rellena la Multipropietario'''
    datos_multipopietarios = obtener_multipropietario_data(datos)
    data = request_algorithm_data(datos)
    for lista in data:
        contador = 0
        ano_corte = 0
        multipropietario_temp = None
        for formularios_dict in lista:
            propiedad = datos[contador]
            #limpiar_multipropietario(propiedad)
            # Código usado para debuggear a base de prints
            print(f"Datos de la propiedad: C: {propiedad['comuna']}, "
                  f"M: {propiedad['manzana']}, "
                  f"P: {propiedad['predio']}")
            print(formularios_dict)
            # Fin del código de debuggeo
            for _,value in formularios_dict.items():
                ano_form = int(value['fecha_inscripcion'][0:4])
                cne = int(value["cne"])
                if ano_corte == 0:
                    ano_corte = ano_form
                elif ano_corte < ano_form:
                    print("ya loop")
                    #ajustar_derechos()
                    #Acotar registro anterior
                    multipropietario_temp = []

                if multipropietario_temp is None:
                    print(None)
                    multipropietario_temp = datos_multipopietarios[contador] #asegurarse de cargar ultimo registro, es decir datos sin fecha f
                if cne == 99:
                    print(99)
                    #overwrite a la temp
                    multipropietario_temp = procesar_resolucion_de_patrimonio(value,propiedad)
                    print(multipropietario_temp)
                if cne == 8:
                    print(8)
                    data = procesar_compra_venta(value["adquirentes"], value["enajenantes"],
                                                  propiedad, value)
                    for i in data:
                        multipropietario_temp.append(i)
                    print(multipropietario_temp)
                #agrupar_propietarios()
                #limpiar_derechos_negativos()



            contador += 1

    return data

#refactorizado
@ controlador_multipropietarios_bp.route('/', methods=['GET'])
def obtener_datos():
    '''Retorna todos los datos de la tabla Multipropietario'''
    try:
        conn = obtener_conexion_db()
        rows = ejecutar_consulta_multipropietario(conn)
        return jsonify(rows)
    except Error as e:
        return jsonify({'error': str(e)})
    finally:
        conn.close()

def ejecutar_consulta_multipropietario(conn):
    '''Ejecuta la consulta para obtener todos los datos de Multipropietario'''
    with conn.cursor(dictionary=True) as cursor:
        query = generar_query_obtener_multipropietarios()
        cursor.execute(query)
        return cursor.fetchall()

@ controlador_multipropietarios_bp.route('/buscar', methods=['POST'])
def buscar_datos():
    '''Retorna filas de la tabla Multipropietario según una búsqueda'''
    comuna = request.json.get("comuna")
    manzana = request.json.get("manzana")
    predio = request.json.get("predio")
    ano = request.json.get("ano")
    rows = ejecutar_consulta_busqueda_multipropietario(comuna, manzana, predio, ano)
    return jsonify(rows)

def ejecutar_consulta_busqueda_multipropietario(comuna, manzana, predio, ano):
    '''Ejecuta la consulta SQL para buscar datos en la tabla Multipropietario'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    query = generar_query_busqueda_multipropietario()
    try:
        cursor.execute(query, (comuna, manzana, predio, ano))
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        conn.close()


@ controlador_multipropietarios_bp.route('/clean', methods=['GET'])
def borrar_datos():
    '''Elimina todas las filas de la tabla Multipropietario'''
    mensaje = ejecutar_borrado_multipropietario()
    return jsonify(mensaje)

def ejecutar_borrado_multipropietario():
    '''Ejecuta la consulta SQL para borrar todas las filas de la tabla Multipropietario'''
    conn = obtener_conexion_db()
    cursor = conn.cursor()
    query = generar_query_borrar_multipropietario()
    try:
        cursor.execute(query)
        conn.commit()  # Confirmar la transacción
        mensaje = {'mensaje': 'Datos borrados exitosamente'}
    except Error as e:
        conn.rollback()  # Revertir la transacción en caso de error
        mensaje = {'error': str(e)}
    finally:
        cursor.close()
        conn.close()
    return mensaje
