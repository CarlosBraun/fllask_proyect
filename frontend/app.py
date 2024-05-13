from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# Cejemplo de llamada


def obtener_datos_de_api():
    try:
        # Hacer la solicitud a la API y obtener los datos
        response = requests.get('https://api.example.com/data')
        # Esto lanzará una excepción si la respuesta no es exitosa (código de estado diferente de 200)
        response.raise_for_status()
        data = response.json()
        print("lo hizo")
        return data
    except requests.RequestException as e:
        # Manejar cualquier excepción de solicitud, como errores de conexión o tiempos de espera
        print("Error al hacer la solicitud a la API")
        return None  # Devolver None para indicar que hubo un error
    except ValueError as e:
        # Manejar excepciones al intentar analizar la respuesta JSON
        print("Error al analizar")


def obtener_listado():
    try:
        # Hacer la solicitud a la API y obtener los datos
        response = requests.get('https://api.example.com/data')
        # Esto lanzará una excepción si la respuesta no es exitosa (código de estado diferente de 200)
        response.raise_for_status()
        data = response.json()
        print("lo hizo")
        return data
    except requests.RequestException as e:
        # Manejar cualquier excepción de solicitud, como errores de conexión o tiempos de espera
        print("Error al hacer la solicitud a la API")
        return None  # Devolver None para indicar que hubo un error
    except ValueError as e:
        # Manejar excepciones al intentar analizar la respuesta JSON
        print("Error al analizar")


def busqueda_ano():
    try:
        # Hacer la solicitud a la API y obtener los datos
        response = requests.get('https://api.example.com/data')
        # Esto lanzará una excepción si la respuesta no es exitosa (código de estado diferente de 200)
        response.raise_for_status()
        data = response.json()
        print("lo hizo")
        return data
    except requests.RequestException as e:
        # Manejar cualquier excepción de solicitud, como errores de conexión o tiempos de espera
        print("Error al hacer la solicitud a la API")
        return None  # Devolver None para indicar que hubo un error
    except ValueError as e:
        # Manejar excepciones al intentar analizar la respuesta JSON
        print("Error al analizar")


@app.route('/submit_json', methods=['POST'])
def submit_json():
    # Verificar si se recibió un archivo JSON
    if 'json_file' not in request.files:
        return jsonify({'error': 'No se recibió ningún archivo JSON'}), 400

    json_file = request.files['json_file']
    data = json.load(json_file)
    # Verificar si el archivo está vacío
    if json_file.filename == '':
        print("El archivo está vacío")
        # Redirigir al formulario de subida de JSON
        return redirect(url_for('json'))

    print(data)
    return data
    # URL a la que enviar el JSON mediante POST
    url = "https://fllask-proyect-yccm.vercel.app/formulario/crear"
    # Enviar el JSON como cuerpo de la solicitud POST a la URL especificada
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Lanzar una excepción si la solicitud no es exitosa
        print('Archivo JSON enviado correctamente')
        return redirect(url_for('json'))
    except requests.RequestException as e:
        print("Error al enviar el JSON:")
        return


@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Obtener los datos del formulario
    data = request.form.to_dict()

    # Procesar los datos y crear el JSON en el formato requerido
    json_data = {
        "F2890": [
            {
                "CNE": int(data.get("cne")),
                "_comment": "",
                "bienRaiz": {
                    "comuna": int(data.get("comuna")),
                    "manzana": int(data.get("manzana")),
                    "predio": int(data.get("predio"))
                },
                "enajenantes": [],
                "adquirentes": [],
                "fojas": int(data.get("fojas")),
                "fechaInscripcion": data.get("fecha_inscripcion"),
                "nroInscripcion": int(data.get("numero_inscripcion"))
            }
        ]
    }

    # Procesar enajenantes
    enajenantes_RUNRUT = request.form.getlist("enajenantes_RUNRUT[]")
    enajenantes_porcDerecho = request.form.getlist("enajenantes_porcDerecho[]")
    for i in range(len(enajenantes_RUNRUT)):
        json_data["F2890"][0]["enajenantes"].append({
            "RUNRUT": enajenantes_RUNRUT[i],
            "porcDerecho": int(enajenantes_porcDerecho[i])
        })

    # Procesar adquirentes
    adquirentes_RUNRUT = request.form.getlist("adquirentes_RUNRUT[]")
    adquirentes_porcDerecho = request.form.getlist("adquirentes_porcDerecho[]")
    for i in range(len(adquirentes_RUNRUT)):
        json_data["F2890"][0]["adquirentes"].append({
            "RUNRUT": adquirentes_RUNRUT[i],
            "porcDerecho": int(adquirentes_porcDerecho[i])
        })
    # Retornar una respuesta apropiada
    return json_data


@app.route('/')
def index():
    datos = obtener_datos_de_api()
    # Pasa los datos a la plantilla y renderiza la plantilla
    return render_template('index.html', datos=datos)


@app.route('/formulario')
def index2():
    return render_template('form.html')


@app.route('/json')
def json1():
    return render_template('json.html')


@app.route('/listado')
def listado():
    return render_template('listado.html')


@app.route('/detalle')
def detalle():
    return render_template('detalle.html')


@app.route('/busqueda')
def busqueda():
    return render_template('busqueda.html')


if __name__ == '__main__':
    app.run()
