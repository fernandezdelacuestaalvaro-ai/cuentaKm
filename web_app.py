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
nombre_actividad_actual = "Actividad Cuenta KM GPS"
tipo_actividad_actual = "Ride"
archivo_gpx_actual = "ruta_cuenta_km.gpx"


@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Cuenta KM GPS</title>
        <style>
            body {
                background: black;
                color: white;
                font-family: Arial;
                padding: 20px;
            }

            h1 {
                color: #00bcd4;
            }

            h2 {
                color: #00bcd4;
                margin-top: 30px;
            }

            .panel {
                background: #111;
                padding: 20px;
                border-radius: 10px;
                max-width: 750px;
                margin-top: 20px;
            }

            .dato {
                font-size: 26px;
                color: #00bcd4;
                font-weight: bold;
            }

            button {
                padding: 14px;
                margin-top: 10px;
                margin-right: 10px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 17px;
            }

            .start {
                background: green;
                color: white;
            }

            .stop {
                background: red;
                color: white;
            }

            a {
                color: #00bcd4;
                display: block;
                margin-top: 12px;
                font-size: 17px;
            }
        </style>
    </head>

    <body>
        <h1>Cuenta KM GPS</h1>

        <div class="panel">
            <h2>GPS real</h2>

            <p>Latitud: <span class="dato" id="lat">---</span></p>
            <p>Longitud: <span class="dato" id="lon">---</span></p>
            <p>Velocidad: <span class="dato" id="velocidad">0.00</span> km/h</p>
            <p>Distancia: <span class="dato" id="distancia">0.000</span> km</p>

            <button class="start" onclick="iniciarGPS()">Iniciar GPS</button>
            <button class="stop" onclick="pararGPS()">Parar GPS</button>
        </div>

        <div class="panel">
            <h2>Strava</h2>
            <a href="/strava/login">Conectar con Strava</a>
            <a href="/actividades">Ver actividades Strava</a>
            <a href="/generar_gpx">Generar GPX de la ruta actual</a>
            <a href="/subir_strava">Subir actividad actual a Strava</a>
        </div>

        <div class="panel">
            <h2>Simulaciones</h2>
            <a href="/simular/reikiavik">Simular carrera por Reikiavik, Islandia</a>
            <a href="/simular/reynisfjara">Simular natación en playa negra de Reynisfjara, Islandia</a>
            <a href="/simular/colonia">Simular media maratón en Colonia, Alemania</a>
        </div>

        <script>
            let watchId = null;
            let ultimaLat = null;
            let ultimaLon = null;
            let distanciaTotal = 0;

            function calcularDistancia(lat1, lon1, lat2, lon2) {
                const R = 6371;
                const dLat = (lat2 - lat1) * Math.PI / 180;
                const dLon = (lon2 - lon1) * Math.PI / 180;

                const a =
                    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                    Math.cos(lat1 * Math.PI / 180) *
                    Math.cos(lat2 * Math.PI / 180) *
                    Math.sin(dLon / 2) *
                    Math.sin(dLon / 2);

                const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
                return R * c;
            }

            function iniciarGPS() {
                if (!navigator.geolocation) {
                    alert("GPS no soportado");
                    return;
                }

                watchId = navigator.geolocation.watchPosition(
                    function(posicion) {
                        const lat = posicion.coords.latitude;
                        const lon = posicion.coords.longitude;

                        let velocidad = posicion.coords.speed;
                        if (velocidad == null) {
                            velocidad = 0;
                        }

                        velocidad = velocidad * 3.6;

                        document.getElementById("lat").innerHTML = lat.toFixed(6);
                        document.getElementById("lon").innerHTML = lon.toFixed(6);
                        document.getElementById("velocidad").innerHTML = velocidad.toFixed(2);

                        if (ultimaLat != null) {
                            distanciaTotal += calcularDistancia(
                                ultimaLat,
                                ultimaLon,
                                lat,
                                lon
                            );
                        }

                        ultimaLat = lat;
                        ultimaLon = lon;

                        document.getElementById("distancia").innerHTML =
                            distanciaTotal.toFixed(3);

                        fetch("/gps", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                latitud: lat,
                                longitud: lon,
                                velocidad: velocidad,
                                distancia_total: distanciaTotal
                            })
                        });
                    },
                    function(error) {
                        alert("Error GPS: " + error.message);
                    },
                    {
                        enableHighAccuracy: true,
                        maximumAge: 0,
                        timeout: 10000
                    }
                );
            }

            function pararGPS() {
                if (watchId != null) {
                    navigator.geolocation.clearWatch(watchId);
                    watchId = null;
                    alert("GPS detenido");
                }
            }
        </script>
    </body>
    </html>
    """


@app.route("/gps", methods=["POST"])
def recibir_gps():
    global ruta_gps
    global nombre_actividad_actual
    global tipo_actividad_actual
    global archivo_gpx_actual

    datos = request.get_json()

    latitud = datos.get("latitud")
    longitud = datos.get("longitud")

    nombre_actividad_actual = "Ruta GPS real Cuenta KM"
    tipo_actividad_actual = "Run"
    archivo_gpx_actual = "ruta_gps_real.gpx"

    if latitud is not None and longitud is not None:
        ruta_gps.append({
            "lat": latitud,
            "lon": longitud
        })

    return {"ok": True, "puntos": len(ruta_gps)}


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
    <p><a href="/actividades">Ver actividades</a></p>
    <p><a href="/">Volver</a></p>
    """


