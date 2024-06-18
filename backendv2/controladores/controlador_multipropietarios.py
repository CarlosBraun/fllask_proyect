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

def construir_fila_general(persona, propiedad, value):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    print(persona)
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
def construir_fila_distribuir_100(persona, propiedad, value, a_distribuir):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    print(persona)
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho':str(int(persona['derecho'])*a_distribuir),
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def construir_fila_var_ena_100(persona, propiedad, value):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho':0,
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def construir_fila_adq(persona, propiedad, value, variacion_derecho_enajenante):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho':int(persona['derecho']) * variacion_derecho_enajenante,
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def construir_fila_ena_fantasma(persona, propiedad):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad['comuna'],
                'manzana': propiedad['manzana'],
                'predio': propiedad['predio'],
                'run': persona['RUNRUT'],
                'derecho': 0,
                'fecha_inscripcion': None,
                'ano_inscripccion': None,
                'numero_inscripcion': None,
                'fojas': None,
                'ano_vigencia_i': None,
                'status': None
    }
def generar_registros_form_a_multi(adquirentes, enajenantes, propiedad, value):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 8'''
    result = []
    for adquirente in adquirentes:
        row = construir_fila_general(adquirente, propiedad, value)
        result.append(row)
    for enajenante in enajenantes:
        row = construir_fila_general(enajenante, propiedad, value)
        result.append(row)
    return result
def cargar_ultimo_registro(multipropietario):
    '''Recibe todas las filas de la multipropietario y retorna las que no tienen ano_vigencia_f'''
    print("CARGAR ULT REGISTRO")
    result =[]
    for i in multipropietario:
        if i["ano_viencia_f"] is None:
            result.append(i)
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
    el total enajenado. Además retorna un count() de los enajenantes.
    '''
    conteo = 0
    for enajenante in enajenantes:
        conteo += 1
        run = enajenante["RUNRUT"]
        derecho = int(enajenante["derecho"])
        total_enajenado += derecho
        if run in derechos:
            derechos[run] -= derecho
    return total_enajenado, conteo

def calcular_derechos_adquirentes(adquirentes, derechos, total_adquirido):
    '''
    Procesa la lista de adquirentes, actualizando el diccionario de derechos
    y el total adquirido. Además retorna un count() de los adquirentes.
    '''
    conteo = 0
    for adquirente in adquirentes:
        conteo += 1
        run = adquirente["RUNRUT"]
        derecho = int(adquirente["derecho"])
        total_adquirido += derecho
        if run in derechos:
            derechos[run] += derecho
    return total_adquirido , conteo

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
    print("datos")
    datos_multipopietarios = obtener_multipropietario_data(datos)
    print(datos_multipopietarios)
    data = request_algorithm_data(datos)
    for lista in data:
        contador = 0
        ano_corte = 0
        multipropietario_temp = None
        for formularios_dict in lista:
            propiedad = datos[contador]
            limpiar_multipropietario(propiedad)
            print(f"Datos de la propiedad: C: {propiedad['comuna']}, "
                  f"M: {propiedad['manzana']}, "
                  f"P: {propiedad['predio']}")
            print(formularios_dict)
            # Fin del código de debuggeo
            for _,value in formularios_dict.items():
                print("OTRO FORM------------------------")
                ano_form = int(value['fecha_inscripcion'][0:4])
                cne = int(value["cne"])
                if ano_corte == 0:
                    ano_corte = ano_form
                elif ano_corte < ano_form:
                    print("Multi LOOP")
                    print(multipropietario_temp)
                    multipropietario_temp = ajustar_derechos(multipropietario_temp)
                    print("Ajuste")
                    print(multipropietario_temp)
                    #Acotar registro anterior
                    ingresar_multipropietarios(multipropietario_temp)

                    multipropietario_temp = []

                if multipropietario_temp is None:
                    print(None)
                    multipropietario_temp = cargar_ultimo_registro(datos_multipopietarios[contador])
                    #asegurarse de cargar ultimo registro, es decir datos sin fecha f
                if cne == 99:
                    print(99)
                    multipropietario_temp = procesar_resolucion_de_patrimonio(value,propiedad)
                if cne == 8:
                    print(8)
                    procesar_compra_venta(multipropietario_temp,value, propiedad)

            if multipropietario_temp is not None:
                print(multipropietario_temp)
                multipropietario_temp = ajustar_derechos(multipropietario_temp)
                multipropietario_temp =eliminar_no_fantasmas_con_derecho_cero(multipropietario_temp)
                print("Ajuste")
                print(multipropietario_temp)
                #Acotar registro anterior
                ingresar_multipropietarios(multipropietario_temp)


            contador += 1

    return data
