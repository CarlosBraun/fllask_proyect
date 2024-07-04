'''
Este controlador define las funciones que se realizan exclusivamente para
el proceso de los formularios.

Funciones:
- get_atention_number: Retorna el número de atención.
- obtener_propiedades_agrupadas: Procesa datos de propiedades y retorna una lista
  con propiedades únicas y su año menor.
- obtener_datos: Retorna todos los formularios.
- obtener_formulario_unico: Retorna un formulario específico.
- borrar_datos: Borra todos los formularios de la tabla Formulario.
- ejecutar_algoritmo: Ejecuta un algoritmo con una lista de datos predefinida.
- agregar_formulario_a_base_de_datos: Agrega un nuevo formulario a la base de datos.
'''
from datetime import datetime
from flask import Blueprint, jsonify, request
from mysql.connector import Error  # type: ignore
from controladores.controlador_multipropietarios import ejecutar_algoritmo
from controladores.controlador_requests import (obtener_conexion_db)
from controladores.controlador_queries import (generar_query_obtener_ultimo_numero,
                                              generar_query_obtener_formularios,
                                              generar_query_obtener_formulario_unico,
                                              generar_query_borrar_formularios,
                                              generar_query_insertar_formularios)

controlador_formularios_bp = Blueprint('controlador_formularios', __name__)

def obtener_numero_de_atencion():
    '''Obtiene y retorna el número de atención incrementado en uno.'''
    ultimo_numero_atencion = obtener_ultimo_numero_atencion()
    nuevo_numero_atencion = incrementar_numero_atencion(ultimo_numero_atencion)
    return nuevo_numero_atencion

