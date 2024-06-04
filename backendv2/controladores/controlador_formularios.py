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
                    fecha_inscripcion, '%Y-%m-%d')
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
        [{'comuna': 77, 'manzana': 64, 'predio': 32, 'fecha_inscripcion': '2000'}, {'comuna': 77, 'manzana': 65, 'predio': 32, 'fecha_inscripcion': '2000'}])
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
            print(datetime.strptime(fecha_inscripcion,
                  '%Y-%m-%d').strftime('%Y%m%d'))
            datos_propiedad = {
                'comuna': comuna,
                'manzana': manzana,
                'predio': predio,
                'fecha_inscripcion': fecha_inscripcion,
            }
            propiedades_a_preprocesar.append(datos_propiedad)

            enajenantes = formulario.get('enajenantes', [])
            for enajenante in enajenantes:
                RUNRUT = enajenante.get('RUNRUT')
                derecho = enajenante.get('porcDerecho')
                cursor.execute('''INSERT INTO Formulario 
                                  (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion,
                                  numero_inscripcion, tipo, RUNRUT, derecho, status, herencia)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                               (numero_atencion, cne, comuna, manzana, predio, fojas, datetime.strptime(fecha_inscripcion, '%Y-%m-%d').strftime('%Y%m%d'),
                                numero_inscripcion, 'enajenante', RUNRUT, derecho, 'vigente', 'n/a'))

            adquirentes = formulario.get('adquirentes', [])
            for adquirente in adquirentes:
                RUNRUT = adquirente.get('RUNRUT')
                derecho = adquirente.get('porcDerecho')
                cursor.execute('''INSERT INTO Formulario 
                                  (numero_atencion, cne, comuna, manzana, predio, fojas, fecha_inscripcion,
                                  numero_inscripcion, tipo, RUNRUT, derecho, status, herencia)
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                               (numero_atencion, cne, comuna, manzana, predio, fojas, datetime.strptime(fecha_inscripcion, '%Y-%m-%d').strftime('%Y%m%d'),
                                numero_inscripcion, 'adquirente', RUNRUT, derecho, 'n/a', 'vigente'))
            numero_atencion = numero_atencion + 1
        conn.commit()  # Confirmar la transacción
        propiedades_a_procesar = preprocesamiento_de_datos(
            propiedades_a_preprocesar)
        # lunchear algoritmo
        algoritmo(propiedades_a_procesar)
        mensaje = {'mensaje': 'Datos agregados exitosamente'}
    except Exception as e:
        conn.rollback()  # Revertir la transacción en caso de error
        mensaje = {'error': str(e)}
    finally:
        cursor.close()
        conn.close()

    return jsonify(mensaje), 201
