# controladores/controlador1.py
from flask import Blueprint, jsonify, request
import mysql.connector
from datetime import datetime
from config import DB_CONFIG
from controladores.controlador_multipropietarios import algoritmo
from controladores.controlador_requests import get_db_connection

controlador_formularios_bp = Blueprint('controlador_formularios', __name__)


def get_atention_number():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT numero_atencion FROM Formulario ORDER BY numero_atencion DESC LIMIT 1')
    result = cursor.fetchone()
    ultimo_numero_atencion = 0
    if result is not None:
        ultimo_numero_atencion = int(result['numero_atencion'])
    return ultimo_numero_atencion + 1


def preprocesamiento_de_datos(datos_propiedades):
    unique_properties = {}

    for prop in datos_propiedades:
        key = (prop['comuna'], prop['manzana'], prop['predio'])
        fecha_inscripcion = prop.get('fecha_inscripcion')

        if fecha_inscripcion:
            try:
                fecha_inscripcion = datetime.strptime(
                    fecha_inscripcion, '%Y%m%d')
            except ValueError:
                continue  # Ignorar fechas inválidas
        else:
            fecha_inscripcion = None

        if key not in unique_properties:
            unique_properties[key] = fecha_inscripcion
        else:
            current_fecha = unique_properties[key]
            if current_fecha is None or (fecha_inscripcion and fecha_inscripcion < current_fecha):
                unique_properties[key] = fecha_inscripcion

    # Convertir el diccionario de vuelta a una lista de diccionarios
    resultado = []
    for (comuna, manzana, predio), fecha_inscripcion in unique_properties.items():
        entry = {'comuna': comuna, 'manzana': manzana, 'predio': predio}

        if fecha_inscripcion:
            entry['fecha_inscripcion'] = fecha_inscripcion.strftime('%Y')

        resultado.append(entry)

    return resultado


@controlador_formularios_bp.route('/', methods=['GET'])
def obtener_datos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM Formulario')
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Diccionario para agrupar los datos por numero_atencion
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

        # Agregar a la lista de adquirentes o enajenantes según corresponda
        persona = {
            'RUNRUT': row['RUNRUT'],
            'derecho': row['derecho']
        }

        if row['tipo'] == 'adquirente':
            grouped_data[numero_atencion]['adquirentes'].append(persona)
        elif row['tipo'] == 'enajenante':
            grouped_data[numero_atencion]['enajenantes'].append(persona)

    # Convertir el diccionario a una lista para poder ser retornada como JSON
    response_data = list(grouped_data.values())
    return jsonify(response_data)


@controlador_formularios_bp.route('/<numero_atencion>', methods=['GET'])
def obtener_formulario_unico(numero_atencion):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = 'SELECT * FROM Formulario WHERE numero_atencion = %s'
    cursor.execute(query, (numero_atencion,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(rows)


@controlador_formularios_bp.route('/clean', methods=['GET'])
def borrar_datos():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM Formulario')
        conn.commit()  # Confirmar la transacción
        mensaje = {'mensaje': 'Datos borrados exitosamente'}
    except Exception as e:
        conn.rollback()  # Revertir la transacción en caso de error
        mensaje = {'error': str(e)}
    finally:
        cursor.close()
        conn.close()
    return jsonify(mensaje)


@controlador_formularios_bp.route('/algo', methods=['GET'])
def ejecutar_algoritmo():
    data1 = algoritmo(
        [{'comuna': 1101, 'manzana': 12, 'predio': 9, 'fecha_inscripcion': '2021'}])
    return jsonify(data1)


@controlador_formularios_bp.route('/crear', methods=['POST'])
def agregar_dato():
    datos = request.json
    formularios = datos.get('F2890', [])
    numero_atencion = get_atention_number()
    conn = get_db_connection()
    cursor = conn.cursor()
    propiedades_a_preprocesar = []
    propiedades_a_procesar = []

    try:
        for formulario in formularios:
            # Recuperar datos de cada formulario
            bien_raiz = formulario.get('bienRaiz', {})
            propiedades_a_preprocesar.append(bien_raiz)
            comuna = bien_raiz.get('comuna')
            manzana = bien_raiz.get('manzana')
            predio = bien_raiz.get('predio')
            cne = formulario.get('CNE')
            fojas = formulario.get('fojas')
            fecha_inscripcion = formulario.get('fechaInscripcion')
            numero_inscripcion = formulario.get('nroInscripcion')
            status = 'vigente'
            # Intentar convertir la fecha de inscripción
            try:
                fecha_inscripcion_formateada = datetime.strptime(
                    fecha_inscripcion, '%Y-%m-%d').strftime('%Y%m%d')
            except ValueError:
                fecha_inscripcion_formateada = '00000000'  # Fecha muy antigua
                status = 'invalido'

            if not str(manzana).isdigit() or not str(comuna).isdigit() or not str(predio).isdigit():
                status = 'invalido'

            datos_propiedad = {
                'comuna': comuna,
                'manzana': manzana,
                'predio': predio,
                'fecha_inscripcion': fecha_inscripcion_formateada,
            }
            print(datos_propiedad)
            propiedades_a_preprocesar.append(datos_propiedad)

            enajenantes = formulario.get('enajenantes', [])
            for enajenante in enajenantes:
                RUNRUT = enajenante.get('RUNRUT')
                derecho = enajenante.get('porcDerecho')
                cursor.execute('''INSERT INTO Formulario 
                                  (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion,
                                  numero_inscripcion, tipo, RUNRUT, derecho, status, herencia)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                               (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion_formateada,
                                numero_inscripcion, 'enajenante', RUNRUT, derecho, status, 'n/a'))

            adquirentes = formulario.get('adquirentes', [])
            for adquirente in adquirentes:
                RUNRUT = adquirente.get('RUNRUT')
                derecho = adquirente.get('porcDerecho')
                cursor.execute('''INSERT INTO Formulario 
                                  (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion,
                                  numero_inscripcion, tipo, RUNRUT, derecho, status, herencia)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                               (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion_formateada,
                                numero_inscripcion, 'adquirente', RUNRUT, derecho, status, 'n/a'))
            numero_atencion = numero_atencion + 1
        conn.commit()  # Confirmar la transacción
        propiedades_a_procesar = preprocesamiento_de_datos(
            propiedades_a_preprocesar)
        print(propiedades_a_procesar)
        # Llamada al algoritmo (comentada en este caso)
        # algoritmo(propiedades_a_procesar)
        mensaje = {
            'mensaje': 'Datos agregados exitosamente. Propiedades:' + str(propiedades_a_procesar)}
    except Exception as e:
        conn.rollback()  # Revertir la transacción en caso de error
        mensaje = {'error': str(e)}
    finally:
        cursor.close()
        conn.close()

    return jsonify(mensaje), 201
