'''
En este módulo se definen funciones auxiliares para el controlador multipropietario
que interactúan con la base de datos y procesan formularios.

Funciones definidas:
- obtener_conexion_db(): Retorna la conexión configurada a la base de datos.
- inicializar_formularios_agrupados(): Inicializa una estructura para agrupar formularios.
- procesar_formulario(formulario, formularios_agrupados): Procesa y actualiza formularios agrupados.
- convertir_formulario_diccionario_a_lista(formularios_agrupados): Convierte estructuras de
  datos agrupadas en listas de formularios.
- reagrupar_formularios(json_data): Agrupa formularios en un formato deseado a partir de datos JSON.
- definir_clave_ordenacion(item): Define una clave para ordenar diccionarios por claves ascendentes.
- ordenar_datos_por_claves(data): Ordena una lista de diccionarios por claves ascendentes.
- ordenar_json_por_claves_ascendente(data): Ordena formularios JSON por claves ascendentes.
- request_algorithm_data(data): Retorna formularios procesados dados una tripleta y un año.
- obtener_formularios(cursor, propiedades): Obtiene formularios de la base de datos según
  propiedades.
- procesar_formularios(formularios): Procesa formularios obtenidos y los agrupa.
- ejecutar_query_multipropietario(cursor, propiedades): Ejecuta consulta SQL para buscar
  en Multipropietario.
- obtener_multipropietario_data(data): Retorna filas en Multipropietario según propiedades.
- ejecutar_limpiar_multipropietario(cursor, propiedad, ano_inicio): Ejecuta consulta SQL para
  limpiar registros en Multipropietario.
- limpiar_multipropietario(propiedad): Elimina registros en Multipropietario a partir de un
  año específico.
- ejecutar_ingresar_multipropietarios(cursor, row): Ejecuta consulta SQL para ingresar registros 
  en Multipropietario.
- ingresar_multipropietarios(data): Ingresa datos en la tabla Multipropietario.

Este archivo define operaciones para interactuar con la base de datos y procesar datos relacionados
con formularios de multipropietario, manteniendo una estructura organizada y coherente.
'''
from collections import defaultdict
import mysql.connector
from config import DB_CONFIG
from controladores.controlador_queries import(
    generar_query_obtener_formularios_asc,
    generar_query_busqueda_multipropietario_completa,
    generar_query_limpiar_multipropietario,
    generar_query_ingresar_multipropietarios
)


def obtener_conexion_db():
    '''Retorna la configuración de la conexión con la base de datos'''
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


def inicializar_formularios_agrupados():
    '''Inicializa la estructura de datos para agrupar los formularios'''
    return defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        'enajenantes': [],
        'adquirentes': []
    })))

def procesar_formulario(formulario, formularios_agrupados):
    '''Procesa cada formulario y actualiza el diccionario agrupado'''
    for propiedad in formulario:
        comuna = propiedad['comuna']
        manzana = propiedad['manzana']
        predio = propiedad['predio']
        numero_inscripcion = propiedad['numero_inscripcion']
        tipo = propiedad['tipo']
        ena = 'enajenantes' #referente al diccionario
        adq = 'adquirentes' #referente al diccionario
        if tipo == 'enajenante':
            formularios_agrupados[comuna][manzana][predio][numero_inscripcion][ena].append({
                'RUNRUT': propiedad['RUNRUT'],
                'derecho': propiedad['derecho']
            })
        elif tipo == 'adquirente':
            formularios_agrupados[comuna][manzana][predio][numero_inscripcion][adq].append({
                'RUNRUT': propiedad['RUNRUT'],
                'derecho': propiedad['derecho']
            })
        # Copiar los demás datos necesarios
        for key, value in propiedad.items():
            if key not in ['RUNRUT', 'derecho', 'tipo']:
                formularios_agrupados[comuna][manzana][predio][numero_inscripcion][key] = value

def convertir_formulario_diccionario_a_lista(formularios_agrupados):
    '''Convierte el diccionario agrupado en la lista de formularios en el formato deseado'''
    resultado_final = []
    for comuna, manzanas in formularios_agrupados.items():
        for manzana, predios in manzanas.items():
            for predio, inscripciones in predios.items():
                for numero_inscripcion, datos in inscripciones.items():
                    resultado_final.append({
                        'comuna': comuna,
                        'manzana': manzana,
                        'predio': predio,
                        'numero_inscripcion': numero_inscripcion,
                        'cne': datos['cne'],
                        'fojas': datos['fojas'],
                        'fecha_inscripcion': datos['fecha_inscripcion'],
                        'numero_atencion': datos['numero_atencion'],
                        'status': datos['status'],
                        'herencia': datos['herencia'],
                        'enajenantes': datos['enajenantes'],
                        'adquirentes': datos['adquirentes']
                    })
    return resultado_final

def reagrupar_formularios(json_data):
    '''Retorna los formularios en un formato agrupado'''
    formularios_agrupados = inicializar_formularios_agrupados()
    for formulario in json_data:
        procesar_formulario(formulario, formularios_agrupados)
    return convertir_formulario_diccionario_a_lista(formularios_agrupados)
# En este archivo se finen las request a la bbdd, pero no se rutea.


def definir_clave_ordenacion(item):
    '''Define la clave de ordenación basada en las claves del diccionario'''
    return sorted(item.keys())

