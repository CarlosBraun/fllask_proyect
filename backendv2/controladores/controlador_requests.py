# controladores/controlador1.py
from flask import Blueprint, jsonify, request
import mysql.connector
from collections import defaultdict
from datetime import datetime
from config import DB_CONFIG
import json


controlador_requests_bp = Blueprint('controlador_formularios', __name__)


def get_db_connection():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn


def reagrupando_formularios(json_data):
    agrupados_por_comuna_manzana_predio = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: {
        'enajenantes': [],
        'adquirentes': []
    })))

    # Recorrer cada conjunto de formularios
    for formulario in json_data:
        for propiedad in formulario:
            comuna = propiedad['comuna']
            manzana = propiedad['manzana']
            predio = propiedad['predio']
            numero_inscripcion = propiedad['numero_inscripcion']
            tipo = propiedad['tipo']

            if tipo == 'enajenante':
                agrupados_por_comuna_manzana_predio[comuna][manzana][predio][numero_inscripcion]['enajenantes'].append({
                    'RUNRUT': propiedad['RUNRUT'],
                    'derecho': propiedad['derecho']
                })
            elif tipo == 'adquirente':
                agrupados_por_comuna_manzana_predio[comuna][manzana][predio][numero_inscripcion]['adquirentes'].append({
                    'RUNRUT': propiedad['RUNRUT'],
                    'derecho': propiedad['derecho']
                })
            # Copiar los demás datos necesarios
            for key, value in propiedad.items():
                if key not in ['RUNRUT', 'derecho', 'tipo']:
                    agrupados_por_comuna_manzana_predio[comuna][manzana][predio][numero_inscripcion][key] = value

    # Convertir el resultado en el formato deseado
    resultado_final = []
    for comuna, manzanas in agrupados_por_comuna_manzana_predio.items():
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
# En este archivo se finen las request a la bbdd, pero no se rutea.


def ordenar_json_por_claves_ascendente(data):
    # Función para comparar las claves y ordenarlas
    def comparar_claves(item):
        return sorted(item.keys())

    # Ordenar la lista de diccionarios por las claves ascendentes
    sorted_data = sorted(data, key=comparar_claves)

    # Convertir el resultado ordenado a JSON
    sorted_json = json.dumps(sorted_data, indent=4)

    return sorted_data


def request_algorithm_data(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    total_data = []
    for propiedades in data:
        query = """
        SELECT * 
        FROM Formulario
        WHERE comuna = %s
        AND manzana = %s
        AND predio = %s
        AND fecha_inscripcion >= %s
        ORDER BY fecha_inscripcion ASC
        """
        cursor.execute(query, (propiedades['comuna'], propiedades['manzana'],
                       propiedades['predio'], propiedades['fecha_inscripcion']))
        results = cursor.fetchall()
        total_data.append(results)
    cursor.close()
    conn.close()
    final_data = []
    for indice in range(len(data)):
        grouped_formularios = defaultdict(
            lambda: {'enajenantes': [], 'adquirentes': [], 'cne': formulario['cne'], 'fecha_inscripcion': formulario['fecha_inscripcion'], 'numero_atencion': formulario['numero_atencion'], 'fojas': formulario['fojas'], 'numero_inscripcion': formulario['numero_inscripcion'], 'status': formulario['status'], 'herencia': formulario['herencia']})
        for formulario in total_data[indice]:
            key = (formulario['fecha_inscripcion'])
            if formulario["tipo"] == "enajenante":
                grouped_formularios[key]['enajenantes'].append(
                    {'RUNRUT': formulario['RUNRUT'], 'derecho': formulario['derecho']})
            if formulario["tipo"] == "adquirente":
                grouped_formularios[key]['adquirentes'].append(
                    {'RUNRUT': formulario['RUNRUT'], 'derecho': formulario['derecho']})

        final_data.append(grouped_formularios)
    return [ordenar_json_por_claves_ascendente(final_data)]


def request_multipropietario_data(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    total_data = []
    for propiedades in data:
        query = """
        SELECT * 
        FROM Multipropietario
        WHERE comuna = %s
        AND manzana = %s
        AND predio = %s
        """
        cursor.execute(query, (propiedades['comuna'], propiedades['manzana'],
                       propiedades['predio']))
        results = cursor.fetchall()
        total_data.append(results)
    cursor.close()
    conn.close()
    return total_data


def revisar_multi():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
    DESCRIBE Multipropietario
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    print(results)
    return results


def limpiar_multipropietario(propiedad):
    ano_inicio = int(propiedad['fecha_inscripcion'][:4])
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    DELETE FROM Multipropietario
    WHERE comuna = %s
    AND manzana = %s
    AND predio = %s
    AND ano_inscripccion >= %s
    """

    cursor.execute(query, (
        propiedad['comuna'],
        propiedad['manzana'],
        propiedad['predio'],
        ano_inicio
    ))

    conn.commit()
    cursor.close()
    conn.close()


def ingresar_multipropietarios(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO Multipropietario (
        comuna, manzana, predio, run, derecho, fojas, fecha_inscripcion, 
        ano_inscripccion, numero_inscripcion, ano_vigencia_i, ano_vigencia_f, status
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for property in data:
        for row in property:
            print(row)
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
                row.get('ano_vigencia_f', None),  # Puede ser None
                row.get('status', None)  # Puede ser None
            ))
    conn.commit()
    cursor.close()
    return
