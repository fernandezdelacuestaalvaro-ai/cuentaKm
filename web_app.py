from flask import Flask, redirect, request
from dotenv import load_dotenv

import os
import requests
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:5000/callback"

ACCESS_TOKEN = None
ruta_gps = []


@app.route("/")
def home():
    return """
    <h1>Cuenta KM GPS</h1>

    <p><a href="/strava/login">Conectar con Strava</a></p>
    <p><a href="/generar_ruta_prueba">Generar ruta GPS de prueba por Islandia</a></p>
    <p><a href="/generar_gpx">Generar GPX</a></p>
    <p><a href="/subir_strava">Subir actividad a Strava</a></p>
    <p><a href="/actividades">Ver actividades Strava</a></p>
    """


@app.route("/strava/login")
def strava_login():
    url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&approval_prompt=force"
        "&scope=read,activity:write,activity:read_all"
    )

    return redirect(url)


@app.route("/callback")
def callback():
    global ACCESS_TOKEN

    code = request.args.get("code")

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        }
    )

    data = response.json()
    ACCESS_TOKEN = data.get("access_token")

    atleta = data.get("athlete", {})
    nombre = atleta.get("firstname", "Usuario")

    return f"""
    <h1>STRAVA CONECTADO</h1>
    <p>Usuario: {nombre}</p>
    <p>Tu aplicación ya puede acceder a Strava.</p>
    <p><a href="/generar_ruta_prueba">Generar ruta Islandia</a></p>
    <p><a href="/actividades">Ver actividades</a></p>
    <p><a href="/">Volver</a></p>
    """


@app.route("/actividades")
def actividades():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        return """
        <h1>No conectado a Strava</h1>
        <a href='/strava/login'>Conectar</a>
        """

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=headers
    )

    actividades_strava = response.json()

    html = """
    <h1>Mis actividades Strava</h1>
    <hr>
    """

    for actividad in actividades_strava[:20]:
        nombre = actividad.get("name", "Sin nombre")
        tipo = actividad.get("type", "Actividad")
        distancia = actividad.get("distance", 0) / 1000
        tiempo = actividad.get("moving_time", 0) / 60
        fecha = actividad.get("start_date_local", "")

        html += f"""
        <div style="margin-bottom:20px;">
            <h3>{nombre}</h3>
            <p><b>Tipo:</b> {tipo}</p>
            <p><b>Distancia:</b> {distancia:.2f} km</p>
            <p><b>Tiempo:</b> {tiempo:.1f} min</p>
            <p><b>Fecha:</b> {fecha}</p>
            <hr>
        </div>
        """

    html += """
    <br>
    <a href="/">Volver</a>
    """

    return html


