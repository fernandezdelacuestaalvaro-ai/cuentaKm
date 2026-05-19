from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/gps", methods=["POST"])
def recibir_gps():
    datos = request.get_json()

    latitud = datos.get("latitud")
    longitud = datos.get("longitud")
    velocidad = datos.get("velocidad")

    print("GPS recibido:", latitud, longitud, velocidad)

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True)