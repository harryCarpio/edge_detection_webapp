"""
Módulo de procesamiento de imágenes y video
Contiene funciones para aplicar Canny Edge Detection a imágenes y frames
"""

import cv2
import numpy as np
import os
import base64
import urllib.request
from typing import Tuple

# Configuración de carpetas
RESULT_FOLDER = 'static/results'


def apply_canny_edge_detection(image_path: str, threshold1: int = 100, threshold2: int = 200, seed: int = 0) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Aplica el algoritmo Canny Edge Detection a una imagen
    
    Args:
        image_path: Ruta de la imagen
        threshold1: Umbral Bajo para la detección de bordes
        threshold2: Umbral Alto para la detección de bordes
        seed: Semilla para operaciones aleatorias (0 significa sin semilla)
    
    Returns:
        Tupla con (imagen_original, imagen_gris, imagen_bordes)
    """
    # Establecer semilla si es diferente de 0
    if seed > 0:
        np.random.seed(seed)
        cv2.setRNGSeed(seed)
    
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


def save_result_image(original_image: np.ndarray, gray_image: np.ndarray, edges: np.ndarray, filename: str) -> str:
    """
    Guarda una imagen con la comparativa de la detección de bordes
    
    Args:
        original_image: Imagen original en BGR
        gray_image: Imagen en escala de grises
        edges: Imagen de bordes detectados
        filename: Nombre base del archivo de salida
    
    Returns:
        Ruta del archivo guardado
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


def save_single_edge_image(edges: np.ndarray, filename: str) -> str:
    """
    Guarda solo la imagen de bordes como PNG
    
    Args:
        edges: Imagen de bordes detectados
        filename: Nombre del archivo de salida
    
    Returns:
        Ruta del archivo guardado
    """
    result_path = os.path.join(RESULT_FOLDER, filename)
    cv2.imwrite(result_path, edges)
    return result_path


def process_realtime_frame(frame_data: bytes, width: int, height: int, threshold1: int, threshold2: int) -> np.ndarray:
    """
    Procesa un frame en tiempo real aplicando Canny Edge Detection
    
    Args:
        frame_data: Datos de la imagen en bytes
        width: Ancho del frame
        height: Alto del frame
        threshold1: Umbral Bajo
        threshold2: Umbral Alto
    
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


def encode_image_to_base64(image_path: str) -> str:
    """
    Codifica una imagen a base64 para transmisión en JSON
    
    Args:
        image_path: Ruta de la imagen
    
    Returns:
        Imagen codificada en formato data URI
    """
    try:
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        return 'data:image/png;base64,' + base64.b64encode(image_bytes).decode('utf-8')
    except Exception:
        return None


def process_image_from_url(image_url: str, threshold1: int = 100, threshold2: int = 200) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Descarga y procesa una imagen desde una URL
    
    Args:
        image_url: URL de la imagen
        threshold1: Umbral Bajo para Canny
        threshold2: Umbral Alto para Canny
    
    Returns:
        Tupla con (imagen_original, imagen_gris, imagen_bordes)
    """
    # Descargar la imagen
    with urllib.request.urlopen(image_url) as response:
        image_array = np.asarray(bytearray(response.read()), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    if image is None:
        raise ValueError("No se pudo descargar la imagen desde la URL")
    
    # Procesar imagen
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 1.5)
    edges = cv2.Canny(blurred_image, threshold1, threshold2)
    
    return image, gray_image, edges


def calculate_edge_percentage(edges: np.ndarray) -> float:
    """
    Calcula el porcentaje de píxeles de borde detectados
    
    Args:
        edges: Imagen de bordes
    
    Returns:
        Porcentaje de bordes encontrados
    """
    return round((np.sum(edges > 0) / edges.size) * 100, 2)