def ejecutar_query_ultimo_numero(query):
    '''Ejecuta una consulta SQL y retorna el resultado.'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def retornar_resultado_obtener_ultimo_numero():
    '''Obtiene el último número de atención desde la base de datos.'''
    query = generar_query_obtener_ultimo_numero()
    return ejecutar_query_ultimo_numero(query)


def obtener_ultimo_numero_atencion():
    '''Obtiene el último número de atención desde la base de datos.'''
    result = retornar_resultado_obtener_ultimo_numero()
    return int(result['numero_atencion']) if result else 0

def incrementar_numero_atencion(ultimo_numero_atencion):
    '''Incrementa el número de atención.'''
    return ultimo_numero_atencion + 2


def parsear_fecha(fecha):
    '''Intenta parsear una fecha en formato YYYYMMDD y retorna un objeto datetime.'''
    try:
        return datetime.strptime(fecha, '%Y%m%d')
    except ValueError:
        return None

def obtener_clave(propiedad):
    '''Obtiene y retorna la clave única de la propiedad.'''
    return (propiedad['comuna'], propiedad['manzana'], propiedad['predio'])

def actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion):
    '''Actualiza la fecha de inscripción mínima en unique_properties para la clave dada.'''
    current_fecha = unique_properties.get(key)

    if current_fecha is None or (fecha_inscripcion and fecha_inscripcion < current_fecha):
        unique_properties[key] = fecha_inscripcion

def convertir_a_lista_de_diccionarios(unique_properties):
    '''Convierte unique_properties en una lista de diccionarios con el formato requerido.'''
    resultado = []
    for (comuna, manzana, predio), fecha_inscripcion in unique_properties.items():
        entry = {'comuna': comuna, 'manzana': manzana, 'predio': predio}

        if fecha_inscripcion:
            entry['fecha_inscripcion'] = fecha_inscripcion.strftime('%Y')

        resultado.append(entry)

    return resultado

def obtener_propiedades_agrupadas(datos_propiedades):
    '''Recibe una lista de propiedades y retorna una lista con propiedades únicas y su año menor.'''
    unique_properties = {}

    for prop in datos_propiedades:
        key = obtener_clave(prop)
        fecha_inscripcion = prop.get('fecha_inscripcion')
        fecha_inscripcion = parsear_fecha(fecha_inscripcion)
        actualizar_fecha_inscripcion(unique_properties, key, fecha_inscripcion)

    return convertir_a_lista_de_diccionarios(unique_properties)


# CÓDIGO POR REFACTORIZAR
@controlador_formularios_bp.route('/', methods=['GET'])
def obtener_datos():
    '''Retorna todos los formularios agrupados por numero_atencion como JSON.'''
    try:
        conn = obtener_conexion_db()
        cursor = conn.cursor(dictionary=True)
        query = generar_query_obtener_formularios()
        cursor.execute(query)
        rows = cursor.fetchall()

        grouped_data = agrupar_formularios(rows)
        return jsonify(grouped_data)
    finally:
        cursor.close()
        conn.close()

def agrupar_formularios(rows):
    '''Agrupa los datos de formularios por numero_atencion.'''
    grouped_data = {}
    for row in rows:
        numero_atencion = row['numero_atencion']
        if numero_atencion not in grouped_data:
            grouped_data[numero_atencion] = {
                'numero_atencion': row['numero_atencion'],
                'cne': row['cne'],
                'comuna': row['comuna'],
                'fecha_inscripcion': row['fecha_inscripcion'],
                'fojas': row['fojas'],
                'herencia': row['herencia'],
                'id': row['id'],
                'manzana': row['manzana'],
                'numero_inscripcion': row['numero_inscripcion'],
                'predio': row['predio'],
                'status': row['status'],
                'adquirentes': [],
                'enajenantes': []
            }

        persona = {
            'RUNRUT': row['RUNRUT'],
            'derecho': row['derecho']
        }

        if row['tipo'] == 'adquirente':
            grouped_data[numero_atencion]['adquirentes'].append(persona)
        elif row['tipo'] == 'enajenante':
            grouped_data[numero_atencion]['enajenantes'].append(persona)

    return list(grouped_data.values())

@controlador_formularios_bp.route('/<numero_atencion>', methods=['GET'])
def obtener_formulario_unico(numero_atencion):
    '''Retorna un formulario específico por su número de atención.'''
    conn = obtener_conexion_db()
    cursor = conn.cursor(dictionary=True)

    try:
        query = generar_query_obtener_formulario_unico()
        cursor.execute(query, (numero_atencion,))
        rows = cursor.fetchall()
        return jsonify(rows)

    finally:
        cursor.close()
        conn.close()


@controlador_formularios_bp.route('/clean', methods=['GET'])
def borrar_datos():
    '''Borra todos los formularios de la tabla Formulario.'''
    query = generar_query_borrar_formularios()
    try:
        ejecutar_query_borrar_formularios(query)
        mensaje = {'mensaje': 'Datos borrados exitosamente'}
    except Error as e:
        mensaje = {'error': str(e)}
    return mensaje

def ejecutar_query_borrar_formularios (query):
    '''Ejecuta una consulta SQL y confirma la transacción.'''
    conn = obtener_conexion_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()



@controlador_formularios_bp.route('/crear', methods=['POST'])
def agregar_formulario_a_base_de_datos():
    '''Agrega los formularios a la tabla Formulario'''
    try:
        conn = obtener_conexion_db()
        cursor = conn.cursor()

        datos = request.json
        formularios = datos.get('F2890', [])
        numero_atencion = obtener_numero_de_atencion()

        propiedades_a_preprocesar = []

        for formulario in formularios:
            numero_atencion = agregar_datos_formulario(cursor, formulario,
                                                        numero_atencion, propiedades_a_preprocesar)
        conn.commit()
        propiedades_a_procesar = obtener_propiedades_agrupadas(propiedades_a_preprocesar)
        mensaje = {'mensaje': f'Datos agregados exitosamente.Propiedades: {propiedades_a_procesar}'}
    except Error as e:
        conn.rollback()
        mensaje = {'error': str(e)}
    finally:
        cursor.close()
        conn.close()
        for propiedad in revisar_propiedades(propiedades_a_procesar):
            ejecutar_algoritmo([propiedad])
    return jsonify(mensaje), 201

def revisar_propiedades(propiedades):
    '''Retorna un array con los datos de las propiedades revisadas.
    Revisa la integridad de los datos de las propiedades, en especifico
    que sean numericos'''
    propiedades_numericas = []
    for propiedad in propiedades:
        datos_numericos = True
        for _, value in propiedad.items():
            try:
                float_value = float(value)
                if isinstance(float_value, (int, float)):
                    continue
                else:
                    datos_numericos = False
                    break
            except ValueError:
                datos_numericos = False
                break
        if datos_numericos:
            propiedades_numericas.append(propiedad)
    return propiedades_numericas

def validar_datos_propiedad(bien_raiz):
    '''Valida los datos de la propiedad'''
    comuna = bien_raiz.get('comuna')
    manzana = bien_raiz.get('manzana')
    predio = bien_raiz.get('predio')

    if not str(manzana).isdigit() or not str(comuna).isdigit() or not str(predio).isdigit():
        return False
    return True

def insertar_persona(cursor, query, datos_persona):
    '''Inserta los datos de una persona en la base de datos'''
    cursor.execute(query, datos_persona)


def agregar_datos_formulario(cursor, formulario, numero_atencion, propiedades_a_preprocesar):
    '''Recibe la información de los formularios, los inserta en la base de 
    datos y retorna el numero de atención para el siguiente formulario.'''
    bien_raiz = obtener_datos_bien_raiz(formulario)
    status = determinar_estado_propiedad(bien_raiz)
    fecha_inscripcion = formatear_fecha_inscripcion(formulario.get('fechaInscripcion'))
    numero_inscripcion = formulario.get('nroInscripcion')
    cne = formulario.get('CNE')
    fojas = formulario.get('fojas')

    datos_propiedad = crear_datos_propiedad(bien_raiz, fecha_inscripcion)
    propiedades_a_preprocesar.append(datos_propiedad)

    procesar_personas_formulario(cursor, formulario, numero_atencion, cne, bien_raiz,
                                 fojas, fecha_inscripcion, numero_inscripcion, status)

    return numero_atencion + 1
def obtener_datos_bien_raiz(formulario):
    '''Obtiene los datos del bien raíz del formulario.'''
    return formulario.get('bienRaiz', {})

def determinar_estado_propiedad(bien_raiz):
    '''Determina el estado de la propiedad basado en los datos del bien raíz.'''
    return 'vigente' if validar_datos_propiedad(bien_raiz) else 'invalido'

def formatear_fecha_inscripcion(fecha_inscripcion):
    '''Formatea la fecha de inscripción.'''
    try:
        return datetime.strptime(fecha_inscripcion, '%Y-%m-%d').strftime('%Y%m%d')
    except ValueError:
        return '00000000'

def crear_datos_propiedad(bien_raiz, fecha_inscripcion):
    '''Crea un diccionario con los datos de la propiedad.'''
    return {
        'comuna': bien_raiz.get('comuna'),
        'manzana': bien_raiz.get('manzana'),
        'predio': bien_raiz.get('predio'),
        'fecha_inscripcion': fecha_inscripcion,
    }

def procesar_personas_formulario(cursor, formulario, numero_atencion, cne, bien_raiz,
                                 fojas, fecha_inscripcion, numero_inscripcion, status):
    '''Procesa y inserta las personas en la base de datos desde el formulario.'''
    for tipo, personas in [('enajenante', formulario.get('enajenantes', [])),
                           ('adquirente', formulario.get('adquirentes', []))]:
        for persona in personas:
            datos_persona = crear_datos_persona(numero_atencion, cne, bien_raiz, fojas,
                                                fecha_inscripcion, numero_inscripcion, tipo,
                                                persona, status)
            query = generar_query_insertar_formularios()
            insertar_persona(cursor, query, datos_persona)

def crear_datos_persona(numero_atencion, cne, bien_raiz, fojas, fecha_inscripcion,
                        numero_inscripcion, tipo, persona, status):
    '''Crea una tupla con los datos de la persona a insertar en la base de datos.'''
    herencia = 'n/a'  # valor inicial del campo herencia, para uso en caso de rectificación.
    return (
        numero_atencion, cne, bien_raiz.get('comuna'), bien_raiz.get('manzana'),
        bien_raiz.get('predio'), fojas, fecha_inscripcion, numero_inscripcion,
        tipo, persona.get('RUNRUT'), persona.get('porcDerecho'), status, herencia
    )
