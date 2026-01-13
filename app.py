from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import os
from datetime import datetime
import base64

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

def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_canny_edge_detection(image_path, threshold1=100, threshold2=200):
    """
    Aplica el algoritmo Canny Edge Detection a una imagen
    
    Args:
        image_path: Ruta de la imagen
        threshold1: Umbral inferior para la detección de bordes
        threshold2: Umbral superior para la detección de bordes
    
    Returns:
        Tupla con (imagen_original, imagen_gris, imagen_bordes, imagen_comparativa)
    """
    # Cargar la imagen
    original_image = cv2.imread(image_path)
    
    if original_image is None:
        raise ValueError("No se pudo cargar la imagen")
    
    # Convertir a escala de grises
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)
    
    # Aplicar suavizado Gaussiano para reducir ruido
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 1.5)
    
    # Aplicar Canny Edge Detection
    edges = cv2.Canny(blurred_image, threshold1, threshold2)
    
    return original_image, gray_image, edges

def save_result_image(original_image, gray_image, edges, filename):
    """
    Guarda una imagen con la comparativa de la detección de bordes
    
    Args:
        original_image: Imagen original en BGR
        gray_image: Imagen en escala de grises
        edges: Imagen de bordes detectados
        filename: Nombre base del archivo de salida
    """
    # Build a 2x2 montage using OpenCV to avoid matplotlib GUI/backends issues
    try:
        print("🖼️ Generando imagen de resultado (OpenCV montage)...")
        # Ensure images are in RGB for consistent display
        orig_rgb = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)

        # Convert gray and edges to RGB
        gray_rgb = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2RGB)
        edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)

        # Create overlay (orig_rgb already RGB)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges_rgb_for_overlay = cv2.cvtColor(edges_bgr, cv2.COLOR_BGR2RGB)
        overlay = cv2.addWeighted(orig_rgb, 0.7, edges_rgb_for_overlay, 0.3, 0)

        # Resize all panels to the same size (use original image size)
        h, w = orig_rgb.shape[:2]
        target_size = (w, h)
        def to_target(img):
            if img.shape[0] == h and img.shape[1] == w:
                return img
            return cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)

        p1 = to_target(orig_rgb)
        p2 = to_target(gray_rgb)
        p3 = to_target(edges_rgb)
        p4 = to_target(overlay)

        # Stack into 2x2 grid
        top = np.hstack((p1, p2))
        bottom = np.hstack((p3, p4))
        montage = np.vstack((top, bottom))

        # Optionally add simple titles using OpenCV
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(montage, 'Original', (10, 30), font, 0.9, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(montage, 'Grayscale', (w+10, 30), font, 0.9, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(montage, 'Edges', (10, h+30), font, 0.9, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(montage, 'Overlay', (w+10, h+30), font, 0.9, (255,255,255), 2, cv2.LINE_AA)

        # Save as PNG (convert back to BGR for cv2.imwrite)
        result_bgr = cv2.cvtColor(montage, cv2.COLOR_RGB2BGR)
        result_path = os.path.join(RESULT_FOLDER, filename)
        print(f"💾 Guardando imagen de resultado en: {result_path}")
        cv2.imwrite(result_path, result_bgr)
        print("✓ Imagen de resultado guardada (OpenCV)")
        return result_path
    except Exception as ex:
        print(f"ERROR guardando imagen de resultado: {ex}")
        raise

def save_single_edge_image(edges, filename):
    """
    Guarda solo la imagen de bordes como PNG
    
    Args:
        edges: Imagen de bordes detectados
        filename: Nombre del archivo de salida
    """
    result_path = os.path.join(RESULT_FOLDER, filename)
    cv2.imwrite(result_path, edges)
    return result_path

def process_realtime_frame(frame_data, width, height, threshold1, threshold2):
    """
    Procesa un frame en tiempo real aplicando Canny Edge Detection
    
    Args:
        frame_data: Datos de la imagen en bytes
        width: Ancho del frame
        height: Alto del frame
        threshold1: Umbral inferior
        threshold2: Umbral superior
    
    Returns:
        Imagen de bordes en formato BGR
    """
    # Convertir bytes a array numpy
    frame_array = np.frombuffer(frame_data, dtype=np.uint8)
    # Decodificar la imagen
    frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise ValueError("No se pudo decodificar el frame")
    
    # Redimensionar si es necesario
    if frame.shape[0] != height or frame.shape[1] != width:
        frame = cv2.resize(frame, (width, height))
    
    # Convertir a escala de grises
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplicar suavizado Gaussiano
    blurred = cv2.GaussianBlur(gray, (5, 5), 1.5)
    
    # Aplicar Canny Edge Detection
    edges = cv2.Canny(blurred, threshold1, threshold2)
    
    # Convertir bordes a BGR para enviar como imagen
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    
    return edges_bgr


@app.route('/')
def index():
    """Ruta principal - muestra la interfaz"""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_image():
    """
    Endpoint para procesar una imagen
    Acepta: archivo de imagen, threshold1, threshold2
    """
    try:
        # Validar que se envió un archivo
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No se envió ningún archivo'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'El archivo está vacío'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Tipo de archivo no permitido. Use: PNG, JPG, JPEG, GIF, BMP'}), 400
        
        # Obtener los parámetros del umbral
        threshold1 = int(request.form.get('threshold1', 100))
        threshold2 = int(request.form.get('threshold2', 200))
        
        # Validar rangos
        if threshold1 < 0 or threshold2 < 0 or threshold1 >= threshold2:
            return jsonify({'success': False, 'message': 'Umbrales inválidos. threshold1 debe ser menor que threshold2'}), 400
        
        # Guardar el archivo subido
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        upload_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(upload_path)
        print(f"📁 Archivo guardado en: {upload_path}")
        # Procesar la imagen
        original_image, gray_image, edges = apply_canny_edge_detection(
            upload_path, 
            threshold1=threshold1, 
            threshold2=threshold2
        )
        print("✅ Imagen procesada con éxito")
        # Guardar resultados
        result_filename = filename.rsplit('.', 1)[0] + '_result.png'
        save_result_image(original_image, gray_image, edges, result_filename)
        print(f"💾 Resultado guardado en: {os.path.join(RESULT_FOLDER, result_filename)}")
        # Guardar imagen de bordes individual
        edges_filename = filename.rsplit('.', 1)[0] + '_edges.png'
        save_single_edge_image(edges, edges_filename)
        # Incluir visualización en base64 para mostrar inmediatamente en la UI
        try:
            with open(os.path.join(RESULT_FOLDER, result_filename), 'rb') as f:
                result_bytes = f.read()
            result_b64 = 'data:image/png;base64,' + base64.b64encode(result_bytes).decode('utf-8')
        except Exception:
            result_b64 = None
        try:
            with open(os.path.join(RESULT_FOLDER, edges_filename), 'rb') as f:
                edges_bytes = f.read()
            edges_b64 = 'data:image/png;base64,' + base64.b64encode(edges_bytes).decode('utf-8')
        except Exception:
            edges_b64 = None
        
        # Calcular estadísticas
        edge_percentage = (np.sum(edges > 0) / edges.size) * 100
        
        return jsonify({
            'success': True,
            'message': 'Imagen procesada correctamente',
            'original_image': os.path.join(UPLOAD_FOLDER, filename),
            'result_image': os.path.join(RESULT_FOLDER, result_filename),
            'edges_image': os.path.join(RESULT_FOLDER, edges_filename),
            'result_image_base64': result_b64,
            'edges_image_base64': edges_b64,
            'edge_percentage': round(edge_percentage, 2),
            'image_width': original_image.shape[1],
            'image_height': original_image.shape[0]
        }), 200
        
    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error procesando la imagen: {str(e)}'}), 500

@app.route('/api/process-url', methods=['POST'])
def process_url():
    """
    Endpoint alternativo para procesar una imagen desde URL
    """
    try:
        data = request.get_json()
        image_url = data.get('url')
        threshold1 = int(data.get('threshold1', 100))
        threshold2 = int(data.get('threshold2', 200))
        
        if not image_url:
            return jsonify({'success': False, 'message': 'URL no proporcionada'}), 400
        
        # Descargar la imagen
        import urllib.request
        with urllib.request.urlopen(image_url) as response:
            image_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("No se pudo descargar la imagen desde la URL")
        
        # Procesar imagen
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 1.5)
        edges = cv2.Canny(blurred_image, threshold1, threshold2)
        
        # Guardar resultados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_filename = f'url_result_{timestamp}.png'
        save_result_image(image, gray_image, edges, result_filename)
        
        edges_filename = f'url_edges_{timestamp}.png'
        save_single_edge_image(edges, edges_filename)
        
        edge_percentage = (np.sum(edges > 0) / edges.size) * 100
        # Incluir visualización en base64
        try:
            with open(os.path.join(RESULT_FOLDER, result_filename), 'rb') as f:
                result_bytes = f.read()
            result_b64 = 'data:image/png;base64,' + base64.b64encode(result_bytes).decode('utf-8')
        except Exception:
            result_b64 = None
        try:
            with open(os.path.join(RESULT_FOLDER, edges_filename), 'rb') as f:
                edges_bytes = f.read()
            edges_b64 = 'data:image/png;base64,' + base64.b64encode(edges_bytes).decode('utf-8')
        except Exception:
            edges_b64 = None
        
        return jsonify({
            'success': True,
            'result_image': os.path.join(RESULT_FOLDER, result_filename),
            'edges_image': os.path.join(RESULT_FOLDER, edges_filename),
            'result_image_base64': result_b64,
            'edges_image_base64': edges_b64,
            'edge_percentage': round(edge_percentage, 2),
            'image_width': image.shape[1],
            'image_height': image.shape[0]
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/process-realtime', methods=['POST'])
def process_realtime():
    """
    Endpoint para procesar frames en tiempo real de la webcam
    Acepta: frame (image data), width, height, threshold1, threshold2
    Retorna: imagen de bordes en base64
    """
    try:
        if 'frame' not in request.files:
            return jsonify({'success': False, 'message': 'No se envió ningún frame'}), 400
        
        frame_file = request.files['frame']
        width = int(request.form.get('width', 640))
        height = int(request.form.get('height', 480))
        threshold1 = int(request.form.get('threshold1', 100))
        threshold2 = int(request.form.get('threshold2', 200))
        
        # Leer datos del frame
        frame_data = frame_file.read()
        
        if not frame_data:
            return jsonify({'success': False, 'message': 'Frame vacío'}), 400
        
        # Procesar el frame
        edges_bgr = process_realtime_frame(frame_data, width, height, threshold1, threshold2)
        
        # Codificar como PNG y convertir a base64
        success, encoded = cv2.imencode('.png', edges_bgr)
        if not success:
            return jsonify({'success': False, 'message': 'Error codificando la imagen'}), 500
        
        # Convertir bytes a base64
        edges_base64 = 'data:image/png;base64,' + base64.b64encode(encoded).decode('utf-8')
        
        return jsonify({
            'success': True,
            'edges_data': edges_base64
        }), 200
        
    except Exception as e:
        print(f"Error en /api/process-realtime: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

@app.route('/api/info')
def info():
    """Endpoint para obtener información sobre el algoritmo"""
    return jsonify({
        'algorithm': 'Canny Edge Detection',
        'description': 'Algoritmo para detectar bordes en imágenes utilizando gradientes y supresión de no máximos',
        'steps': [
            '1. Suavizado Gaussiano para reducir ruido',
            '2. Cálculo del gradiente de la imagen',
            '3. Supresión de no máximos para adelgazar bordes',
            '4. Histéresis de umbral para conectar bordes'
        ],
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'threshold_ranges': {
            'threshold1': 'Umbral inferior (0-500)',
            'threshold2': 'Umbral superior (0-500)'
        }
    }), 200

@app.errorhandler(413)
def request_entity_too_large(error):
    """Manejo de archivos demasiado grandes"""
    return jsonify({'success': False, 'message': 'Archivo demasiado grande. Máximo 16 MB'}), 413

@app.errorhandler(404)
def not_found(error):
    """Manejo de rutas no encontradas"""
    return jsonify({'success': False, 'message': 'Ruta no encontrada'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos"""
    return jsonify({'success': False, 'message': 'Error interno del servidor'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
