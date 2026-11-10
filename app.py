from flask import Flask
from database import init_db
from routes import register_routes

app = Flask(__name__)

# Inicializar base de datos y tablas
init_db()

# Registrar todas las rutas de la aplicación
register_routes(app)

if __name__ == '__main__':
    print("Iniciando Sistema Pocha (Modular)... Abre http://127.0.0.1:5000 en tu navegador.")
    app.run(host='0.0.0.0', port=5000, debug=True)