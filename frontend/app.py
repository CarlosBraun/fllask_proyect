from flask import Flask, render_template, request, redirect, url_for
import requests
from datetime import datetime

app = Flask(__name__)

# Cejemplo de llamada


def obtener_datos_de_api():
    # Hacer la solicitud a la API y obtener los datos
    response = requests.get('https://api.example.com/data')
    data = response.json()
    return data


@app.route('/')
def index():
    datos = obtener_datos_de_api()
    # Pasa los datos a la plantilla y renderiza la plantilla
    return render_template('index.html', datos=datos)


@app.route('/formulario')
def index2():
    return render_template('form.html')


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
