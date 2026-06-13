# =============================================================================
# simulation/metrics.py
# =============================================================================

from __future__ import annotations


class Metrics:

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.total_llegadas  : int = 0
        self.total_atendidos : int = 0
        self.rechazados      : int = 0
        self.en_sistema      : int = 0
        self.max_simultaneos : int = 0

        self._tiempos_espera  : list[float] = []
        self._tiempos_sistema : list[float] = []

    # ── Registro de eventos ───────────────────────────────────────────────────

    def registrar_llegada(self) -> None:
        self.total_llegadas += 1
        self.en_sistema     += 1
        if self.en_sistema > self.max_simultaneos:
            self.max_simultaneos = self.en_sistema

    def registrar_rechazo(self) -> None:
        self.total_llegadas += 1
        self.rechazados     += 1

    def registrar_salida(self, cliente, sim_time: float) -> None:
        self.total_atendidos += 1
        self.en_sistema       = max(0, self.en_sistema - 1)

        if cliente.tiempo_espera > 0:
            self._tiempos_espera.append(cliente.tiempo_espera)

        tiempo_total = sim_time - cliente.tiempo_llegada
        if tiempo_total > 0:
            self._tiempos_sistema.append(tiempo_total)

    def registrar_servicio_completado(self, tiempo_espera: float) -> None:
        """Compatibilidad con llamadas existentes."""
        self.total_atendidos += 1
        self.en_sistema       = max(0, self.en_sistema - 1)
        if tiempo_espera > 0:
            self._tiempos_espera.append(tiempo_espera)

    # ── Propiedades calculadas ────────────────────────────────────────────────

    @property
    def espera_promedio(self) -> float:
        if not self._tiempos_espera:
            return 0.0
        return sum(self._tiempos_espera) / len(self._tiempos_espera)

    @property
    def tiempo_espera_promedio(self) -> float:
        return self.espera_promedio

    @property
    def tiempo_sistema_promedio(self) -> float:
        if not self._tiempos_sistema:
            return 0.0
        return sum(self._tiempos_sistema) / len(self._tiempos_sistema)

    @property
    def espera_maxima(self) -> float:
        if not self._tiempos_espera:
            return 0.0
        return max(self._tiempos_espera)

    # ── Listas públicas (para pantalla de estadísticas finales) ───────────────

    @property
    def tiempos_espera(self) -> list[float]:
        """Copia de los tiempos de espera registrados."""
        return list(self._tiempos_espera)

    @property
    def tiempos_en_sistema(self) -> list[float]:
        """Copia de los tiempos totales en sistema registrados."""
        return list(self._tiempos_sistema)

    # ── Exportación para la UI ────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "total_llegadas"         : self.total_llegadas,
            "total_atendidos"        : self.total_atendidos,
            "rechazados"             : self.rechazados,
            "en_sistema"             : self.en_sistema,
            "max_simultaneos"        : self.max_simultaneos,
            "espera_promedio"        : self.espera_promedio,
            "tiempo_espera_promedio" : self.tiempo_espera_promedio,
            "tiempo_sistema_promedio": self.tiempo_sistema_promedio,
            "espera_maxima"          : self.espera_maxima,
        }