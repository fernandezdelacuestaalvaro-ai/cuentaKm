from flask import Flask, redirect, request, jsonify
from dotenv import load_dotenv
import os
import math
import requests
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI", "http://localhost:5000/callback")

ACCESS_TOKEN = None

ruta_gps = []
nombre_actividad_actual = "Actividad Cuenta KM GPS"
tipo_actividad_actual = "Run"
archivo_gpx_actual = "ruta_cuenta_km.gpx"


@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Cuenta KM GPS</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <link
        rel="stylesheet"
        href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    />

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: #05080d;
            color: #f5f5f5;
            font-family: Arial, sans-serif;
        }

        header {
            padding: 20px;
            border-bottom: 1px solid #1f2937;
            background: #070b12;
        }

        h1 {
            margin: 0;
            color: #00d9ff;
            font-size: 34px;
        }

        h2 {
            color: #00d9ff;
            font-size: 20px;
            margin-top: 0;
        }

        a {
            color: #00d9ff;
            text-decoration: none;
        }

        .layout {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
            padding: 20px;
        }

        .card {
            background: #0b111c;
            border: 1px solid #1f2937;
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 0 20px rgba(0, 217, 255, 0.05);
        }

        .menu a {
            display: block;
            padding: 12px 0;
            border-bottom: 1px solid #1f2937;
            font-size: 16px;
        }

        .stats p {
            margin: 12px 0;
            color: #d1d5db;
        }

        .dato {
            display: block;
            color: #00d9ff;
            font-size: 28px;
            font-weight: bold;
            margin-top: 4px;
        }

        .btn {
            display: inline-block;
            border: none;
            border-radius: 10px;
            padding: 13px 18px;
            margin: 6px 6px 6px 0;
            color: white;
            cursor: pointer;
            font-size: 15px;
            text-align: center;
        }

        .btn-green {
            background: #138a13;
        }

        .btn-red {
            background: #c81e1e;
        }

        .btn-blue {
            background: #075fc9;
        }

        .btn-purple {
            background: #9b1aa6;
        }

        .btn-orange {
            background: #f05a14;
        }

        .sim-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }

        .sim-card {
            background: #080d15;
            border: 1px solid #263241;
            border-radius: 14px;
            padding: 16px;
            text-align: center;
        }

        .sim-card h3 {
            margin-top: 0;
        }

        .sim-card p {
            color: #d1d5db;
            min-height: 60px;
        }

        #map {
            height: 480px;
            width: 100%;
            border-radius: 14px;
            border: 1px solid #1f2937;
            overflow: hidden;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 12px;
            margin-top: 16px;
        }

        .summary-item {
            background: #070b12;
            border: 1px solid #1f2937;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
        }

        .summary-item span {
            display: block;
            color: #00d9ff;
            font-size: 22px;
            font-weight: bold;
            margin-top: 6px;
        }
        
        .sim-img {
            width: 100%;
            height: 170px;
            object-fit: cover;
            border-radius: 10px;
            margin: 12px 0;
            border: 1px solid #263241;
        }

        @media (max-width: 900px) {
            .sim-img {
                height: 150px;
            }
        }        

        @media (max-width: 900px) {
            .layout {
                grid-template-columns: 1fr;
                padding: 12px;
            }

            .sim-grid {
                grid-template-columns: 1fr;
            }

            .summary-grid {
                grid-template-columns: repeat(2, 1fr);
            }

            h1 {
                font-size: 28px;
            }

            #map {
                height: 360px;
            }
        }
    </style>
</head>

