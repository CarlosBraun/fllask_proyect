'''
En este módulo
'''
import copy
from controladores.controlador_requests import (
    obtener_conexion_db,
    obtener_multipropietario_data,
    request_algorithm_data,
    limpiar_multipropietario,
    ingresar_multipropietarios,
    eliminar_ultimo_registro_multipropietario

)
from controladores.controlador_queries import (
    generar_query_obtener_multipropietarios,
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
    return row if float(row["derecho"]) > 0 else None

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
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4]),
        'ano_vigencia_f': None
    }
def construir_fila_distribuir_100(persona, propiedad, value, a_distribuir):
    '''Construye una fila con los datos de la persona (adquirente o enajenante) y la propiedad.'''
    return {
        'comuna': propiedad["comuna"],
        'manzana': propiedad["manzana"],
        'predio': propiedad["predio"],
        'run': persona['RUNRUT'],
        'derecho':str(float(persona['derecho'])*a_distribuir/100),
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
        'derecho':float(persona['derecho']) * variacion_derecho_enajenante,
        'fojas': value['fojas'],
        'fecha_inscripcion': value['fecha_inscripcion'],
        'ano_inscripccion': int(value['fecha_inscripcion'][:4]),
        'numero_inscripcion': value['numero_inscripcion'],
        'ano_vigencia_i': int(value['fecha_inscripcion'][:4])
    }

def construir_fila_ena_fantasma(persona, propiedad, ano):
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
                'ano_vigencia_i': ano,
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
def obtener_ultimo_registro(propiedad, ano_actual):
    '''Recibe todas las filas de la multipropietario y retorna las que no tienen ano_vigencia_f'''
    result = []
    data = obtener_multipropietario_data([propiedad])[0]
    for i in data:
        ano_vigencia_f = i.get('ano_vigencia_f')
        ano_vigencia_i = i.get('ano_vigencia_i')
        if ano_vigencia_f is None and (ano_vigencia_i is None or (isinstance(ano_vigencia_i, int)
                                                                  and ano_vigencia_i < ano_actual)):
            result.append(i)
    return result

def revisar_multipropietario(multipropietario):
    '''Recibe todas las filas de la multipropietario y retorna un arreglo vacío en caso
    de no existir registros
    '''
    result =[]
    for i in multipropietario:
        result.append(i)
    return result

def inicializar_derechos(multipropietario_temp):
    '''
    Inicializa el diccionario de derechos a partir de los datos de multipropietario_temp.
    '''
    derechos = {}
    for prop in multipropietario_temp:
        run = prop['run']
        derecho = float(prop['derecho'])
        if run in derechos:
            derechos[run] += derecho
        else:
            derechos[run] = derecho
    return derechos

def calcular_derechos_enajenantes(enajenantes, derechos, total_enajenado, multipropietario_temp):
    '''
    Procesa la lista de enajenantes, actualizando el diccionario de derechos,
    el total enajenado. Además retorna un count() de los enajenantes.
    '''
    conteo = 0
    derecho = 0
    for enajenante in enajenantes:
        conteo += 1
        run = enajenante["RUNRUT"]
        for i in multipropietario_temp:
            ano_vigencia_f = i.get('ano_vigencia_f')
            if i['run'] == run and ano_vigencia_f is None:
                derecho += float(i['derecho'])
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
        derecho = float(adquirente["derecho"])
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
    total_enajenado = calcular_derechos_enajenantes(value["enajenantes"], derechos,
                                                     total_enajenado , multipropietario_temp)
    total_adquirido = calcular_derechos_adquirentes(value["adquirentes"], derechos, total_adquirido)

    return derechos ,total_enajenado, total_adquirido
###    CÓDIGO POR REFACTORIZAR
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


