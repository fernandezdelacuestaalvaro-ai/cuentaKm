from flask import Flask, render_template, request, jsonify, redirect
from dotenv import load_dotenv
import os
import requests

load_dotenv()

CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("STRAVA_REDIRECT_URI")

app = Flask(__name__)

ultima_latitud = None
ultima_longitud = None
ultima_velocidad = 0
access_token_global = None


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/gps", methods=["POST"])
def recibir_gps():
    global ultima_latitud
    global ultima_longitud
    global ultima_velocidad

    datos = request.get_json()

    ultima_latitud = datos.get("latitud")
    ultima_longitud = datos.get("longitud")
    ultima_velocidad = datos.get("velocidad")

    print("GPS recibido:", ultima_latitud, ultima_longitud, ultima_velocidad)

    return jsonify({"ok": True})


@app.route("/ubicacion")
def ubicacion():
    return jsonify({
        "latitud": ultima_latitud,
        "longitud": ultima_longitud,
        "velocidad": ultima_velocidad
    })


@app.route("/strava/login")
@app.route("/login_strava")
def login_strava():
    url = (
        "https://www.strava.com/oauth/authorize"
        f"?client_id={CLIENT_ID}"
        "&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        "&approval_prompt=force"
        "&scope=read,activity:read_all,activity:write"
    )

    return redirect(url)


@app.route("/callback")
def callback():
    global access_token_global

    code = request.args.get("code")

    if not code:
        return "Error: Strava no devolvió código de autorización"

    response = requests.post(
        "https://www.strava.com/oauth/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code"
        }
    )

    datos = response.json()

    access_token = datos.get("access_token")

    if not access_token:
        return f"Error obteniendo token de Strava: {datos}"

    access_token_global = access_token

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    atleta_response = requests.get(
        "https://www.strava.com/api/v3/athlete",
        headers=headers
    )

    atleta = atleta_response.json()

    nombre = atleta.get("firstname", "")
    apellido = atleta.get("lastname", "")

    return f"""
    <h1>STRAVA CONECTADO</h1>

    <p><b>Usuario:</b> {nombre} {apellido}</p>

    <p>Tu aplicación ya puede acceder a Strava.</p>

    <p>
        <a href="/actividades">Ver actividades</a>
    </p>

    <p>
        <a href="/">Volver</a>
    </p>
    """


@app.route("/actividades")
def actividades():
    if not access_token_global:
        return redirect("/strava/login")

    headers = {
        "Authorization": f"Bearer {access_token_global}"
    }

    response = requests.get(
        "https://www.strava.com/api/v3/athlete/activities",
        headers=headers,
        params={
            "per_page": 10
        }
    )

    if response.status_code != 200:
        return f"Error consultando actividades: {response.text}"

    actividades_strava = response.json()

    html = """
    <h1>Actividades de Strava</h1>
    <p><a href="/">Volver</a></p>
    <hr>
    """

    for actividad in actividades_strava:
        nombre = actividad.get("name", "Sin nombre")
        tipo = actividad.get("type", "")
        distancia_km = round(actividad.get("distance", 0) / 1000, 2)
        tiempo_min = round(actividad.get("moving_time", 0) / 60, 1)
        fecha = actividad.get("start_date_local", "")

        html += f"""
        <div>
            <h3>{nombre}</h3>
            <p>Tipo: {tipo}</p>
            <p>Distancia: {distancia_km} km</p>
            <p>Tiempo: {tiempo_min} min</p>
            <p>Fecha: {fecha}</p>
        </div>
        <hr>
        """

    return html


if __name__ == "__main__":
    app.run(debug=True)