<body>
    <header>
        <h1>Cuenta KM GPS</h1>
    </header>

    <main class="layout">
        <aside>
            <section class="card menu">
                <h2>Conexión</h2>
                <a href="/strava/login">Conectar con Strava</a>
                <a href="/actividades">Ver actividades Strava</a>

                <h2 style="margin-top:25px;">Rutas</h2>
                <a href="/generar_gpx">Generar GPX</a>
                <a href="/subir_strava">Subir actividad a Strava</a>
                <a href="/reset_ruta">Resetear ruta</a>
            </section>

            <section class="card stats" style="margin-top:20px;">
                <h2>GPS real</h2>

                <p>Latitud:<span class="dato" id="lat">---</span></p>
                <p>Longitud:<span class="dato" id="lon">---</span></p>
                <p>Velocidad:<span class="dato"><span id="velocidad">0.00</span> km/h</span></p>
                <p>Distancia:<span class="dato"><span id="distancia">0.000</span> km</span></p>
                <p>Tiempo:<span class="dato" id="tiempo">00:00:00</span></p>

                <button class="btn btn-green" onclick="iniciarGPS()">Iniciar GPS</button>
                <button class="btn btn-red" onclick="pararGPS()">Parar GPS</button>
            </section>
        </aside>

        <section>
            <section class="card">
                <h2>Simulaciones disponibles</h2>

                <div class="sim-grid">
                    <div class="sim-card">
                        <h3>1. Carrera</h3>

                        <img class="sim-img"
                         src="https://images.unsplash.com/photo-1529963183134-61a90db47eaf?auto=format&fit=crop&w=1200&q=80"
                         alt="Reikiavik">

                        <p>Ruta urbana 10K por Reikiavik, Islandia.</p>

                        <a class="btn btn-green" href="/simular/reikiavik">Generar ruta</a>
                    </div>

                    <div class="sim-card">
                        <h3>2. Natación</h3>

                        <img class="sim-img"
                             src="https://images.unsplash.com/photo-1500043357865-c6b8827edf10?auto=format&fit=crop&w=800&q=80"
                             alt="Reikiavik">

                        <p>Natación en aguas abiertas frente a Reynisfjara.</p>

                        <a class="btn btn-blue" href="/simular/reynisfjara">Generar ruta</a>
                    </div>

                    <div class="sim-card">
                        <h3>3. Media maratón</h3>

                        <img class="sim-img"
                             src="https://images.unsplash.com/photo-1599946347371-68eb71b16afc?auto=format&fit=crop&w=800&q=80"
                             alt="Colonia Alemania">

                        <p>Media maratón por Colonia, Alemania.</p>

                        <a class="btn btn-purple" href="/simular/colonia">Generar ruta</a>
                    </div>
                </div>
            </section>

            <section class="card" style="margin-top:20px;">
                <h2>Vista previa de la ruta</h2>
                <div id="map"></div>

                <div class="summary-grid">
                    <div class="summary-item">
                        Distancia
                        <span id="mapDistancia">0.000 km</span>
                    </div>

                    <div class="summary-item">
                        Puntos GPS
                        <span id="mapPuntos">0</span>
                    </div>

                    <div class="summary-item">
                        Actividad
                        <span id="mapTipo">---</span>
                    </div>

                    <div class="summary-item">
                        Nombre
                        <span id="mapNombre" style="font-size:15px;">---</span>
                    </div>

                    <div class="summary-item">
                        Estado
                        <span id="mapEstado" style="font-size:15px;">Sin ruta</span>
                    </div>
                </div>

                <div style="margin-top:16px;">
                    <a class="btn btn-blue" href="/generar_gpx">Generar GPX</a>
                    <a class="btn btn-orange" href="/subir_strava">Subir a Strava</a>
                </div>
            </section>
        </section>
    </main>

    <script>
        let watchId = null;
        let ultimaLat = null;
        let ultimaLon = null;
        let distanciaTotal = 0;
        let segundosTotales = 0;
        let timerId = null;

        let map = L.map("map").setView([40.4168, -3.7038], 5);

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            maxZoom: 19,
            attribution: "OpenStreetMap"
        }).addTo(map);

        let rutaLayer = L.polyline([], {
            color: "#003cff",
            weight: 5
        }).addTo(map);

        let marcadorInicio = null;
        let marcadorFin = null;

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

            if (!timerId) {
                timerId = setInterval(function() {
                    segundosTotales++;
                    actualizarTiempo();
                }, 1000);
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
                        distanciaTotal += calcularDistancia(ultimaLat, ultimaLon, lat, lon);
                    }

                    ultimaLat = lat;
                    ultimaLon = lon;

                    document.getElementById("distancia").innerHTML = distanciaTotal.toFixed(3);

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
                    }).then(() => cargarRutaMapa());
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
            }

            if (timerId != null) {
                clearInterval(timerId);
                timerId = null;
            }
        }

        function actualizarTiempo() {
            const h = Math.floor(segundosTotales / 3600);
            const m = Math.floor((segundosTotales % 3600) / 60);
            const s = segundosTotales % 60;

            document.getElementById("tiempo").innerHTML =
                String(h).padStart(2, "0") + ":" +
                String(m).padStart(2, "0") + ":" +
                String(s).padStart(2, "0");
        }

        function cargarRutaMapa() {
            fetch("/api/ruta")
                .then(response => response.json())
                .then(data => {
                    const puntos = data.puntos.map(p => [p.lat, p.lon]);

                    rutaLayer.setLatLngs(puntos);

                    if (marcadorInicio) {
                        map.removeLayer(marcadorInicio);
                    }

                    if (marcadorFin) {
                        map.removeLayer(marcadorFin);
                    }

                    if (puntos.length > 0) {
                        marcadorInicio = L.marker(puntos[0]).addTo(map).bindPopup("Inicio");
                        marcadorFin = L.marker(puntos[puntos.length - 1]).addTo(map).bindPopup("Fin");

                        map.fitBounds(rutaLayer.getBounds(), {
                            padding: [30, 30]
                        });
                    }

                    document.getElementById("mapDistancia").innerHTML =
                        data.distancia.toFixed(3) + " km";

                    document.getElementById("mapPuntos").innerHTML =
                        data.puntos.length;

                    document.getElementById("mapTipo").innerHTML =
                        data.tipo;

                    document.getElementById("mapNombre").innerHTML =
                        data.nombre;

                    document.getElementById("mapEstado").innerHTML =
                        data.puntos.length > 1 ? "Lista" : "Sin ruta";
                });
        }

        cargarRutaMapa();
    </script>