def ejecutar_algoritmo(datos):
    '''Es el ejecutar_algoritmo central, procesa los formularios y rellena la Multipropietario'''
    print("COMIENZO ejecutar_ALGORITMO------------")
    data = request_algorithm_data(datos)
    for lista in data:
        contador = 0
        ano_corte = 0
        multipropietario_temp = None
        for formularios_dict in lista:
            propiedad = datos[contador]
            limpiar_multipropietario(propiedad)
            ultimo_registro = []
            # Fin del código de Debugger
            for _,value in formularios_dict.items():
                print("Ciclo------------------------")
                print("FORM")
                ano_form = int(value['fecha_inscripcion'][0:4])
                print(ano_form)
                print(value)
                print("---------------------------------------")
                cne = int(value["cne"])
                if ano_corte == 0:
                    ano_corte = ano_form
                elif ano_corte < ano_form:
                    print("CICLO INTERNOOOOOOOOOOOOOOOOOOOOOOO")
                    multipropietario_temp = realizar_merge(multipropietario_temp)
                    multipropietario_temp = ajustar_derechos(multipropietario_temp)
                    multipropietario_temp =eliminar_enas_con_derecho_cero(multipropietario_temp)
                    ultimo_registro =acotar_registro_anterior(ultimo_registro , ano_form)
                    print("ÚLTIMO REGISTRO")
                    for i in ultimo_registro:
                        print(i)
                    eliminar_ultimo_registro_multipropietario(propiedad)
                    print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
                    print(ultimo_registro)
                    multipropietario = ultimo_registro
                    for i in multipropietario_temp:
                        multipropietario.append(i)
                    print("MULTIPROPIETARIO A INGRESAR")
                    for i in multipropietario:
                        print(i)
                    print("-------------------------")
                    ingresar_multipropietarios(multipropietario)
                    multipropietario_temp = None
                if multipropietario_temp is None:
                    multipropietario_temp=obtener_ultimo_registro(propiedad,ano_form)
                    print(propiedad)
                    ultimo_registro =obtener_ultimo_registro(propiedad, ano_form)
                if cne == 99:
                    multipropietario_temp = procesar_resolucion_de_patrimonio(value,propiedad)
                if cne == 8:
                    procesar_compra_venta(multipropietario_temp,value, propiedad)
            if multipropietario_temp is not None:
                multipropietario_temp = realizar_merge(multipropietario_temp)
                multipropietario_temp = ajustar_derechos(multipropietario_temp)
                multipropietario_temp =eliminar_enas_con_derecho_cero(multipropietario_temp)
                ultimo_registro =acotar_registro_anterior(ultimo_registro , ano_form)
                print("ÚLTIMO REGISTRO")
                for i in ultimo_registro:
                    print(i)
                eliminar_ultimo_registro_multipropietario(propiedad)
                multipropietario = ultimo_registro
                for i in multipropietario_temp:
                    multipropietario.append(i)
                print("MULTIPROPIETARIO A INGRESAR")
                for i in multipropietario:
                    print(i)
                print("-------------------------")
                ingresar_multipropietarios(multipropietario)


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
    generar_registros_form_a_multi(value["adquirentes"],
                                            value["enajenantes"], propiedad, value)
    data_temp = calcular_derechos_totales(multipropietario_temp, value)
    _,enajenado, adquirido = data_temp
    total_adquirido , cantidad_adq = adquirido
    _, cantidad_ena = enajenado
    if (total_adquirido == 100 or total_adquirido == 0):
        distribuir_100(value, propiedad, multipropietario_temp)
        print("Distribuir%=100();")

    elif (100>total_adquirido>0 and (cantidad_ena ==1 and cantidad_adq ==1)):
        print("Distribuir%<100();")
        distribuir_menos_100(value, propiedad, multipropietario_temp)
    else:
        distribuir_general(value, propiedad, multipropietario_temp)
        print("Distribuir%s();")

