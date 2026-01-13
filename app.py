from flask import Flask
import os

from routes import init_routes

app = Flask(__name__)

# Configuración
UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Crear carpetas si no existen
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# Inicializar rutas
init_routes(app, UPLOAD_FOLDER, RESULT_FOLDER, ALLOWED_EXTENSIONS)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