</body>
</html>
    """


@app.route("/api/ruta")
def api_ruta():
    return jsonify({
        "puntos": ruta_gps,
        "distancia": distancia_ruta_km(ruta_gps),
        "nombre": nombre_actividad_actual,
        "tipo": tipo_actividad_actual
    })


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

    return jsonify({
        "ok": True,
        "puntos": len(ruta_gps)
    })


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

    nombre_actividad_actual = "Carrera 10K por Reikiavik - Cuenta KM GPS"
    tipo_actividad_actual = "Run"
    archivo_gpx_actual = "ruta_10k_reikiavik.gpx"

    ruta_gps = []

    puntos = 273

    puntos_control = [
        (64.14580, -21.93980),
        (64.14320, -21.92500),
        (64.13920, -21.91000),
        (64.13400, -21.90400),
        (64.12800, -21.91250),
        (64.12370, -21.92800),
        (64.12480, -21.94000),
        (64.12850, -21.95900),
        (64.13650, -21.96050),
        (64.14380, -21.95500),
        (64.15180, -21.94650),
        (64.15480, -21.93600),
        (64.14820, -21.93450),
        (64.14580, -21.93980),
    ]

    segmentos = len(puntos_control) - 1

    for i in range(puntos + 1):
        progreso = i / puntos
        posicion = progreso * segmentos
        indice = int(posicion)

        if indice >= segmentos:
            indice = segmentos - 1
            t = 1
        else:
            t = posicion - indice

        lat1, lon1 = puntos_control[indice]
        lat2, lon2 = puntos_control[indice + 1]

        lat = lat1 + (lat2 - lat1) * t
        lon = lon1 + (lon2 - lon1) * t

        ruta_gps.append({
            "lat": lat,
            "lon": lon
        })

    return pagina_simulacion_generada(
        "Carrera 10K por Reikiavik generada",
        "Run"
    )

@app.route("/simular/reynisfjara")
def simular_reynisfjara():
    global ruta_gps
    global nombre_actividad_actual
    global tipo_actividad_actual
    global archivo_gpx_actual

    nombre_actividad_actual = "Natación en Reynisfjara - Cuenta KM GPS"
    tipo_actividad_actual = "Swim"
    archivo_gpx_actual = "ruta_reynisfjara_swim.gpx"

    ruta_gps = []

    # Objetivo:
    # - Natación ida y vuelta frente a la playa negra de Reynisfjara.
    # - Salida desde la orilla.
    # - Toda la ruta dentro del mar.
    # - Distancia aproximada: 1.500 m.
    # - Ritmo aproximado: 2:30 / 100 m.
    # - Tiempo aproximado: 37 min 30 s.
    #
    # Tu generar_gpx usa 10 segundos por punto.
    # 225 puntos aproximadamente = 37 min 30 s.

    puntos_ida = 113
    puntos_vuelta = 113

    # Salida en la orilla, zona de playa
    lat_salida = 63.403950
    lon_salida = -19.044200

    # Punto mar adentro, separado de la costa
    lat_giro = 63.398900
    lon_giro = -19.034000

    # IDA: desde la orilla hacia mar abierto
    for i in range(puntos_ida):
        t = i / (puntos_ida - 1)

        lat = lat_salida + (lat_giro - lat_salida) * t
        lon = lon_salida + (lon_giro - lon_salida) * t

        # Curva suave mar adentro para evitar tierra
        lat -= 0.00055 * math.sin(t * math.pi)

        # Oleaje suave
        lon += 0.00012 * math.sin(t * math.pi * 4)

        ruta_gps.append({
            "lat": lat,
            "lon": lon
        })

    # VUELTA: regreso a la orilla por una línea paralela, más mar adentro
    for i in range(1, puntos_vuelta):
        t = i / (puntos_vuelta - 1)

        lat = lat_giro + (lat_salida - lat_giro) * t
        lon = lon_giro + (lon_salida - lon_giro) * t

        # Vuelta más mar adentro que la ida
        lat -= 0.00110 * math.sin(t * math.pi)

        # Oleaje suave
        lon -= 0.00012 * math.sin(t * math.pi * 4)

        ruta_gps.append({
            "lat": lat,
            "lon": lon
        })

    return pagina_simulacion_generada(
        "Natación por Reynisfjara generada",
        "Swim"
    )


@app.route("/simular/colonia")
def simular_colonia():
    global ruta_gps
    global nombre_actividad_actual
    global tipo_actividad_actual
    global archivo_gpx_actual

    nombre_actividad_actual = "Media maratón en Colonia - Cuenta KM GPS"
    tipo_actividad_actual = "Run"
    archivo_gpx_actual = "ruta_media_maraton_colonia.gpx"

    ruta_gps = []

    # Centro aproximado en Colonia, al oeste del Rin
    centro_lat = 50.9362
    centro_lon = 6.9250

    # Queremos que el GPX tenga unos 590 intervalos.
    # Como generar_gpx suma 10 segundos por punto:
    # 590 * 10 = 5900 segundos = 1h 38min 20s aprox.
    # Eso encaja con una media maratón a ritmo 4:40/km.
    puntos = 591

    # Elipse urbana aproximada de unos 21 km.
    # Radio norte-sur: unos 4.35 km
    # Radio este-oeste: unos 2.15 km
    radio_lat = 4.35 / 111.32
    radio_lon = 2.15 / 70.3

    for i in range(puntos + 1):
        angulo = 2 * math.pi * i / puntos

        lat = centro_lat + radio_lat * math.sin(angulo)
        lon = centro_lon + radio_lon * math.cos(angulo)

        ruta_gps.append({
            "lat": lat,
            "lon": lon
        })

    return pagina_simulacion_generada(
        "Media maratón en Colonia generada",
        "Run"
    )



def pagina_simulacion_generada(titulo, tipo):
    return f"""
    <h1>{titulo}</h1>
    <p>Tipo de actividad: {tipo}</p>
    <p>Puntos GPS generados: {len(ruta_gps)}</p>
    <p>Distancia aproximada: {distancia_ruta_km(ruta_gps):.3f} km</p>
    <p><a href="/">Ver vista previa en el mapa</a></p>
    <p><a href="/generar_gpx">Generar GPX</a></p>
    <p><a href="/subir_strava">Subir actividad a Strava</a></p>
    """


@app.route("/generar_gpx")
def generar_gpx():
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
    <p>Distancia aproximada: {distancia_ruta_km(ruta_gps):.3f} km</p>
    <p><a href="/">Ver ruta en mapa</a></p>
    <p><a href="/subir_strava">Subir actividad a Strava</a></p>
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


@app.route("/reset_ruta")
def reset_ruta():
    global ruta_gps
    global nombre_actividad_actual
    global tipo_actividad_actual
    global archivo_gpx_actual

    ruta_gps = []
    nombre_actividad_actual = "Actividad Cuenta KM GPS"
    tipo_actividad_actual = "Run"
    archivo_gpx_actual = "ruta_cuenta_km.gpx"

    return redirect("/")


def distancia_ruta_km(ruta):
    distancia = 0

    for i in range(1, len(ruta)):
        distancia += calcular_distancia_km(
            ruta[i - 1]["lat"],
            ruta[i - 1]["lon"],
            ruta[i]["lat"],
            ruta[i]["lon"]
        )

    return distancia


def calcular_distancia_km(lat1, lon1, lat2, lon2):
    radio_tierra_km = 6371

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return radio_tierra_km * c


if __name__ == "__main__":
    app.run(debug=True)