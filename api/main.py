import os
import time
import bcrypt
import zxcvbn
from flask import Flask, request, jsonify, make_response # Ya no necesitamos render_template
from flask_cors import CORS

# --- Función para cargar el diccionario ---
def cargar_diccionario(ruta: str) -> set:
    """Carga palabras de un archivo de diccionario a un set respetando mayúsculas/minúsculas."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        ruta_abs = os.path.join(script_dir, ruta)
        print(f"ℹ️ Intentando cargar diccionario desde: {ruta_abs}")
        with open(ruta_abs, "r", encoding="utf-8") as f:
            diccionario_cargado = set(line.strip() for line in f if line.strip())
            if not diccionario_cargado:
                print(f"⚠️ Archivo de diccionario '{ruta_abs}' está vacío. Usando lista por defecto.")
                return {"123456", "password", "qwerty", "abc123", "letmein", "admin", "test", "usuario"}
            print(f"ℹ️ Diccionario cargado con {len(diccionario_cargado)} entradas únicas (respetando may/min).")
            return diccionario_cargado
    except FileNotFoundError:
        print(f"⚠️ Archivo de diccionario no encontrado en '{ruta_abs}'. Usando lista por defecto.")
        return {"123456", "password", "qwerty", "abc123", "letmein", "admin", "test", "usuario"}
    except Exception as e:
        print(f"🚨 Error al leer el diccionario '{ruta_abs}': {e}. Usando lista por defecto.")
        return {"123456", "password", "qwerty", "abc123", "letmein", "admin", "test", "usuario"}

DICCIONARIO_PATH = "lists/Diccionario.txt"
DICCIONARIO_COMUN = cargar_diccionario(DICCIONARIO_PATH)

# --- Crear la app Flask  ---
app = Flask(__name__)

# --- Configuración de CORS ---
origins = [
    "https://frontend-passafe-1fs04ks60-juanseds-projects.vercel.app",
    "https://frontend-passafe.vercel.app",
    "http://frontend-passafe-qbg3frajx-juanseds-projects.vercel.app",
    "http://localhost",
    "http://localhost:3000",
]
CORS(
    app,
    origins=origins,
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

# --- Funciones de Traducción ---
def traducir_sugerencias(suggestions):
    traducciones = { "Use a few words, avoid common phrases": "Usa algunas palabras, evita frases comunes", "No need for symbols, digits, or uppercase letters": "No necesitas símbolos, números ni letras mayúsculas", "Add another word or two. Uncommon words are better.": "Añade otra palabra o dos. Las palabras poco comunes son mejores.", "Straight rows of keys are easy to guess": "Las filas rectas de teclas son fáciles de adivinar", "Short keyboard patterns are easy to guess": "Los patrones cortos en el teclado son fáciles de adivinar", "Use a longer keyboard pattern with more turns": "Usa un patrón de teclado más largo con más giros", "Repeats like 'aaa' are easy to guess": "Las repeticiones como 'aaa' son fáciles de adivinar", "Repeats like 'abcabcabc' are only slightly harder to guess than 'abc'": "Las repeticiones como 'abcabcabc' son apenas un poco más difíciles de adivinar que 'abc'", "Avoid repeated words and characters": "Evita palabras y caracteres repetidos", "Sequences like abc or 6543 are easy to guess": "Las secuencias como 'abc' o '6543' son fáciles de adivinar", "Avoid sequences": "Evita secuencias", "Recent years are easy to guess": "Los años recientes son fáciles de adivinar", "Avoid recent years": "Evita los años recientes", "Avoid years that are associated with you": "Evita años que estén asociados contigo", "Dates are often easy to guess": "Las fechas suelen ser fáciles de adivinar", "Avoid dates and years that are associated with you": "Evita fechas y años asociados contigo", "This is a top-10 common password": "Esta es una de las 10 contraseñas más comunes", "This is a top-100 common password": "Esta es una de las 100 contraseñas más comunes", "This is a very common password": "Esta es una contraseña muy común", "This is similar to a common password": "Esto es similar a una contraseña común", "A word by itself is easy to guess": "Una palabra sola es fácil de adivinar", "Names and surnames by themselves are easy to guess": "Los nombres y apellidos solos son fáciles de adivinar", "Common names and surnames are easy to guess": "Los nombres y apellidos comunes son fáciles de adivinar", "Capitalization doesn't help very much": "Las mayúsculas no ayudan mucho", "All-uppercase is easy to guess": "Todo en mayúsculas es fácil de adivinar", "Reversed words aren't much harder to guess": "Las palabras al revés no son mucho más difíciles de adivinar", "Predictable substitutions like '@' instead of 'a' don't help very much": "Sustituciones predecibles como '@' en lugar de 'a' no ayudan mucho", "Straight or curved rows of keys are easy to guess": "Las filas rectas o curvas de teclas son fáciles de adivinar", "Predictable substitutions like '@' instead of 'a' don't help": "Las sustituciones predecibles como '@' en lugar de 'a' no ayudan", }
    if not suggestions: return []
    return [traducciones.get(s, s) for s in suggestions]

def traducir_crack_time(crack_time_str):
    traducciones = { "instant": "instantáneo", "less than a second": "menos de un segundo", "second": "segundo", "seconds": "segundos", "minute": "minuto", "minutes": "minutos", "hour": "hora", "hours": "horas", "day": "día", "days": "días", "month": "mes", "months": "meses", "year": "año", "years": "años", "century": "siglo", "centuries": "siglos", }
    lower_str = crack_time_str.lower()
    for key, value in traducciones.items():
        if key in lower_str: lower_str = lower_str.replace(key, value)
    return lower_str.capitalize()

# --- LÓGICA DE ANÁLISIS ---
def realizar_analisis(data):

    password_original = data.get("password", "")
    nombre = data.get("nombre", "")
    apellidos = data.get("apellidos", "")
    email = data.get("email", "")
    sexo = data.get("sexo")
    fecha_nacimiento = data.get("fecha_nacimiento", "")
    nombre_madre = data.get("nombre_madre")
    nombre_padre = data.get("nombre_padre")
    nombre_mascota = data.get("nombre_mascota")
    hobbies = data.get("hobbies")
    estudios = data.get("estudios")
    trabajo = data.get("trabajo")
    redes_sociales = data.get("redes_sociales")
    ciudad = data.get("ciudad")
    color_favorito = data.get("color_favorito")
    comida_favorita = data.get("comida_favorita")
    ataque_fuerza_bruta_flag = data.get("ataque_fuerza_bruta", 0)
    ataque_diccionario_flag = data.get("ataque_diccionario", 0)
    ataque_relleno_credenciales_flag = data.get("ataque_relleno_credenciales", 0)
    ataque_ingenieria_social_flag = data.get("ataque_ingenieria_social", 0)
    response = {}
    password_lower = password_original.lower()
    user_inputs = [ nombre, apellidos, email, sexo, fecha_nacimiento, nombre_madre, nombre_padre, nombre_mascota, hobbies, estudios, trabajo, redes_sociales, ciudad, color_favorito, comida_favorita ]
    user_inputs_filtered = [str(item).lower() for item in user_inputs if item and str(item).strip()]
    try:
        start_zxcvbn = time.time()
        resultado_zxcvbn = zxcvbn.zxcvbn(password_original, user_inputs=user_inputs_filtered)
        response["evaluacion_general_zxcvbn"] = { "descripcion": "Evaluación general de fortaleza y tiempo estimado de ruptura (offline, hashing lento)", "score": resultado_zxcvbn.get("score", -1), "crack_time_display": traducir_crack_time(resultado_zxcvbn.get("crack_times_display", {}).get("offline_slow_hashing_1e4_per_second", "N/A")), "feedback": { "warning": resultado_zxcvbn.get("feedback", {}).get("warning", ""), "suggestions": traducir_sugerencias(resultado_zxcvbn.get("feedback", {}).get("suggestions", [])) }, "tiempo_seg": round(time.time() - start_zxcvbn, 4) }
    except Exception as e: response["evaluacion_general_zxcvbn"] = {"error": f"No se pudo evaluar: {str(e)}"}

    # --- Ataque de Diccionario ---
    if ataque_diccionario_flag == 1:
        inicio = time.time()
        encontrada = password_original in DICCIONARIO_COMUN
        tiempo = round(time.time() - inicio, 4)
        response["ataque_diccionario_directo"] = { "descripcion": "Simula si la contraseña es una palabra común de diccionario (intento directo, sensible a may/min)", "vulnerable": encontrada, "mensaje": ("ALERTA: La contraseña fue encontrada directamente en el diccionario común (coincidencia exacta)." if encontrada else "La contraseña NO fue encontrada directamente en el diccionario común (coincidencia exacta)."), "tiempo_seg": tiempo }

    # --- Ataque de Ingeniería Social ---
    if ataque_ingenieria_social_flag == 1:
        inicio = time.time()
        vulnerable_is, detalles_is = False, []
        for dato in user_inputs_filtered:
            if dato and len(dato) > 2 and dato in password_lower:
                vulnerable_is, detalles_is = True, detalles_is + [f"Contiene: '{dato}'"]
        tiempo = round(time.time() - inicio, 4)
        response["ataque_ingenieria_social"] = { "descripcion": "Simula si la contraseña contiene información personal obvia (ignora may/min)", "vulnerable": vulnerable_is, "mensaje": ("ALERTA: La contraseña parece contener información personal obvia." if vulnerable_is else "La contraseña no parece contener información personal obvia."), "detalles_encontrados": list(set(detalles_is)), "tiempo_seg": tiempo }

    # --- Ataque de Fuerza Bruta ---
    if ataque_fuerza_bruta_flag == 1:
        start_fb_sim = time.time()
        hashed_password, encontrada_fb, password_encontrada_fb = None, False, ""
        intentos_fb, error_fb, tiempo_hash_fb, tiempo_check_fb = 0, None, 0, 0
        MAX_BRUTEFORCE_SIM_ATTEMPTS = 100
        try:
            start_hash = time.time()
            hashed_password = bcrypt.hashpw(password_original.encode('utf-8'), bcrypt.gensalt())
            tiempo_hash_fb = round(time.time() - start_hash, 4)
        except Exception as e: error_fb = f"Error generando hash: {str(e)}"
        if hashed_password and not error_fb:
            palabras_para_simulacion = list(DICCIONARIO_COMUN)[:MAX_BRUTEFORCE_SIM_ATTEMPTS]
            start_check = time.time()
            try:
                for guess_word in palabras_para_simulacion:
                    intentos_fb += 1
                    if bcrypt.checkpw(guess_word.encode('utf-8'), hashed_password):
                        encontrada_fb, password_encontrada_fb = True, guess_word
                        break
                tiempo_check_fb = round(time.time() - start_check, 4)
            except Exception as e: error_fb, encontrada_fb = f"Error comparando hash: {str(e)}", False
        tiempo_total_fb = round(time.time() - start_fb_sim, 4)
        resultado_fb = { "descripcion": "Simula romper el hash vs subconjunto diccionario (LIMITADO).", "tiempo_total_seg": tiempo_total_fb, "tiempo_generacion_hash_seg": tiempo_hash_fb if not error_fb else 0, "tiempo_simulacion_check_diccionario_seg": tiempo_check_fb if not error_fb else 0, "intentos_realizados_simulacion": intentos_fb, "tamano_subconjunto_diccionario_usado": len(palabras_para_simulacion), "tamano_diccionario_completo_disponible": len(DICCIONARIO_COMUN) }
        if error_fb: resultado_fb.update({"error": error_fb, "vulnerable": None, "mensaje": "Simulación falló por error."})
        elif encontrada_fb: resultado_fb.update({"vulnerable": True, "mensaje": f"ALERTA: SIMULACIÓN - ¡Hash roto! '{password_encontrada_fb}' encontrada.", "password_adivinada_diccionario": password_encontrada_fb})
        else: resultado_fb.update({"vulnerable": False, "mensaje": f"SIMULACIÓN - Resistente en {intentos_fb} intentos."})
        response["ataque_fuerza_bruta_simulada"] = resultado_fb

    # --- Ataque de Relleno de Credenciales---
    if ataque_relleno_credenciales_flag == 1:
        inicio_rc = time.time()
        encontrada_rc = password_original in DICCIONARIO_COMUN
        tiempo_rc = round(time.time() - inicio_rc, 4)
        response["ataque_relleno_credenciales_simulado"] = { "descripcion": "Simula si la contraseña es común y expuesta (coincidencia exacta)", "vulnerable": encontrada_rc, "mensaje": ("ALERTA: Contraseña común, vulnerable a Relleno Credenciales." if encontrada_rc else "Contraseña no común (según diccionario)."), "tiempo_seg": tiempo_rc }
    return response

# --- Función Auxiliar para Construir Respuesta OPTIONS ---
def _build_cors_preflight_response():
    response = make_response()
    origin = request.headers.get('Origin')
    if origin in origins:
        response.headers.add("Access-Control-Allow-Origin", origin)
    else:
        response.headers.add("Access-Control-Allow-Origin", origins[0] if origins else '*')
    response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
    response.headers.add('Access-Control-Allow-Methods', "GET,POST,OPTIONS")
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# --- RUTAS FLASK ---
@app.route('/simular_ataque', methods=['POST', 'OPTIONS'])
def simular_ataque_json():
    """Endpoint que devuelve los resultados en formato JSON."""
    print("ℹ️ Petición recibida en /simular_ataque")
    if request.method == 'OPTIONS':
        print("🟠 Respondiendo a OPTIONS en /simular_ataque")
        return _build_cors_preflight_response()

    if not request.is_json:
        print("🚨 Error: Petición no es JSON")
        return jsonify({"error": "La petición debe ser JSON"}), 400

    try:
        data = request.get_json()
        print("ℹ️ Realizando análisis...")
        resultados = realizar_analisis(data)
        print(f"✅ Petición JSON completada. Enviando {len(resultados)} resultados.")
        return jsonify(resultados)
    except Exception as e:
        print(f"🚨 ERROR INESPERADO en /simular_ataque: {e}")
        # En caso de un error muy grave, intentamos imprimirlo
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Ocurrió un error interno en el servidor."}), 500




@app.route('/')
def home():
    print("ℹ️ Petición recibida en /")
    return jsonify({"message": "Servidor Flask para Simulación de Seguridad (Solo JSON) está activo!"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    print(f"🚀 Iniciando servidor Flask localmente en http://{host}:{port}")
    app.run(host=host, port=port, debug=True)