def ordenar_datos_por_claves(data):
    '''Ordena una lista de diccionarios por las claves ascendentes'''
    return sorted(data, key=definir_clave_ordenacion)

def ordenar_json_por_claves_ascendente(data):
    '''Retorna una lista ordenada con los formularios'''
    sorted_data = ordenar_datos_por_claves(data)
    return sorted_data


def ejecutar_query_formulario(cursor, propiedades):
    '''Ejecuta la consulta SQL con los parámetros dados'''
    query = generar_query_obtener_formularios_asc()
    cursor.execute(query, (propiedades['comuna'], propiedades['manzana'],
                            propiedades['predio'], propiedades['fecha_inscripcion']))
    return cursor.fetchall()

def agrupar_formularios(formularios):
    '''Agrupa los formularios en enajenantes y adquirentes'''
    grouped_formularios = defaultdict(
        lambda: {'enajenantes': [], 'adquirentes': [],
                 'cne': None,
                 'fecha_inscripcion': None,
                 'numero_atencion': None,
                 'fojas': None,
                 'numero_inscripcion': None,
                 'status': None,
                 'herencia': None})
    for formulario in formularios:
        key = formulario['fecha_inscripcion'] + "_" + formulario['numero_atencion']
        if grouped_formularios[key]['cne'] is None:
            grouped_formularios[key].update({
                'cne': formulario['cne'],
                'fecha_inscripcion': formulario['fecha_inscripcion'],
                'numero_atencion': formulario['numero_atencion'],
                'fojas': formulario['fojas'],
                'numero_inscripcion': formulario['numero_inscripcion'],
                'status': formulario['status'],
                'herencia': formulario['herencia']
            })
        if formulario["tipo"] == "enajenante":
            grouped_formularios[key]['enajenantes'].append(
                {'RUNRUT': formulario['RUNRUT'], 'derecho': formulario['derecho']})
        elif formulario["tipo"] == "adquirente":
            grouped_formularios[key]['adquirentes'].append(
                {'RUNRUT': formulario['RUNRUT'], 'derecho': formulario['derecho']})
    return grouped_formularios

def obtener_formularios(cursor, propiedades):
    '''Obtiene los formularios de la base de datos según las propiedades dadas'''
    return ejecutar_query_formulario(cursor,propiedades)

def procesar_formularios(formularios):
    '''Procesa los formularios obtenidos y los agrupa'''
    total_data = []
    for formulario in formularios:
        grouped_formularios = agrupar_formularios(formulario)
        total_data.append(grouped_formularios)
    return [ordenar_json_por_claves_ascendente(total_data)]

def request_algorithm_data(data):
    '''Retorna los formularios necesarios para procesar dada una tripleta y un año'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    try:
        formularios = []
        for propiedades in data:
            formularios.append(obtener_formularios(cursor, propiedades))
        final_data = procesar_formularios(formularios)
        return final_data
    finally:
        cursor.close()
        conn.close()

def ejecutar_query_multipropietario(cursor, propiedades):
    '''Ejecuta la consulta SQL con los parámetros dados'''
    query = generar_query_busqueda_multipropietario_completa()
    cursor.execute(query, (propiedades['comuna'], propiedades['manzana'], propiedades['predio']))
    return cursor.fetchall()

def obtener_multipropietario_data(data):
    '''Retorna las filas en la Multipropietario de cierta propiedad'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    total_data = []
    for propiedades in data:
        results = ejecutar_query_multipropietario(cursor, propiedades)
        total_data.append(results)
    cursor.close()
    conn.close()
    return total_data



def ejecutar_limpiar_multipropietario(cursor, propiedad, ano_inicio):
    '''Ejecuta la consulta SQL para eliminar registros de la tabla Multipropietario'''
    query = generar_query_limpiar_multipropietario()
    cursor.execute(query, (
        propiedad['comuna'],
        propiedad['manzana'],
        propiedad['predio'],
        ano_inicio
    ))

def limpiar_multipropietario(propiedad):
    '''Elimina los registros de la tabla Multipropietario un año en adelante
    para cierta propiedad'''
    print(propiedad['fecha_inscripcion'])
    ano_inicio = int(propiedad['fecha_inscripcion'][:4])
    conn = obtener_conexion_db()
    cursor = conn.cursor()

    try:
        ejecutar_limpiar_multipropietario(cursor, propiedad, ano_inicio)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()




def ejecutar_ingresar_multipropietarios(cursor, row):
    '''Ejecuta la consulta SQL para insertar un registro en la tabla Multipropietario'''
    query = generar_query_ingresar_multipropietarios()
    cursor.execute(query, (
        row['comuna'],
        row['manzana'],
        row['predio'],
        row['run'],
        int(row['derecho']),
        row['fojas'],
        row['fecha_inscripcion'],
        row['ano_inscripccion'],
        row['numero_inscripcion'],
        row['ano_vigencia_i'],
        row.get('ano_vigencia_f', None),
        row.get('status', None)
    ))

def ingresar_multipropietarios(data):
    '''Ingresa datos a la tabla Multipropietario'''
    conn = obtener_conexion_db()
    cursor = conn.cursor()

    try:
        for row in data:
            ejecutar_ingresar_multipropietarios(cursor, row)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
