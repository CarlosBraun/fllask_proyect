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


@app.route('/submit_form', methods=['POST'])
def submit_form():
    # Obtener datos del formulario
    numero_atencion = request.form['numero_atencion']
    cne = request.form['cne']
    comuna = request.form['comuna']
    manzana = request.form['manzana']
    predio = request.form['predio']
    fojas = request.form['fojas']
    fecha_inscripcion = datetime.strptime(
        request.form['fecha_inscripcion'], '%Y-%m-%d')
    numero_inscripcion = request.form['numero_inscripcion']

    # Crear instancia del formulario
    formulario = Formulario(numero_atencion=numero_atencion, cne=cne, comuna=comuna, manzana=manzana,
                            predio=predio, fojas=fojas, fecha_inscripcion=fecha_inscripcion,
                            numero_inscripcion=numero_inscripcion)

    # Guardar formulario en la base de datos
    db.session.add(formulario)
    db.session.commit()

    # Guardar enajenantes
    for enajenante_data in request.form.getlist('enajenante'):
        runrut, porc_derecho = enajenante_data.split(',')
        enajenante = Enajenante(
            runrut=runrut, porc_derecho=porc_derecho, formulario_id=formulario.id)
        db.session.add(enajenante)

    # Guardar adquirentes
    for adquirente_data in request.form.getlist('adquirente'):
        runrut_adq, porc_derecho_adq = adquirente_data.split(',')
        adquirente = Adquirente(
            runrut_adq=runrut_adq, porc_derecho_adq=porc_derecho_adq, formulario_id=formulario.id)
        db.session.add(adquirente)

    db.session.commit()

    return redirect(url_for('index'))  # Redirigir a la página de inicio

# Ruta de inicio


@app.route('/')
def index():
    return render_template('index.html')

# Función para obtener los formularios


def obtener_formularios():
    return Formulario.query.all()


@app.route('/1')
def index2():
    return render_template('form1 copy.html')

# Ruta para mostrar el listado de formularios


@app.route('/listado')
def mostrar_listado():
    return render_template('listado.html')


@app.route('/listado1')
def mostrar_listado1():
    formularios = obtener_formularios()
    return render_template('listado.html', formularios=formularios)

# Ruta para mostrar los detalles de un formulario específico


@app.route('/detalle/<int:id>')
def mostrar_detalle(id):
    formulario = Formulario.query.get_or_404(id)
    return render_template('detalle.html', formulario=formulario)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
