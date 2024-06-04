from flask import Flask, jsonify
import mysql.connector
from config import DB_CONFIG, PORT_CONFIG
from controladores import create_app


app = create_app()


if __name__ == '__main__':
    app.run(debug=True, port=PORT_CONFIG['port'])
