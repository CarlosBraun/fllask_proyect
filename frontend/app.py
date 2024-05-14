from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import requests
import json
from datetime import datetime

app = Flask(__name__)
app.debug = True
# Cejemplo de llamada

file_path = 'static/css/comunas.txt'

# Diccionario para almacenar los códigos y nombres de las comunas
comunas_dict = {}

# Leer el archivo de texto línea por línea
with open(file_path, 'r', encoding='utf-8') as file:
    next(file)
    for line in file:
        # Dividir la línea en partes usando el separador adecuado
        parts = line.split()
        # El código de la comuna será la primera parte
        codigo = parts[0]
        # El nombre de la comuna será el resto de las partes unidas
        nombre = ' '.join(parts[1:])
        # Agregar al diccionario
        comunas_dict[int(codigo)] = nombre

    # Imprimir el diccionario para verificar


@app.route('/submit_form_busqueda', methods=['POST'])
def submit_form_busqueda():
    # Obtener los datos del formulario
    comuna = request.form.get('comuna')
    manzana = request.form.get('manzana')
    predio = request.form.get('predio')
    year = request.form.get('year')
    if comuna is not None and manzana is not None and predio is not None and year is not None:
        # Redirigir a una URL con los parámetros en la query string
        return redirect(url_for('busqueda', comuna=comuna, manzana=manzana, predio=predio, year=year))
    else:
        # Al menos uno de los parámetros está ausente o es None
        # Manejar este caso según tus necesidades
        return "Faltan parámetros en el formulario", 400


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
    # URL a la que enviar el JSON mediante POST
    url = "https://fllask-proyect-yccm.vercel.app/formulario/crear"
    headers = {'Content-Type': 'application/json'}
    # Enviar el JSON como cuerpo de la solicitud POST a la URL especificada
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()  # Lanzar una excepción si la solicitud no es exitosa
        print('Archivo JSON enviado correctamente')
        return redirect(url_for('listado'))
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
    url = 'https://fllask-proyect-yccm.vercel.app/formulario/crear'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=json_data, headers=headers)

    # Retornar una respuesta apropiada
    if response.status_code == 200:
        print("Formulario enviado exitosamente")
        return redirect(url_for('listado'))
    else:
        print("Error al enviar el formulario"), 500
        return redirect(url_for('formulario'))


@app.route('/')
def index():
    datos = obtener_datos_de_api()
    # Pasa los datos a la plantilla y renderiza la plantilla
    return render_template('index.html', datos=datos)


@app.route('/formulario')
def index2():
    return render_template('form.html', comunas_dict=comunas_dict)


@app.route('/json')
def json1():
    return render_template('json.html')


@app.route('/listado')
def listado():
    listado = obtener_listado()
    return render_template('listado.html', listado=listado)


@app.route('/detalle')
def detalle():
    numero_atencion = request.args.get('numero_atencion')
    data = {
        "numero_atencion": numero_atencion
    }
    response = requests.post(
        "https://fllask-proyect-yccm.vercel.app/busqueda/formularioatencion", json=data)
    json_data = json.loads(response.text)
    comuna = json_data[0]["bienRaiz"]["comuna"]
    print(comunas_dict.keys())
    print(json_data[0]["bienRaiz"]["comuna"])
    # print(json_data[0])
    return render_template('detalle.html', data=json_data[0])


@app.route('/busqueda')
def busqueda():
    # Obtener los parámetros de la URL
    comuna = request.args.get('comuna')
    manzana = request.args.get('manzana')
    predio = request.args.get('predio')
    year = request.args.get('year')

    if comuna is not None and manzana is not None and predio is not None and year is not None:
        data = {
            "comuna": comuna,
            "manzana": manzana,
            "predio": predio,
            "year": year
        }
        response = requests.post(
            "https://fllask-proyect-yccm.vercel.app/busqueda/formularioCMP", json=data)
        json_data = json.loads(response.text)
        duplicated_data = []
        for item in json_data:
            # Por cada adquirente en el item, creamos un nuevo item
            for adquirente in item['adquirentes']:
                # Creamos una copia del item original
                new_item = item.copy()
                # Actualizamos la lista de adquirentes para tener solo el adquirente actual
                new_item['adquirentes'] = [adquirente]
                # Agregamos el nuevo item a la lista
                duplicated_data.append(new_item)
        print(duplicated_data)
        return render_template('busqueda.html', resultados=duplicated_data)
    # Aquí puedes hacer lo que necesites con los parámetros obtenidos

    return render_template('busqueda.html')


if __name__ == '__main__':
    app.run()