@app.route("/generar_ruta_prueba")
def generar_ruta_prueba():
    global ruta_gps

    ruta_gps = []

    ruta_islandia = [
        (64.1466, -21.9426),
        (64.1472, -21.9360),
        (64.1480, -21.9288),
        (64.1493, -21.9215),
        (64.1505, -21.9142),
        (64.1517, -21.9068),
        (64.1530, -21.8995),
        (64.1544, -21.8921),
        (64.1558, -21.8848),
        (64.1573, -21.8775),
        (64.1586, -21.8702),
        (64.1599, -21.8629),
        (64.1610, -21.8556),
        (64.1620, -21.8484),
        (64.1631, -21.8411),
        (64.1644, -21.8338),
        (64.1658, -21.8265),
        (64.1671, -21.8192),
        (64.1685, -21.8119),
        (64.1698, -21.8046),
        (64.1710, -21.7973),
        (64.1721, -21.7900),
        (64.1733, -21.7828),
        (64.1745, -21.7755),
        (64.1758, -21.7682),
        (64.1770, -21.7609),
        (64.1782, -21.7536),
        (64.1794, -21.7464),
        (64.1806, -21.7391),
        (64.1819, -21.7318),
        (64.1830, -21.7246),
        (64.1842, -21.7173),
        (64.1854, -21.7100),
        (64.1866, -21.7028),
        (64.1878, -21.6955),
        (64.1890, -21.6883),
        (64.1902, -21.6810),
        (64.1914, -21.6738),
        (64.1926, -21.6665),
        (64.1938, -21.6592),
        (64.1950, -21.6520),
        (64.1962, -21.6447),
        (64.1974, -21.6375),
        (64.1986, -21.6302),
        (64.1998, -21.6230),
        (64.2010, -21.6158),
        (64.2022, -21.6085),
        (64.2034, -21.6013),
        (64.2046, -21.5940),
        (64.2058, -21.5868),
        (64.2070, -21.5796),
        (64.2082, -21.5723),
        (64.2094, -21.5651),
        (64.2106, -21.5579),
        (64.2118, -21.5506),
        (64.2130, -21.5434),
        (64.2142, -21.5362),
        (64.2154, -21.5290),
        (64.2166, -21.5217),
        (64.2178, -21.5145),
    ]

    for lat, lon in ruta_islandia:
        ruta_gps.append({
            "lat": lat,
            "lon": lon
        })

    return """
    <h1>Ruta de prueba por Islandia generada</h1>
    <p>Se han generado 60 puntos GPS simulados cerca de Reikiavik.</p>
    <p><a href="/generar_gpx">Generar GPX</a></p>
    <p><a href="/subir_strava">Subir actividad a Strava</a></p>
    <p><a href="/">Volver</a></p>
    """


@app.route("/generar_gpx")
def generar_gpx():
    global ruta_gps

    if len(ruta_gps) < 2:
        return """
        <h1>No hay suficientes puntos GPS</h1>
        <p><a href='/generar_ruta_prueba'>Generar ruta de prueba por Islandia</a></p>
        """

    nombre_archivo = "ruta_cuenta_km_islandia.gpx"
    inicio = datetime.utcnow()

    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="CuentaKM">
<trk>
<name>Ruta Cuenta KM Islandia</name>
<trkseg>
""")

        for i, punto in enumerate(ruta_gps):
            lat = punto["lat"]
            lon = punto["lon"]
            tiempo = inicio + timedelta(seconds=i * 10)
            tiempo_str = tiempo.strftime("%Y-%m-%dT%H:%M:%SZ")

            f.write(f"""
<trkpt lat="{lat}" lon="{lon}">
<time>{tiempo_str}</time>
</trkpt>
""")

        f.write("""
</trkseg>
</trk>
</gpx>
""")

    return f"""
    <h1>GPX generado</h1>
    <p>Archivo creado: {nombre_archivo}</p>
    <p><a href="/subir_strava">Subir actividad a Strava</a></p>
    <p><a href="/">Volver</a></p>
    """


@app.route("/subir_strava")
def subir_strava():
    global ACCESS_TOKEN

    if not ACCESS_TOKEN:
        return """
        <h1>No conectado a Strava</h1>
        <a href='/strava/login'>Conectar</a>
        """

    nombre_archivo = "ruta_cuenta_km_islandia.gpx"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    with open(nombre_archivo, "rb") as fichero:
        files = {
            "file": fichero
        }

        data = {
            "data_type": "gpx",
            "name": "Ruta Cuenta KM Islandia",
            "description": "Ruta de prueba por Islandia subida desde Flask + Strava API",
            "sport_type": "Ride"
        }

        response = requests.post(
            "https://www.strava.com/api/v3/uploads",
            headers=headers,
            files=files,
            data=data
        )

    resultado = response.json()

    return f"""
    <h1>Actividad enviada a Strava</h1>
    <p>Strava procesará el archivo GPX en unos segundos.</p>
    <pre>{resultado}</pre>
    <p><a href="/actividades">Ver actividades</a></p>
    <p><a href="/">Volver</a></p>
    """


if __name__ == "__main__":
    app.run(debug=True)