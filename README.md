# Cuenta KM GPS

Aplicación Python para registrar rutas GPS, calcular distancia recorrida, calcular velocidad, generar rutas GPX y subir actividades a Strava mediante su API.

El proyecto nació como una evolución de un antiguo cuentakilómetros personal, pero adaptado a una arquitectura web con Flask, GPS del navegador y conexión real con Strava.

## Tecnologías

- Python
- Flask
- HTML
- JavaScript
- Geolocation API del navegador
- API de Strava
- OAuth2
- GPX
- dotenv para variables de entorno

## Funcionalidades principales

- Lectura GPS real desde navegador.
- Obtención de latitud y longitud.
- Cálculo de distancia acumulada.
- Cálculo de velocidad en tiempo real.
- Generación de rutas GPX.
- Conexión real con Strava usando OAuth2.
- Lectura de actividades reales de Strava.
- Subida de actividades GPX a Strava.
- Simulaciones de rutas:
  - Carrera por Reikiavik, Islandia.
  - Natación en la playa negra de Reynisfjara, Islandia.
  - Media maratón en Colonia, Alemania.

## Estructura del proyecto

```text
cuenta_km_python/
├── web_app.py
├── requirements.txt
├── .env
├── .gitignore
├── csv_writer.py
├── geo_utils.py
├── main.py
├── route_tracker.py
└── templates/
    └── index.html
```

## Variables de entorno

El fichero .env contiene los datos privados de Strava.

Ejemplo:

STRAVA_CLIENT_ID=tu_client_id
STRAVA_CLIENT_SECRET=tu_client_secret
STRAVA_REDIRECT_URI=http://localhost:5000/callback

Importante: el fichero .env no debe subirse a GitHub.

En .gitignore debe aparecer:

.env
__pycache__/
*.pyc
Ejecutar proyecto

Instalar dependencias:

pip install -r requirements.txt

Ejecutar aplicación:

python web_app.py

Abrir navegador:

http://127.0.0.1:5000

## Funcionamiento general

La aplicación tiene dos formas de trabajar:

GPS real desde navegador.
Rutas simuladas generadas desde Python.

En el modo GPS real, el navegador obtiene la ubicación mediante navigator.geolocation.watchPosition.

Cada nueva posición contiene:

latitud
longitud
velocidad

Después, el frontend calcula la distancia entre la posición anterior y la nueva posición.

También envía los puntos GPS al backend Flask mediante una petición POST a /gps.

En el modo simulación, Python genera listas de coordenadas GPS ficticias o predefinidas para representar rutas deportivas.

## Fórmula de distancia entre coordenadas GPS

Para calcular la distancia entre dos puntos de la Tierra se usa la fórmula Haversine.

Se parte de dos puntos:

Punto 1: lat1, lon1
Punto 2: lat2, lon2

La fórmula usada es:

R = 6371 km

dLat = (lat2 - lat1) * PI / 180
dLon = (lon2 - lon1) * PI / 180

a = sin²(dLat / 2)
    + cos(lat1 * PI / 180)
    * cos(lat2 * PI / 180)
    * sin²(dLon / 2)

c = 2 * atan2(sqrt(a), sqrt(1 - a))

distancia = R * c

Donde:

R es el radio aproximado de la Tierra en kilómetros.
dLat es el cambio de latitud.
dLon es el cambio de longitud.
distancia es la distancia entre ambos puntos en kilómetros.

En JavaScript aparece en la función:

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

## Cálculo de velocidad

Cuando el GPS real devuelve velocidad, el navegador la entrega normalmente en metros por segundo.

Para convertirla a kilómetros por hora:

velocidad_kmh = velocidad_metros_segundo * 3.6

Ejemplo:

let velocidad = posicion.coords.speed;

if (velocidad == null) {
    velocidad = 0;
}

velocidad = velocidad * 3.6;

Si el navegador no proporciona velocidad, la aplicación muestra 0.00 km/h.

## Métodos principales de web_app.py
home()

Ruta:

/

Muestra la pantalla principal de la aplicación.

Incluye:

panel de GPS real,
latitud,
longitud,
velocidad,
distancia,
botones para iniciar/parar GPS,
enlaces a Strava,
enlaces a simulaciones,
generación de GPX,
subida a Strava.
recibir_gps()

Ruta:

/gps

Método:

POST

Recibe desde JavaScript los datos GPS reales:

{
  "latitud": 40.123456,
  "longitud": -0.123456,
  "velocidad": 12.5,
  "distancia_total": 1.25
}

Después guarda cada punto dentro de la lista global:

ruta_gps

Cada punto se guarda así:

{
    "lat": latitud,
    "lon": longitud
}

Esta lista luego se usa para generar el archivo GPX.

strava_login()

Ruta:

/strava/login

Redirige al usuario a Strava para autorizar la aplicación.

La URL generada usa OAuth2:

https://www.strava.com/oauth/authorize

Solicita los permisos:

read
activity:write
activity:read_all

Estos permisos permiten:

leer perfil básico,
leer actividades,
subir actividades nuevas.
callback()

Ruta:

/callback

Strava llama a esta ruta después de autorizar la aplicación.

Recibe un parámetro code.

Ese code se intercambia por un access_token haciendo una petición POST a:

