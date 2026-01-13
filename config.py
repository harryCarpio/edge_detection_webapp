"""
Archivo de configuración para la aplicación Flask
Puedes modificar estos parámetros según tus necesidades
"""

import os

# ==================== CONFIGURACIÓN BÁSICA ====================
DEBUG = True                              # Modo debug (desactivar en producción)
SECRET_KEY = 'dev-secret-key-change-in-production'

# ==================== CONFIGURACIÓN DE CARPETAS ====================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
RESULT_FOLDER = os.path.join(BASE_DIR, 'static', 'results')

# ==================== CONFIGURACIÓN DE ARCHIVOS ====================
MAX_FILE_SIZE = 16 * 1024 * 1024          # Máximo tamaño de archivo: 16 MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}

# ==================== CONFIGURACIÓN DE CANNY ====================
DEFAULT_THRESHOLD1 = 100                  # Umbral inferior por defecto
DEFAULT_THRESHOLD2 = 200                  # Umbral superior por defecto
MIN_THRESHOLD = 0                         # Umbral mínimo permitido
MAX_THRESHOLD = 500                       # Umbral máximo permitido

# ==================== CONFIGURACIÓN DE KERNEL GAUSSIANO ====================
GAUSSIAN_KERNEL = (5, 5)                  # Tamaño del kernel
GAUSSIAN_SIGMA = 1.5                      # Sigma del kernel Gaussiano

# ==================== CONFIGURACIÓN DE FLASK SERVER ====================
SERVER_HOST = '0.0.0.0'                   # Host (0.0.0.0 = accesible desde cualquier IP)
SERVER_PORT = 5000                        # Puerto
THREADED = True                           # Ejecutar en modo multi-hilo

# ==================== CONFIGURACIÓN DE RESULTADOS ====================
RESULT_DPI = 100                          # DPI de las imágenes de resultado
RESULT_FORMAT = 'PNG'                     # Formato de las imágenes
OVERLAY_ALPHA = 0.3                       # Opacidad del overlay de bordes

# ==================== CONFIGURACIÓN DE LOGGING ====================
LOG_LEVEL = 'DEBUG'                       # Nivel de logging
LOG_FILE = 'app.log'                      # Archivo de log

# ==================== CONFIGURACIÓN DE SESIÓN ====================
SESSION_COOKIE_SECURE = False              # True para HTTPS
SESSION_COOKIE_HTTPONLY = True             # Proteger cookies
SESSION_COOKIE_SAMESITE = 'Lax'            # Prevenir CSRF

# ==================== VALORES PREDEFINIDOS DE UMBRALES ====================
PRESET_THRESHOLDS = {
    'bajo_ruido': {'threshold1': 50, 'threshold2': 150, 'description': 'Muy sensible, detecta muchos bordes'},
    'normal': {'threshold1': 100, 'threshold2': 200, 'description': 'Balance normal'},
    'alto_ruido': {'threshold1': 150, 'threshold2': 300, 'description': 'Menos sensible, detecta bordes principales'},
    'objetos_definidos': {'threshold1': 80, 'threshold2': 240, 'description': 'Buen balance para contornos claros'},
}

def init_app(app):
    """Inicializar la aplicación con la configuración"""
    # Crear carpetas si no existen
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(RESULT_FOLDER, exist_ok=True)
    
    # Aplicar configuración a la app
    app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['THREADED'] = THREADED
