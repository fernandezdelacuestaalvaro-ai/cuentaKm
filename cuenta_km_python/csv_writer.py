import csv
from datetime import datetime
from pathlib import Path


class CsvWriter:
    def __init__(self):
        carpeta = Path.home() / "Documents" / "misRutas"
        carpeta.mkdir(parents=True, exist_ok=True)

        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.ruta_fichero = carpeta / f"Ruta_{fecha}.csv"

        with open(self.ruta_fichero, "w", newline="", encoding="utf-8") as fichero:
            writer = csv.writer(fichero, delimiter=";")
            writer.writerow([
                "tiempo_segundos",
                "distancia_total_km",
                "distancia_teorica_km",
                "precision",
                "velocidad_actual_kmh",
                "velocidad_media_kmh",
                "latitud",
                "longitud"
            ])

    def grabar(self, tracker):
        with open(self.ruta_fichero, "a", newline="", encoding="utf-8") as fichero:
            writer = csv.writer(fichero, delimiter=";")
            writer.writerow([
                tracker.tiempo_segundos,
                round(tracker.distancia_total, 6),
                round(tracker.distancia_teorica(), 6),
                round(tracker.precision(), 2),
                round(tracker.velocidad_actual, 2),
                round(tracker.velocidad_media(), 2),
                tracker.latitud,
                tracker.longitud
            ])