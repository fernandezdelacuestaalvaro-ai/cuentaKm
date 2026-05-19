import tkinter as tk
from tkinter import messagebox

from route_tracker import RouteTracker
from csv_writer import CsvWriter


class CuentaKmApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cuenta KM Python")
        self.root.geometry("430x520")
        self.root.configure(bg="black")

        self.tracker = RouteTracker()
        self.csv_writer = CsvWriter()

        self.en_marcha = False
        self.factor_aumento = tk.IntVar(value=0)

        self.crear_interfaz()
        self.actualizar_pantalla()

    def crear_interfaz(self):
        self.lbl_velocidad = self.crear_label("Velocidad actual:")
        self.lbl_velocidad_valor = self.crear_label_valor("0.00 km/h")

        self.lbl_media = self.crear_label("Velocidad media:")
        self.lbl_media_valor = self.crear_label_valor("0.00 km/h")

        self.lbl_distancia = self.crear_label("Distancia recorrida:")
        self.lbl_distancia_valor = self.crear_label_valor("0.000 km")

        self.lbl_tiempo = self.crear_label("Tiempo:")
        self.lbl_tiempo_valor = self.crear_label_valor("00:00:00")

        self.lbl_precision = self.crear_label("Precisión:")
        self.lbl_precision_valor = self.crear_label_valor("0.00 %")

        self.lbl_teorica = self.crear_label("Distancia teórica:")
        self.lbl_teorica_valor = self.crear_label_valor("0.000 km")

        self.lbl_calculada = self.crear_label("Distancia calculada:")
        self.lbl_calculada_valor = self.crear_label_valor("0.000 km")

        self.btn_start = tk.Button(
            self.root,
            text="Start",
            bg="green",
            fg="white",
            width=10,
            command=self.start
        )
        self.btn_start.pack(pady=5)

        self.btn_stop = tk.Button(
            self.root,
            text="Stop",
            bg="red",
            fg="white",
            width=10,
            command=self.stop
        )
        self.btn_stop.pack(pady=5)

        self.btn_reset = tk.Button(
            self.root,
            text="Reset",
            bg="yellow",
            fg="black",
            width=10,
            command=self.reset
        )
        self.btn_reset.pack(pady=5)

        self.slider = tk.Scale(
            self.root,
            from_=0,
            to=100,
            orient="horizontal",
            label="Factor de aumento / simulación",
            variable=self.factor_aumento,
            bg="black",
            fg="white",
            troughcolor="gray",
            length=350
        )
        self.slider.pack(pady=20)

    def crear_label(self, texto):
        label = tk.Label(
            self.root,
            text=texto,
            bg="black",
            fg="white",
            font=("Arial", 12, "bold")
        )
        label.pack()
        return label

    def crear_label_valor(self, texto):
        label = tk.Label(
            self.root,
            text=texto,
            bg="black",
            fg="cyan",
            font=("Arial", 14, "bold")
        )
        label.pack(pady=3)
        return label

    def start(self):
        self.en_marcha = True

    def stop(self):
        self.en_marcha = False

    def reset(self):
        self.en_marcha = False
        self.tracker.reset()
        self.actualizar_pantalla()

    def actualizar_pantalla(self):
        if self.en_marcha:
            self.tracker.tiempo_segundos += 1
            self.tracker.avanzar(self.factor_aumento.get())
            self.csv_writer.grabar(self.tracker)

        horas = self.tracker.tiempo_segundos // 3600
        minutos = (self.tracker.tiempo_segundos % 3600) // 60
        segundos = self.tracker.tiempo_segundos % 60

        self.lbl_tiempo_valor.config(
            text=f"{horas:02d}:{minutos:02d}:{segundos:02d}"
        )

        self.lbl_velocidad_valor.config(
            text=f"{self.tracker.velocidad_actual:.2f} km/h"
        )

        self.lbl_media_valor.config(
            text=f"{self.tracker.velocidad_media():.2f} km/h"
        )

        self.lbl_distancia_valor.config(
            text=f"{self.tracker.distancia_total:.3f} km"
        )

        self.lbl_precision_valor.config(
            text=f"{self.tracker.precision():.2f} %"
        )

        self.lbl_teorica_valor.config(
            text=f"{self.tracker.distancia_teorica():.3f} km"
        )

        self.lbl_calculada_valor.config(
            text=f"{self.tracker.distancia_total:.3f} km"
        )

        self.root.after(1000, self.actualizar_pantalla)


if __name__ == "__main__":
    root = tk.Tk()
    app = CuentaKmApp(root)
    root.mainloop()