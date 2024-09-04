import requests
from datetime import datetime
import telebot

# Diccionario para traducir los días de la semana al español
dias_semana = {
    "Monday": "Lunes",
    "Tuesday": "Martes",
    "Wednesday": "Miércoles",
    "Thursday": "Jueves",
    "Friday": "Viernes",
    "Saturday": "Sábado",
    "Sunday": "Domingo"
}

# Credenciales
api_key = 'eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJKNDk0OEBpY2xvdWQuY29tIiwianRpIjoiMDU4ZDJiNzAtNGJiNC00MWE2LTk1MzEtZmJmOWZhY2M5NmRjIiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3MTMyNDM4ODUsInVzZXJJZCI6IjA1OGQyYjcwLTRiYjQtNDFhNi05NTMxLWZiZjlmYWNjOTZkYyIsInJvbGUiOiIifQ.2QEECrTNbTmbBBo3hQCrI1sXu8Q8rHxUzT4q_-kfwxE'
telegram_token = '6659256025:AAFK3y_PbW3zhGzURyEc9v-7cZ1v9LwvNpc'
chat_id = ['317007077', '937187153']  # Reemplaza con tu chat ID

# URLs para las ciudades
urls = {
    'Bilbao': 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/48020',
    'Zamora': 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/49275',
    'Ayamonte': 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/21010',
    'Huelva': 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/21041',
    'Badajoz': 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/06015'
}

# Hacer la solicitud a la API para obtener las previsiones
def obtener_previsiones(api_key, url):
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        datos_url = response.json().get('datos', '')
        if datos_url:
            data_response = requests.get(datos_url)
            if data_response.status_code == 200:
                datos_prevision = data_response.json()
                return datos_prevision
            else:
                print(f'Error al recuperar los datos de previsión: {data_response.status_code}')
        else:
            print('No se encontró la URL de datos.')
    else:
        print(f'Error en la solicitud: {response.status_code}')

# Función para formatear los datos de previsión
def formatear_previsiones(previsiones, ciudad):
    mensaje = f"*Previsiones para {ciudad}*:\n"
    for dia in previsiones[0]['prediccion']['dia'][:3]:  # Limita a 3 días
        fecha = datetime.strptime(dia['fecha'], '%Y-%m-%dT%H:%M:%S')
        dia_semana_en = fecha.strftime('%A')
        dia_semana_es = dias_semana[dia_semana_en]
        dia_formateado = f"*{fecha.strftime('%B')}, día {fecha.strftime('%d')} ({dia_semana_es})*"

        estado_cielo = dia['estadoCielo'][0]['descripcion'].lower()
        if "despejado" in estado_cielo or "poco nuboso" in estado_cielo:
            emoji = "☀️"
        elif "cubierto" in estado_cielo or "muy nuboso" in estado_cielo or "nublado" in estado_cielo:
            emoji = "☁️"
        elif "lluvia" in estado_cielo or "chubascos" in estado_cielo:
            emoji = "🌧️"
        else:
            emoji = "⛅"

        # Añadir la información al mensaje
        mensaje += f"\n{dia_formateado} {emoji}\n"
        mensaje += f"  - *Estado del cielo:* {dia['estadoCielo'][0]['descripcion']}\n"
        mensaje += f"  - *Probabilidad de precipitación:* {dia['probPrecipitacion'][0]['value']}%\n"
        mensaje += f"  - *Temperatura máxima:* {dia['temperatura']['maxima']}°C\n"
        mensaje += f"  - *Temperatura mínima:* {dia['temperatura']['minima']}°C\n"
        mensaje += f"  - *Viento:* {dia['viento'][0]['direccion']} a {dia['viento'][0]['velocidad']} km/h\n"

    return mensaje

# Función para enviar las previsiones por Telegram
def enviar_por_telegram(mensaje, token, chat_id):
    bot = telebot.TeleBot(token)
    bot.send_message(chat_id, mensaje, parse_mode="Markdown")

# Ejecutar la función y enviar las previsiones por Telegram para cada ciudad
for ciudad, url in urls.items():
    previsiones = obtener_previsiones(api_key, url)
    if previsiones:
        mensaje = formatear_previsiones(previsiones, ciudad)
        enviar_por_telegram(mensaje, telegram_token, chat_id)
    else:
        print(f"No se pudieron obtener las previsiones para {ciudad}.")
