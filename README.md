# BorderDetectionApp - Canny Edge Detection

![Flask](https://img.shields.io/badge/Flask-3.0.0-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

Una aplicación web desarrollada con Flask que implementa el **algoritmo Canny Edge Detection** de OpenCV para detectar y visualizar bordes en imágenes.

## 🎯 Características

- ✅ **Carga de imágenes**: Soporta PNG, JPG, JPEG, GIF, BMP
- ✅ **Conversión a escala de grises**: Procesamiento automático
- ✅ **Detección de bordes Canny**: Con parámetros ajustables
- ✅ **Visualización interactiva**: Interfaz web moderna y responsiva
- ✅ **Parámetros configurables**: Umbrales ajustables mediante sliders
- ✅ **Descarga de resultados**: Imágenes procesadas en alta calidad
- ✅ **Estadísticas**: Porcentaje de bordes detectados y dimensiones

## 🚀 Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| **Flask** | 3.0.0 | Framework web |
| **OpenCV** | 4.8.1 | Procesamiento de imágenes |
| **NumPy** | 2.4.1 | Operaciones numéricas |

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Navegador web moderno

## 🔧 Instalación

### 1. Clonar o descargar el repositorio

```bash
cd edge_detection_webapp
```

### 2. Crear un entorno virtual (opcional pero recomendado)

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 🏃 Ejecución

### Iniciar la aplicación

```bash
python app.py
```

### Acceder a la aplicación

Abre tu navegador web y ve a:
```
http://localhost:5000
```

## 📖 Cómo Usar

1. **Carga una imagen**: Haz clic en "Seleccionar Imagen" y elige un archivo de imagen
2. **Ajusta los parámetros**: 
   - **Umbral 1 (Inferior)**: Sensibilidad para detectar bordes débiles (0-500)
   - **Umbral 2 (Superior)**: Sensibilidad para detectar bordes fuertes (0-500)
3. **Procesa la imagen**: Haz clic en "Procesar Imagen"
4. **Visualiza los resultados**: Observa la comparativa en tiempo real
5. **Descarga**: Descarga la imagen con los bordes detectados

### Valores Recomendados de Umbrales

| Tipo de Imagen | Umbral 1 | Umbral 2 | Descripción |
|---|---|---|---|
| Imagen con poco ruido | 50 | 150 | Muy sensible, detecta muchos bordes |
| Imagen normal | 100 | 200 | Valores balanceados |
| Imagen con mucho ruido | 150 | 300 | Menos sensible, detecta bordes principales |
| Objetos definidos | 80 | 240 | Buen balance para contornos claros |

## 🧠 Algoritmo Canny Edge Detection

El algoritmo Canny es un detector de bordes multi-etapa ampliamente utilizado:

### Pasos del Algoritmo

1. **Suavizado Gaussiano**
   - Reduce el ruido de la imagen
   - Aplica un filtro Gaussiano 5x5

2. **Cálculo de Gradientes**
   - Calcula la magnitud y dirección del cambio de intensidad
   - Utiliza operadores Sobel

3. **Supresión de No Máximos**
   - Adelgaza los bordes detectados
   - Mantiene solo los máximos locales

4. **Histéresis de Umbral**
   - Usa dos umbrales para conectar bordes
   - Bordes fuertes se mantienen siempre
   - Bordes débiles se conectan a bordes fuertes

### Ventajas del Algoritmo Canny

✓ Baja tasa de error en la detección  
✓ Localización precisa de bordes  
✓ Respuesta única a bordes simples  
✓ Robustez ante ruido  

## 📁 Estructura del Proyecto

```
edge_detection_webapp/
│
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias de Python
├── README.md                       # Este archivo
│
├── templates/
│   └── index.html                  # Interfaz web HTML/CSS/JavaScript
│
└── static/
    ├── uploads/                    # Imágenes subidas
    └── results/                    # Resultados procesados
```

## 🔌 API Endpoints

### POST `/api/process`
Procesa una imagen con Canny Edge Detection

**Parámetros (multipart/form-data):**
- `file`: Archivo de imagen (requerido)
- `threshold1`: Umbral inferior (por defecto: 100)
- `threshold2`: Umbral superior (por defecto: 200)

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "original_image": "static/uploads/filename.jpg",
  "result_image": "static/results/filename_result.png",
  "edges_image": "static/results/filename_edges.png",
  "edge_percentage": 15.45,
  "image_width": 800,
  "image_height": 600
}
```

### POST `/api/process-url`
Procesa una imagen desde URL

**Body (JSON):**
```json
{
  "url": "https://ejemplo.com/imagen.jpg",
  "threshold1": 100,
  "threshold2": 200
}
```

### GET `/api/info`
Obtiene información sobre el algoritmo

## 🎨 Interfaz de Usuario

La aplicación incluye una interfaz moderna con:

- **Diseño responsivo**: Funciona en desktop, tablet y móvil
- **Tema visual gradiente**: Colores atractivos y profesionales
- **Sliders interactivos**: Ajuste en tiempo real de parámetros
- **Previsualizaciones**: Vista previa de la imagen original
- **Galería de resultados**: Visualización lado a lado
- **Estadísticas**: Información detallada del procesamiento

## ⚙️ Configuración

### Variables del Servidor

En `app.py` puedes modificar:

```python
UPLOAD_FOLDER = 'static/uploads'      # Carpeta de carga
RESULT_FOLDER = 'static/results'      # Carpeta de resultados
ALLOWED_EXTENSIONS = {...}             # Extensiones permitidas
MAX_FILE_SIZE = 16 * 1024 * 1024      # Tamaño máximo (16 MB)
```

### Ejecutar en Producción

**Usando Gunicorn:**

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Usando Waitress:**

```bash
pip install waitress
waitress-serve --port=5000 app:app
```

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'cv2'"
```bash
pip install opencv-python
```

### Error: "No se pudo cargar la imagen"
- Verifica que el archivo sea una imagen válida
- Comprueba el formato (PNG, JPG, JPEG, GIF, BMP)
- Asegúrate de que el archivo no esté corrupto

### La aplicación tarda mucho en procesar
- Reduce el tamaño de la imagen
- Ajusta los valores de umbral
- Verifica los recursos del sistema

### Errores de permisos en Windows
```bash
# Ejecuta como administrador o usa:
python -m flask run
```

## 📊 Ejemplos de Uso

### Detección de Contornos de Objetos
```
Umbral 1: 100
Umbral 2: 200
```

### Detección de Detalles Finos
```
Umbral 1: 50
Umbral 2: 150
```

### Reducción de Ruido
```
Umbral 1: 150
Umbral 2: 300
```

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## 👨‍💻 Autor

Desarrollado como práctica de Visión por Computadora en MIAA.

## 📚 Referencias

- [OpenCV Canny Documentation](https://docs.opencv.org/master/da/d22/tutorial_py_canny.html)
- [Canny Edge Detection - Wikipedia](https://en.wikipedia.org/wiki/Canny_edge_detector)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [NumPy Documentation](https://numpy.org/doc/)

---

**Nota**: Esta aplicación está diseñada con fines didácticos. Para usar en producción se debe considerar implementar:
- Autenticación y autorización
- Validación más estricta de archivos
- Límites de rate limiting
- Certificados SSL/TLS
- Logging y monitoreo avanzado
