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
comunas_dict_nombre_codigo = {}

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
        comunas_dict_nombre_codigo[nombre] = codigo
    comunas_dict = dict(sorted(comunas_dict.items(), key=lambda item: item[1]))
    # Imprimir el diccionario para verificar


def obtener_listado():
    try:
        # Hacer la solicitud a la API y obtener los datos
        response = requests.get(
            'https://fllask-proyect-yccm.vercel.app/tablas/tablas1')
        # Esto lanzará una excepción si la respuesta no es exitosa (código de estado diferente de 200)
        response.raise_for_status()
        data = response.json()["body"]
        for elemento in data:
            codigo_comuna = elemento.get("comuna")
            # Buscar el nombre de la comuna correspondiente al código de comuna
            nombre_comuna = comunas_dict.get(
                codigo_comuna, "No se encuentra el código")
            # Actualizar el valor de "codigo_comuna" por "nombre_comuna" en el elemento actual
            elemento["comuna"] = nombre_comuna
        data = sorted(data, key=lambda x: int(x['numero_atencion']))
        print(data)
        return data
    except requests.RequestException as e:
        # Manejar cualquier excepción de solicitud, como errores de conexión o tiempos de espera
        print("Error al hacer la solicitud a la API")
        return None  # Devolver None para indicar que hubo un error
    except ValueError as e:
        # Manejar excepciones al intentar analizar la respuesta JSON
        print("Error al analizar")


def obtener_multipropietario():
    try:
        # Hacer la solicitud a la API y obtener los datos
        response = requests.get(
            'https://fllask-proyect-yccm.vercel.app/tablas/tablas4')
        # Esto lanzará una excepción si la respuesta no es exitosa (código de estado diferente de 200)
        response.raise_for_status()
        json_data = json.loads(response.text)["body"]
        print(json_data)
        for elemento in json_data:
            # Eliminar 'T00:00:00.000Z' del final
            fecha_str = elemento['fecha_inscripcion'][:-5]
            fecha_datetime = datetime.fromisoformat(fecha_str)
            elemento['fecha_inscripcion'] = fecha_datetime
        if json_data == []:
            return "No se pudo cargar la tabla multiplropietario"
        return (json_data)
    except requests.RequestException as e:
        # Manejar cualquier excepción de solicitud, como errores de conexión o tiempos de espera
        print("Error al hacer la solicitud a la API")
        return None  # Devolver None para indicar que hubo un error
    except ValueError as e:
        # Manejar excepciones al intentar analizar la respuesta JSON
        print("Error al analizar")


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
    url = "http://fllask-proyect-yccm.vercel.app/formulario/crear"
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
    # Pasa los datos a la plantilla y renderiza la plantilla
    return render_template('index.html')


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


@app.route('/multipropietario')
def multipropietario():
    listado = obtener_multipropietario()
    print(listado)
    return render_template('multipropietario.html', resultados=listado)


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
            "ano": year
        }
        response = requests.post(
            "https://fllask-proyect-yccm.vercel.app/multipropietario/buscar", json=data)
        json_data = json.loads(response.text)
        for elemento in json_data:
            # Eliminar 'T00:00:00.000Z' del final
            fecha_str = elemento['fecha_inscripcion'][:-5]
            fecha_datetime = datetime.fromisoformat(fecha_str)
            elemento['fecha_inscripcion'] = fecha_datetime

        print(json_data)
        return render_template('busqueda.html', resultados=json_data, comunas_dict=comunas_dict)
    # Aquí puedes hacer lo que necesites con los parámetros obtenidos

    return render_template('busqueda.html')


if __name__ == '__main__':
    app.run()