def procesar_resolucion_de_patrimonio(value, propiedad):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 99'''
    result = []
    for adquirente in value['adquirentes']:
        row = construir_fila_adquirente(adquirente, propiedad, value)
        row = validar_y_ajustar_fila(row)
        if row is not None:
            result.append(row)
    return result
def procesar_compra_venta(multipropietario_temp,value, propiedad):
    '''Retorna un diccionario con datos para la multiporpietario. CNE 8'''
    registros = generar_registros_form_a_multi(value["adquirentes"],
                                            value["enajenantes"], propiedad, value)
    for i in registros:
        print(i)
#                        multipropietario_temp.append(i)
    data_temp = calcular_derechos_totales(multipropietario_temp, value)
    _,enajenado, adquirido = data_temp
    total_adquirido , cantidad_adq = adquirido
    total_enajenado, cantidad_ena = enajenado


    if (total_adquirido == 100 or total_adquirido == 0):
        distribuir_100(total_enajenado, value, propiedad, multipropietario_temp)
        print("Distribuir%=100();")

    elif (100>total_adquirido>0 and (cantidad_ena ==1 and cantidad_adq ==1)):
        print("Distribuir%<100();")
        distribuir_menos_100(value, propiedad, multipropietario_temp)
    else:
        distribuir_general(value, propiedad, multipropietario_temp)
        print("Distribuir%s();")

def distribuir_100(total_enajenado, value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución del caso Distribuir 100%'''
    a_distribuir = total_enajenado
    if a_distribuir == 0:
        a_distribuir = 100
    for adquirente in value["adquirentes"]:
        row = construir_fila_distribuir_100(adquirente, propiedad, value, a_distribuir )
        multipropietario_temp.append(row)

def distribuir_menos_100(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución del caso Distribuir <100%'''
    print(value)
    print(propiedad)
    print(multipropietario_temp)

    multipropietario_dict = {}
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            multipropietario_dict[run] += int(prop['derecho'])
        else:
            multipropietario_dict[run] = int(prop['derecho'])

    # Iterar sobre los enajenantes y restar sus derechos en multipropietario_dict
    for enajenante in value['enajenantes']:
        run = enajenante['RUNRUT']
        derecho = int(enajenante['derecho'])
        if run in multipropietario_dict and derecho>0:
            variacion_derecho_enajenante = multipropietario_dict[run]
            derecho_enajenante = variacion_derecho_enajenante * (100-int(derecho))
            multipropietario_dict[run] = derecho_enajenante
        else:
            variacion_derecho_enajenante = 100
            multipropietario_temp.append(construir_fila_var_ena_100(enajenante, propiedad, value))


    # Actualizar multipropietario_temp con los derechos ajustados
        for prop in multipropietario_temp:
            run = prop['run']
            if run in multipropietario_dict:
                prop['derecho'] = multipropietario_dict[run]
        for adquirente in value['adquirentes']:
            multipropietario_temp.append(construir_fila_adq(adquirente, propiedad,
                                                             value, variacion_derecho_enajenante))
    print("Datos actualizados de multipropietario_temp:")
    print(multipropietario_temp)

    return 200

def distribuir_general(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución el resto de los casos que
    no fueron especificados previamente'''
    print(value)
    print(propiedad)
    print(multipropietario_temp)

    # Crear un diccionario de derechos en multipropietario_temp
    multipropietario_dict = {}
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            multipropietario_dict[run] += int(prop['derecho'])
        else:
            multipropietario_dict[run] = int(prop['derecho'])

    # Iterar sobre los enajenantes y restar sus derechos en multipropietario_dict
    for enajenante in value['enajenantes']:
        run = enajenante['RUNRUT']
        derecho = int(enajenante['derecho'])
        if run in multipropietario_dict:
            multipropietario_dict[run] -= derecho
        else:
            multipropietario_temp.append(construir_fila_ena_fantasma(enajenante, propiedad))

    # Actualizar multipropietario_temp con los derechos ajustados
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            prop['derecho'] = multipropietario_dict[run]

    # Insertar los adquirentes en multipropietario_temp
    for adquirente in value['adquirentes']:
        run = adquirente['RUNRUT']
        derecho = int(adquirente['derecho'])
        multipropietario_temp.append(construir_fila_general(adquirente, propiedad, value))
    print("Datos actualizados de multipropietario_temp:")
    print(multipropietario_temp)

    return 200

def ajustar_derechos(multipropietario_temp):
    '''Ajusta los derechos de la multipropietario_temp para que la sumatoria de derechos sea 100'''
    total_derechos = sum(int(prop['derecho']) for prop in multipropietario_temp)
    fantasmas = [prop for prop in multipropietario_temp if int(prop['derecho']) == 0 and
                 prop['fecha_inscripcion'] is None and
                 prop['ano_inscripccion'] is None and
                 prop['numero_inscripcion'] is None and
                 prop['fojas'] is None and
                 prop['ano_vigencia_i'] is None and
                 prop['status'] is None]
    factor_ajuste = 1
    if total_derechos == 100:
        print("Caso1")
        return multipropietario_temp  # No se necesita ajuste
    elif total_derechos < 100 and fantasmas:
        print("Caso2")
        sobrante = 100 - total_derechos
        sobrante_por_fantasma = sobrante / len(fantasmas)
        for fantasma in fantasmas:
            fantasma['derecho'] = sobrante_por_fantasma
            for prop in multipropietario_temp:
                if prop['run'] == fantasma['run']:
                    prop['derecho'] = fantasma['derecho']
    elif total_derechos >100:
        print("Caso3")
        factor_ajuste = 100 / total_derechos

    for prop in multipropietario_temp:
        prop['derecho'] = round(int(prop['derecho']) * factor_ajuste)
    return multipropietario_temp

def eliminar_no_fantasmas_con_derecho_cero(multipropietario_temp):
    '''Elimina las filas que no pertenecen a los fantasmas y tienen derecho 0 y negativo'''
    return [prop for prop in multipropietario_temp if not (int(prop['derecho']) <= 0 and
                                                          prop['fecha_inscripcion'] is not None and
                                                          prop['ano_inscripccion'] is not None and
                                                          prop['numero_inscripcion'] is not None and
                                                          prop['fojas'] is not None and
                                                          prop['ano_vigencia_i'] is not None and
                                                          prop['status'] is not None)]

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
