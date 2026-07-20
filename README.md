# Backend de Passafe - Simulador de Seguridad de Contraseñas

Este proyecto es el backend de la aplicación Passafe. Es una API construida con Flask (Python) diseñada para analizar la fortaleza de las contraseñas y simular varios tipos de ataques comunes. Proporciona una evaluación detallada para ayudar a los usuarios a comprender las vulnerabilidades de sus contraseñas.

Actualmente, esta API está diseñada para ser desplegada en Vercel y devuelve los resultados de los análisis en formato JSON.

## Características

* **Evaluación de Fortaleza:** Utiliza la biblioteca `zxcvbn` para una estimación robusta de la fortaleza de la contraseña, incluyendo el tiempo estimado para romperla y sugerencias de mejora (traducidas al español).
* **Simulación de Ataque de Diccionario:** Verifica si la contraseña se encuentra (con coincidencia exacta, sensible a mayúsculas/minúsculas) en un diccionario de contraseñas comunes.
* **Simulación de Ingeniería Social:** Comprueba si la contraseña contiene fragmentos de información personal proporcionada por el usuario (nombres, fechas, etc.).
* **Simulación de Fuerza Bruta (Limitada):** Realiza una demostración de un ataque offline, intentando romper un hash `bcrypt` de la contraseña contra un *subconjunto limitado* del diccionario.
* **Simulación de Relleno de Credenciales:** Evalúa si la contraseña es tan común que sería vulnerable a ataques de relleno de credenciales (basado en el diccionario).
* **API RESTful:** Expone los resultados a través de un endpoint JSON.
* **CORS Configurado:** Permite peticiones desde los frontends desplegados en Vercel y entornos locales.

## Stack Tecnológico

* **Lenguaje:** Python 3.x
* **Framework:** Flask
* **Hashing:** bcrypt
* **Análisis de Fortaleza:** zxcvbn-python
* **CORS:** Flask-CORS
* **Despliegue:** Vercel

## API Endpoints

### `GET /`

* **Descripción:** Endpoint básico para verificar si el servidor está activo.
* **Respuesta (Éxito):**
    ```json
    {
      "message": "Servidor Flask para Simulación de Seguridad (Solo JSON) está activo!"
    }
    ```

### `POST /simular_ataque`

* **Descripción:** Recibe la contraseña y datos opcionales para realizar todos los análisis seleccionados.
* **Formato Petición (JSON):**
    ```json
    {
      "password": "mi_contraseña_secreta",
      "nombre": "Juan",
      "apellidos": "Perez",
      "email": "juan@example.com",
      "fecha_nacimiento": "1990-05-15",
      // ... otros datos personales ...
      "ataque_fuerza_bruta": 1, // 1 para activar, 0 para desactivar
      "ataque_diccionario": 1,
      "ataque_relleno_credenciales": 1,
      "ataque_ingenieria_social": 1
    }
    ```
* **Respuesta (Éxito - JSON):** Un objeto JSON que contiene los resultados detallados de cada análisis solicitado. La estructura exacta varía según los análisis activados. Ejemplo parcial:
    ```json
    {
      "evaluacion_general_zxcvbn": {
        "descripcion": "Evaluación general...",
        "score": 3,
        "crack_time_display": "1 siglo",
        "feedback": {
          "warning": "",
          "suggestions": ["Añade otra palabra o dos..."]
        },
        "tiempo_seg": 0.0123
      },
      "ataque_diccionario_directo": {
        "descripcion": "Simula si la contraseña...",
        "vulnerable": false,
        "mensaje": "La contraseña NO fue encontrada...",
        "tiempo_seg": 0.0001
      }
      // ... otros resultados ...
    }
    ```

## Configuración y Estructura

* **`api/main.py`**: Contiene el código principal de la aplicación Flask.
* **`requirements.txt`**: Lista las dependencias de Python. Debe estar en la raíz del proyecto.
* **`vercel.json`**: Archivo de configuración para el despliegue en Vercel. Debe estar en la raíz.
* **`api/lists/Diccionario.txt`**: Este archivo (que debes crear o proporcionar) contiene la lista de contraseñas comunes, una por línea. Si no se encuentra, se usará una lista interna muy pequeña.

## Instalación y Ejecución Local

1.  **Clonar el Repositorio:**
    ```bash
    git clone <url_del_repositorio>
    cd Backed_passefe
    ```
2.  **Crear y Activar Entorno Virtual:**
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\activate
    # macOS/Linux:
    source .venv/bin/activate
    ```
3.  **Instalar Dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Crear Diccionario (Opcional):**
    Crea la carpeta `api/lists/` y dentro un archivo `Diccionario.txt` con tus contraseñas comunes, una por línea.
5.  **Ejecutar:**
    ```bash
    python api/main.py
    ```
    El servidor se ejecutará localmente (normalmente en `http://0.0.0.0:8000`).

## Despliegue en Vercel

1.  Asegúrate de tener `vercel.json` y `requirements.txt` en la **raíz** de tu proyecto.
2.  Asegúrate de que `api/main.py` y `api/lists/Diccionario.txt` estén en sus ubicaciones correctas.
3.  Conecta tu repositorio a Vercel.
4.  Vercel debería detectar la configuración (`vercel.json`) y desplegar la aplicación automáticamente.
5.  **Importante:** La generación de PDF **no** se realiza en este backend. Se ha movido al frontend usando `jsPDF` para evitar problemas de dependencias en Vercel.

---