@app.route("/actividades")
def actividades():
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

    html = "<h1>Mis actividades Strava</h1><hr>"

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

    html += '<p><a href="/">Volver</a></p>'
    return html


@app.route("/simular/reikiavik")
def simular_reikiavik():
    global ruta_gps
    global nombre_actividad_actual
    global tipo_actividad_actual
    global archivo_gpx_actual

    nombre_actividad_actual = "Carrera por Reikiavik - Cuenta KM GPS"
    tipo_actividad_actual = "Run"
    archivo_gpx_actual = "ruta_reikiavik.gpx"

    ruta_gps = [
        {"lat": 64.146600, "lon": -21.942600},
        {"lat": 64.146850, "lon": -21.941000},
        {"lat": 64.147100, "lon": -21.939300},
        {"lat": 64.147350, "lon": -21.937700},
        {"lat": 64.147700, "lon": -21.936100},
        {"lat": 64.148100, "lon": -21.934500},
        {"lat": 64.148500, "lon": -21.932900},
        {"lat": 64.148850, "lon": -21.931200},
        {"lat": 64.149100, "lon": -21.929500},
        {"lat": 64.149400, "lon": -21.927900},
        {"lat": 64.149750, "lon": -21.926200},
        {"lat": 64.150100, "lon": -21.924600},
        {"lat": 64.150500, "lon": -21.923000},
        {"lat": 64.150900, "lon": -21.921500},
        {"lat": 64.151300, "lon": -21.920000},
        {"lat": 64.151700, "lon": -21.918400},
        {"lat": 64.152000, "lon": -21.916800},
        {"lat": 64.152300, "lon": -21.915200},
        {"lat": 64.152600, "lon": -21.913600},
        {"lat": 64.152900, "lon": -21.912000},
        {"lat": 64.153200, "lon": -21.910400},
        {"lat": 64.153500, "lon": -21.908800},
        {"lat": 64.153800, "lon": -21.907200},
        {"lat": 64.154100, "lon": -21.905600},
        {"lat": 64.154400, "lon": -21.904000},
        {"lat": 64.154700, "lon": -21.902400},
        {"lat": 64.155000, "lon": -21.900800},
        {"lat": 64.155300, "lon": -21.899200},
        {"lat": 64.155600, "lon": -21.897600},
        {"lat": 64.155900, "lon": -21.896000},
        {"lat": 64.156200, "lon": -21.894400},
        {"lat": 64.156500, "lon": -21.892800},
        {"lat": 64.156800, "lon": -21.891200},
        {"lat": 64.157100, "lon": -21.889600},
        {"lat": 64.157400, "lon": -21.888000},
        {"lat": 64.157700, "lon": -21.886400},
        {"lat": 64.158000, "lon": -21.884800},
        {"lat": 64.158300, "lon": -21.883200},
        {"lat": 64.158600, "lon": -21.881600},
        {"lat": 64.158900, "lon": -21.880000},
    ]

    return pagina_simulacion_generada("Carrera por Reikiavik generada", "Run")


