from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos

# Definición de modelos


# Ruta para manejar la solicitud POST del formulario


# Ruta de inicio


@app.route('/')
def index():
    return render_template('index.html')


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