https://www.strava.com/oauth/token

El token se guarda temporalmente en:

ACCESS_TOKEN

Ese token se usa luego para consultar actividades o subir rutas.

actividades()

Ruta:

/actividades

Consulta las actividades reales del usuario en Strava.

Llama a:

https://www.strava.com/api/v3/athlete/activities

Devuelve información como:

nombre de la actividad,
tipo,
distancia,
tiempo,
fecha.
simular_reikiavik()

Ruta:

/simular/reikiavik

Genera una ruta simulada de carrera por Reikiavik, Islandia.

Configura:

nombre_actividad_actual = "Carrera por Reikiavik - Cuenta KM GPS"
tipo_actividad_actual = "Run"
archivo_gpx_actual = "ruta_reikiavik.gpx"

Después rellena ruta_gps con coordenadas de Reikiavik.

simular_reynisfjara()

Ruta:

/simular/reynisfjara

Genera una ruta simulada de natación en la playa negra de Reynisfjara, Islandia.

Configura:

nombre_actividad_actual = "Natación en Reynisfjara - Cuenta KM GPS"
tipo_actividad_actual = "Swim"
archivo_gpx_actual = "ruta_reynisfjara_swim.gpx"

Después rellena ruta_gps con coordenadas cercanas a Reynisfjara.

simular_colonia()

Ruta:

/simular/colonia

Genera una ruta simulada de media maratón en Colonia, Alemania.

Configura:

nombre_actividad_actual = "Media maratón en Colonia - Cuenta KM GPS"
tipo_actividad_actual = "Run"
archivo_gpx_actual = "ruta_media_maraton_colonia.gpx"

Después rellena ruta_gps con coordenadas de Colonia.

pagina_simulacion_generada()

Muestra una pantalla de confirmación después de generar una simulación.

Indica:

nombre de la simulación,
tipo de actividad,
número de puntos GPS generados,
enlace para generar GPX,
enlace para subir a Strava.
generar_gpx()

Ruta:

/generar_gpx

Genera un fichero GPX a partir de los puntos de ruta_gps.

El formato generado es:

<gpx>
    <trk>
        <name>Cuenta KM GPS</name>
        <trkseg>
            <trkpt lat="..." lon="...">
                <time>...</time>
            </trkpt>
        </trkseg>
    </trk>
</gpx>

Cada punto lleva:

latitud,
longitud,
tiempo.

Los tiempos se generan así:

inicio = datetime.utcnow()
tiempo = inicio + timedelta(seconds=i * 10)

Esto simula un punto GPS cada 10 segundos.

subir_strava()

Ruta:

/subir_strava

Sube el archivo GPX generado a Strava.

Llama a:

https://www.strava.com/api/v3/uploads

Envía:

data = {
    "data_type": "gpx",
    "name": nombre_actividad_actual,
    "description": "Actividad subida desde Cuenta KM GPS con Flask y Strava API",
    "sport_type": tipo_actividad_actual
}

Y adjunta el archivo GPX:

files = {
    "file": fichero
}

Strava responde indicando que la actividad está en proceso:

Your activity is still being processed.

Después de unos segundos o minutos, la actividad aparece en Strava.

Flujo para probar GPS real
Abrir:
http://127.0.0.1:5000
Pulsar:
Iniciar GPS
Aceptar permisos de ubicación en el navegador.
Ver:
latitud
longitud
velocidad
distancia
Pulsar:
Generar GPX de la ruta actual
Pulsar:
Subir actividad actual a Strava
Flujo para probar simulaciones
Carrera por Reikiavik
/simular/reikiavik
/generar_gpx
/subir_strava
Natación en Reynisfjara
/simular/reynisfjara
/generar_gpx
/subir_strava
Media maratón en Colonia
/simular/colonia
/generar_gpx
/subir_strava

## Conexión con Strava

Para conectar con Strava:

Crear una aplicación en:
https://www.strava.com/settings/api

Configurar:
Authorization Callback Domain: localhost
Configurar .env:

STRAVA_CLIENT_ID=tu_client_id
STRAVA_CLIENT_SECRET=tu_client_secret
STRAVA_REDIRECT_URI=http://localhost:5000/callback

Entrar en:
http://127.0.0.1:5000/strava/login

Autorizar la aplicación.
La app recibirá el token en /callback.
Despliegue futuro en Render

En local se usa:

STRAVA_REDIRECT_URI=http://localhost:5000/callback

En Render habría que cambiarlo por algo como:

STRAVA_REDIRECT_URI=https://cuenta-km-gps.onrender.com/callback

Y en Strava habría que cambiar el dominio de callback a:

cuenta-km-gps.onrender.com

Las variables privadas no deben ir en GitHub. En Render se configurarían como variables de entorno.

## Mejoras futuras
Guardar rutas en base de datos.
Añadir mapa OpenStreetMap con Leaflet.
Mostrar la ruta antes de subirla.
Exportar GPX manualmente.
Exportar TCX/FIT.
Añadir historial de rutas.
Añadir desnivel acumulado.
Añadir autenticación de usuarios.
Separar frontend y backend.
Mejorar estilos de la interfaz.
Guardar refresh_token para no tener que reconectar con Strava cada vez.