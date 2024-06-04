# controladores/__init__.py
from flask import Flask
from controladores.controlador_formularios import controlador_formularios_bp
from controladores.controlador_multipropietarios import controlador_multipropietarios_bp
# from controladores.controlador2 import controlador2_bp


def create_app():
    app = Flask(__name__)

    # Registrar los blueprints
    app.register_blueprint(controlador_formularios_bp,
                           url_prefix='/formulario')
    app.register_blueprint(controlador_multipropietarios_bp,
                           url_prefix='/multipropietario')

    return app
