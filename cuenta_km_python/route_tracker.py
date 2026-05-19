from geo_utils import distancia_km


class RouteTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.latitud = 41.084117
        self.longitud = -0.198851

        self.latitud_anterior = self.latitud
        self.longitud_anterior = self.longitud

        self.distancia_total = 0.0
        self.velocidad_actual = 0.0
        self.velocidades = []
        self.tiempo_segundos = 0

    def avanzar(self, factor_aumento):
        self.latitud_anterior = self.latitud
        self.longitud_anterior = self.longitud

        incremento = factor_aumento / 100000
        self.latitud -= incremento
        self.longitud -= incremento

        distancia = distancia_km(
            self.latitud_anterior,
            self.longitud_anterior,
            self.latitud,
            self.longitud
        )

        self.distancia_total += distancia

        if self.tiempo_segundos > 0:
            self.velocidad_actual = distancia * 3600
            self.velocidades.append(self.velocidad_actual)

        return distancia

    def velocidad_media(self):
        if not self.velocidades:
            return 0.0
        return sum(self.velocidades) / len(self.velocidades)

    def distancia_teorica(self):
        return (self.velocidad_media() / 3600) * self.tiempo_segundos

    def precision(self):
        teorica = self.distancia_teorica()
        calculada = self.distancia_total

        if teorica == 0 or calculada == 0:
            return 0.0

        menor = min(teorica, calculada)
        mayor = max(teorica, calculada)

        return (menor / mayor) * 100