@app.route("/simular/reynisfjara")
def simular_reynisfjara():
    global ruta_gps
    global nombre_actividad_actual
    global tipo_actividad_actual
    global archivo_gpx_actual

    nombre_actividad_actual = "Natación en Reynisfjara - Cuenta KM GPS"
    tipo_actividad_actual = "Swim"
    archivo_gpx_actual = "ruta_reynisfjara_swim.gpx"

    ruta_gps = [
        {"lat": 63.404500, "lon": -19.044900},
        {"lat": 63.404300, "lon": -19.043900},
        {"lat": 63.404100, "lon": -19.042900},
        {"lat": 63.403900, "lon": -19.041900},
        {"lat": 63.403700, "lon": -19.040900},
        {"lat": 63.403500, "lon": -19.039900},
        {"lat": 63.403300, "lon": -19.038900},
        {"lat": 63.403100, "lon": -19.037900},
        {"lat": 63.402900, "lon": -19.036900},
        {"lat": 63.402700, "lon": -19.035900},
        {"lat": 63.402500, "lon": -19.034900},
        {"lat": 63.402300, "lon": -19.033900},
        {"lat": 63.402100, "lon": -19.032900},
        {"lat": 63.401900, "lon": -19.031900},
        {"lat": 63.401700, "lon": -19.030900},
        {"lat": 63.401500, "lon": -19.029900},
        {"lat": 63.401300, "lon": -19.028900},
        {"lat": 63.401100, "lon": -19.027900},
        {"lat": 63.400900, "lon": -19.026900},
        {"lat": 63.400700, "lon": -19.025900},
        {"lat": 63.400500, "lon": -19.024900},
        {"lat": 63.400300, "lon": -19.023900},
        {"lat": 63.400100, "lon": -19.022900},
        {"lat": 63.399900, "lon": -19.021900},
        {"lat": 63.399700, "lon": -19.020900},
        {"lat": 63.399500, "lon": -19.019900},
        {"lat": 63.399300, "lon": -19.018900},
        {"lat": 63.399100, "lon": -19.017900},
        {"lat": 63.398900, "lon": -19.016900},
        {"lat": 63.398700, "lon": -19.015900},
    ]

    return pagina_simulacion_generada("Natación por Reynisfjara generada", "Swim")


