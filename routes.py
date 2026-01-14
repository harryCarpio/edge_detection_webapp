"""
Rutas y endpoints de la aplicación Flask
"""

from flask import render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from datetime import datetime
import base64
import cv2

from image_processor import (
    apply_canny_edge_detection,
    save_result_image,
    save_single_edge_image,
    process_realtime_frame,
    encode_image_to_base64,
    process_image_from_url,
    calculate_edge_percentage
)

# Configuración (será usada desde app.py)
UPLOAD_FOLDER = None
RESULT_FOLDER = None
ALLOWED_EXTENSIONS = None
app = None


def init_routes(flask_app, upload_folder, result_folder, allowed_extensions):
    """Inicializa las rutas con la instancia de Flask y la configuración"""
    global app, UPLOAD_FOLDER, RESULT_FOLDER, ALLOWED_EXTENSIONS
    app = flask_app
    UPLOAD_FOLDER = upload_folder
    RESULT_FOLDER = result_folder
    ALLOWED_EXTENSIONS = allowed_extensions
    
    # Registrar todas las rutas
    register_routes()


def allowed_file(filename):
    """Verifica si la extensión del archivo es permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def register_routes():
    """Registra todas las rutas de la aplicación"""
    
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
            
            # Obtener los parámetros del umbral y semilla
            threshold1 = int(request.form.get('thresholdLow', 100))
            threshold2 = int(request.form.get('thresholdHigh', 200))
            seed = int(request.form.get('seed', 0))
            
            # Validar rangos
            if threshold1 < 0 or threshold2 < 0 or threshold1 >= threshold2:
                return jsonify({'success': False, 'message': 'Umbrales inválidos. Umbral Bajo debe ser menor que Umbral Alto'}), 400
            
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
                threshold2=threshold2,
                seed=seed
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
            result_b64 = encode_image_to_base64(os.path.join(RESULT_FOLDER, result_filename))
            edges_b64 = encode_image_to_base64(os.path.join(RESULT_FOLDER, edges_filename))
            
            # Calcular estadísticas
            edge_percentage = calculate_edge_percentage(edges)
            
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
            
            # Descargar y procesar la imagen
            image, gray_image, edges = process_image_from_url(image_url, threshold1, threshold2)
            
            # Guardar resultados
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            result_filename = f'url_result_{timestamp}.png'
            save_result_image(image, gray_image, edges, result_filename)
            
            edges_filename = f'url_edges_{timestamp}.png'
            save_single_edge_image(edges, edges_filename)
            
            edge_percentage = calculate_edge_percentage(edges)
            
            # Incluir visualización en base64
            result_b64 = encode_image_to_base64(os.path.join(RESULT_FOLDER, result_filename))
            edges_b64 = encode_image_to_base64(os.path.join(RESULT_FOLDER, edges_filename))
            
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
            threshold1 = int(request.form.get('thresholdLow', 100))
            threshold2 = int(request.form.get('thresholdHigh', 200))
            
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