def distribuir_100(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución del caso Distribuir 100%'''
    #función que llevo a 0 el derecho en la TEMP si en value enajenante hace match
    #  con el rut de la multipropietario en este caso
    rut_enajenantes = []
    for i in (value["enajenantes"]):
        rut_enajenantes.append(i["RUNRUT"])
    total_enajenado = 0
    for i in rut_enajenantes:
        for j in multipropietario_temp:
            if i == j["run"]:
                total_enajenado += float(j["derecho"])
    print(rut_enajenantes)
    a_distribuir = total_enajenado
    print("Derecho a distribuir:", a_distribuir)
    if a_distribuir == 0:
        a_distribuir = 100
    for enajenante in value["enajenantes"]:
        for temp_row in multipropietario_temp:
            if temp_row['run'] == enajenante['RUNRUT']:
                temp_row['derecho'] = 0
    for adquirente in value["adquirentes"]:
        row = construir_fila_distribuir_100(adquirente, propiedad, value, a_distribuir )
        multipropietario_temp.append(row)#Se agregan las filas nuevas, pero no se maneja
        #la resta de las viejas enagenadas

def distribuir_menos_100(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución del caso Distribuir <100%'''
    print(value)
    ano_actual = value["fecha_inscripcion"][:4]
    multipropietario_dict = {}
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            multipropietario_dict[run] += float(prop['derecho'])
        else:
            multipropietario_dict[run] = float(prop['derecho'])

    print("Multi Dict")
    print(multipropietario_dict)
    # Iterar sobre los enajenantes y restar sus derechos en multipropietario_dict
    for enajenante in value['enajenantes']:
        run = enajenante['RUNRUT']
        derecho = float(enajenante['derecho'])
        if run in multipropietario_dict and derecho>0:
            print("entro", run , multipropietario_dict[run])
            variacion_derecho_enajenante = float(multipropietario_dict[run])/100
            print(variacion_derecho_enajenante)
            derecho_enajenante = variacion_derecho_enajenante * (100-float(derecho))
            print(derecho_enajenante)
            multipropietario_dict[run] = derecho_enajenante
            print("ÑÑÑÑÑÑÑÑÑÑÑÑÑÑÑÑ")
            print(multipropietario_dict)
            print("ÑÑÑÑÑÑÑÑÑÑÑÑÑÑÑÑ")
        else:
            variacion_derecho_enajenante = 100
            multipropietario_temp.append(construir_fila_var_ena_100(enajenante, propiedad, value))

    # Actualizar multipropietario_temp con los derechos ajustados
        for prop in multipropietario_temp:
            run = prop['run']
            if run in multipropietario_dict:
                prop['derecho'] = multipropietario_dict[run]
                prop['ano_vigencia_i'] = int(ano_actual)
        for adquirente in value['adquirentes']:
            multipropietario_temp.append(construir_fila_adq(adquirente, propiedad,
                                                             value, variacion_derecho_enajenante))
    print("Multi Dict")
    print(multipropietario_dict)
    print("Datos actualizados de multipropietario_temp:")
    print(multipropietario_temp)

    return 200

def distribuir_general(value, propiedad, multipropietario_temp):
    '''Esta función se encarga de manejar la distribución el resto de los casos que
    no fueron especificados previamente'''

    # Crear un diccionario de derechos en multipropietario_temp
    multipropietario_dict = {}
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            multipropietario_dict[run] += float(prop['derecho'])
        else:
            multipropietario_dict[run] = float(prop['derecho'])

    # Iterar sobre los enajenantes y restar sus derechos en multipropietario_dict
    for enajenante in value['enajenantes']:
        run = enajenante['RUNRUT']
        derecho = float(enajenante['derecho'])
        if run in multipropietario_dict:
            multipropietario_dict[run] -= derecho
        else:
            multipropietario_temp.append(construir_fila_ena_fantasma(enajenante,
                                                                      propiedad,value["fecha_inscripcion"][:4]))

    # Actualizar multipropietario_temp con los derechos ajustados
    for prop in multipropietario_temp:
        run = prop['run']
        if run in multipropietario_dict:
            prop['derecho'] = multipropietario_dict[run]
            prop['ano_vigencia_i'] = value["fecha_inscripcion"][:4]

    # Insertar los adquirentes en multipropietario_temp
    for adquirente in value['adquirentes']:
        run = adquirente['RUNRUT']
        derecho = float(adquirente['derecho'])
        multipropietario_temp.append(construir_fila_general(adquirente, propiedad, value))

    return 200

def acotar_registro_anterior(multipropietario_temp, ano):
    '''Retorna la tabla multipropietario con los años anteriores acotados'''
    multi_temp = copy.deepcopy(multipropietario_temp)
    print("REVISION ULTIMO BUG------------------------------------")
    for i in multi_temp:
        print(i)
        ano_vigencia_f = i.get('ano_vigencia_f')
        if ano_vigencia_f is None:
            i['ano_vigencia_f'] = ano -1
    return multi_temp

def realizar_merge(multipropietario_temp):
    '''Realiza y retorna el merge de los particulares en la multipropietario'''
    agrupados_por_rut = {}

    for registro in multipropietario_temp:
        rut = registro['run']
        derecho = float(registro['derecho'])  # Aseguramos que derecho es float

        if rut not in agrupados_por_rut:
            agrupados_por_rut[rut] = registro.copy()
        else:
            agrupados_por_rut[rut]['derecho'] = float(agrupados_por_rut[rut]['derecho']) + derecho
            # Comparar fechas de inscripción, considerando casos donde la fecha es None
            fecha_inscripcion_actual = registro.get('fecha_inscripcion')
            fecha_inscripcion_agrupada = agrupados_por_rut[rut].get('fecha_inscripcion')

            if fecha_inscripcion_actual is None or (
                fecha_inscripcion_agrupada is not None and
                fecha_inscripcion_actual < fecha_inscripcion_agrupada):
                for key, value in registro.items():
                    if value is not None:
                        agrupados_por_rut[rut][key] = value
            else:
                # Actualizar el año de vigencia inicial con el del nuevo registro si es más reciente
                agrupados_por_rut[rut]['ano_vigencia_i'] = registro.get('ano_vigencia_i',
                                                agrupados_por_rut[rut]['ano_vigencia_i'])

    # Convertimos el diccionario de vuelta a una lista
    merged_list = list(agrupados_por_rut.values())

    # Establecer derecho en 0 si es negativo
    for registro in merged_list:
        if float(registro['derecho']) < 0:
            registro['derecho'] = 0

    return merged_list




def ajustar_derechos(multipropietario_temp):
    '''Ajusta los derechos de la multipropietario_temp para que la sumatoria de derechos sea 100'''
    total_derechos = sum(float(prop['derecho']) for prop in multipropietario_temp)
    fantasmas = [prop for prop in multipropietario_temp if float(prop['derecho']) == 0 and
                 prop['fecha_inscripcion'] is None and
                 prop['ano_inscripccion'] is None and
                 prop['numero_inscripcion'] is None and
                 prop['fojas'] is None and
                 prop['status'] is None]
    factor_ajuste = 1
    if total_derechos == 100:
        factor_ajuste = 1 # No se necesita ajuste
    elif total_derechos < 100 and fantasmas:
        sobrante = 100 - total_derechos
        sobrante_por_fantasma = sobrante / len(fantasmas)
        for fantasma in fantasmas:
            fantasma['derecho'] = sobrante_por_fantasma
            for prop in multipropietario_temp:
                if prop['run'] == fantasma['run']:
                    prop['derecho'] = fantasma['derecho']
    elif total_derechos >100:
        factor_ajuste = 100 / total_derechos

    for prop in multipropietario_temp:
        prop['derecho'] = float(prop['derecho']) * factor_ajuste
    return multipropietario_temp

def eliminar_enas_con_derecho_cero(multipropietario_temp):
    '''Elimina las filas que no pertenecen a los fantasmas y tienen derecho 0 y negativo'''
    return [prop for prop in multipropietario_temp if float(prop['derecho']) > 0]

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
    query = generar_query_obtener_multipropietarios()
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        rows = filtrar_datos_multipropietario(rows,str(comuna),int(manzana),int(predio),int(ano))
        return rows
    finally:
        cursor.close()
        conn.close()

def filtrar_datos_multipropietario(rows, comuna, manzana, predio, ano):
    """
    Filtra los datos de la lista de diccionarios 'rows' según los parámetros especificados.
    La necesidad de crear esta función nace de la incompatibilidad de realizar la búsqueda
    mediante queries dinámicas.

    """
    resultado_filtrado = []
    for row in rows:
        if (row['comuna'] == comuna and
            row['manzana'] == manzana and
            row['predio'] == predio and
            (row['ano_vigencia_f'] is None or row['ano_vigencia_f'] >= ano)):
            resultado_filtrado.append(row)
    return resultado_filtrado

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