@app.route("/simular/colonia")
def simular_colonia():
    global ruta_gps
    global nombre_actividad_actual
    global tipo_actividad_actual
    global archivo_gpx_actual

    nombre_actividad_actual = "Media maratón en Colonia - Cuenta KM GPS"
    tipo_actividad_actual = "Run"
    archivo_gpx_actual = "ruta_media_maraton_colonia.gpx"

    ruta_gps = [
        {"lat": 50.941300, "lon": 6.958300},
        {"lat": 50.940700, "lon": 6.960200},
        {"lat": 50.940100, "lon": 6.962100},
        {"lat": 50.939500, "lon": 6.964000},
        {"lat": 50.938900, "lon": 6.965900},
        {"lat": 50.938300, "lon": 6.967800},
        {"lat": 50.937700, "lon": 6.969700},
        {"lat": 50.937100, "lon": 6.971600},
        {"lat": 50.936500, "lon": 6.973500},
        {"lat": 50.935900, "lon": 6.975400},
        {"lat": 50.935300, "lon": 6.977300},
        {"lat": 50.934700, "lon": 6.979200},
        {"lat": 50.934100, "lon": 6.981100},
        {"lat": 50.933500, "lon": 6.983000},
        {"lat": 50.932900, "lon": 6.984900},
        {"lat": 50.932300, "lon": 6.986800},
        {"lat": 50.931700, "lon": 6.988700},
        {"lat": 50.931100, "lon": 6.990600},
        {"lat": 50.930500, "lon": 6.992500},
        {"lat": 50.929900, "lon": 6.994400},
        {"lat": 50.929300, "lon": 6.996300},
        {"lat": 50.928700, "lon": 6.998200},
        {"lat": 50.928100, "lon": 7.000100},
        {"lat": 50.927500, "lon": 7.002000},
        {"lat": 50.926900, "lon": 7.003900},
        {"lat": 50.926300, "lon": 7.005800},
        {"lat": 50.925700, "lon": 7.007700},
        {"lat": 50.925100, "lon": 7.009600},
        {"lat": 50.924500, "lon": 7.011500},
        {"lat": 50.923900, "lon": 7.013400},
        {"lat": 50.923300, "lon": 7.015300},
        {"lat": 50.922700, "lon": 7.017200},
        {"lat": 50.922100, "lon": 7.019100},
        {"lat": 50.921500, "lon": 7.021000},
        {"lat": 50.920900, "lon": 7.022900},
        {"lat": 50.920300, "lon": 7.024800},
        {"lat": 50.919700, "lon": 7.026700},
        {"lat": 50.919100, "lon": 7.028600},
        {"lat": 50.918500, "lon": 7.030500},
        {"lat": 50.917900, "lon": 7.032400},
        {"lat": 50.917300, "lon": 7.034300},
        {"lat": 50.916700, "lon": 7.036200},
        {"lat": 50.916100, "lon": 7.038100},
        {"lat": 50.915500, "lon": 7.040000},
        {"lat": 50.914900, "lon": 7.041900},
        {"lat": 50.914300, "lon": 7.043800},
        {"lat": 50.913700, "lon": 7.045700},
        {"lat": 50.913100, "lon": 7.047600},
        {"lat": 50.912500, "lon": 7.049500},
        {"lat": 50.911900, "lon": 7.051400},
        {"lat": 50.911300, "lon": 7.053300},
        {"lat": 50.910700, "lon": 7.055200},
        {"lat": 50.910100, "lon": 7.057100},
        {"lat": 50.909500, "lon": 7.059000},
        {"lat": 50.908900, "lon": 7.060900},
        {"lat": 50.908300, "lon": 7.062800},
        {"lat": 50.907700, "lon": 7.064700},
        {"lat": 50.907100, "lon": 7.066600},
        {"lat": 50.906500, "lon": 7.068500},
        {"lat": 50.905900, "lon": 7.070400},
    ]

    return pagina_simulacion_generada("Media maratón en Colonia generada", "Run")


def pagina_simulacion_generada(titulo, tipo):
    return f"""
    <h1>{titulo}</h1>
    <p>Tipo de actividad: {tipo}</p>
    <p>Puntos GPS generados: {len(ruta_gps)}</p>
    <p><a href="/generar_gpx">Generar GPX</a></p>
    <p><a href="/subir_strava">Subir actividad a Strava</a></p>
    <p><a href="/">Volver</a></p>
    """


@app.route("/generar_gpx")
def generar_gpx():
    global ruta_gps
    global archivo_gpx_actual

    if len(ruta_gps) < 2:
        return """
        <h1>No hay suficientes puntos GPS</h1>
        <p>Primero inicia GPS real o genera una simulación.</p>
        <p><a href="/">Volver</a></p>
        """

    inicio = datetime.utcnow()

    with open(archivo_gpx_actual, "w", encoding="utf-8") as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="CuentaKM">
<trk>
<name>Cuenta KM GPS</name>
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
    <p>Archivo creado: {archivo_gpx_actual}</p>
    <p>Actividad actual: {nombre_actividad_actual}</p>
    <p><a href="/subir_strava">Subir actividad a Strava</a></p>
    <p><a href="/">Volver</a></p>
    """


@app.route("/subir_strava")
def subir_strava():
    if not ACCESS_TOKEN:
        return """
        <h1>No conectado a Strava</h1>
        <a href='/strava/login'>Conectar</a>
        """

    if not os.path.exists(archivo_gpx_actual):
        return """
        <h1>No existe GPX</h1>
        <p>Primero genera el GPX.</p>
        <p><a href="/">Volver</a></p>
        """

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    with open(archivo_gpx_actual, "rb") as fichero:
        files = {
            "file": fichero
        }

        data = {
            "data_type": "gpx",
            "name": nombre_actividad_actual,
            "description": "Actividad subida desde Cuenta KM GPS con Flask y Strava API",
            "sport_type": tipo_actividad_actual
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