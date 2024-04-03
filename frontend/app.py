from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://g19:g19@localhost/bienes_raices'
db = SQLAlchemy(app)

# Definición de modelos


class Formulario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero_atencion = db.Column(db.String(255))
    cne = db.Column(db.Integer)
    comuna = db.Column(db.Integer)
    manzana = db.Column(db.Integer)
    predio = db.Column(db.Integer)
    fojas = db.Column(db.Integer)
    fecha_inscripcion = db.Column(db.Date)
    numero_inscripcion = db.Column(db.String(255))
    enajenantes = db.relationship(
        'Enajenante', backref='formulario', lazy=True)
    adquirentes = db.relationship(
        'Adquirente', backref='formulario', lazy=True)


class Enajenante(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    runrut = db.Column(db.String(255))
    porc_derecho = db.Column(db.Float)
    formulario_id = db.Column(db.Integer, db.ForeignKey(
        'formulario.id'), nullable=False)


class Adquirente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    runrut_adq = db.Column(db.String(255))
    porc_derecho_adq = db.Column(db.Float)
    formulario_id = db.Column(db.Integer, db.ForeignKey(
        'formulario.id'), nullable=False)

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
    app.run(debug=True, port=8000)
