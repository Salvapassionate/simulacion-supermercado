# =============================================================================
# simulation/arrival_system.py
# Administra el proceso de arrivals (llegadas) de clientes.
# Simula un proceso de Poisson mediante intervalos aleatorios exponenciales.
# =============================================================================

from __future__ import annotations
import random
import math


class ArrivalSystem:
    """
    Generador de llegadas de clientes con distribución exponencial.

    El tiempo entre llegadas sucesivas sigue una distribución exponencial
    con media = intervalo_base segundos, lo que equivale a un proceso de Poisson
    con tasa λ = 1 / intervalo_base clientes por segundo.

    Uso:
        arrival.update(dt)   → acumula tiempo
        arrival.debe_generar → True si es momento de crear un nuevo cliente
        arrival.reset_flag() → confirma la generación y prepara el siguiente ciclo
    """

    def __init__(self, intervalo_base: float = 3.0) -> None:
        """
        Parameters
        ----------
        intervalo_base : Tiempo promedio entre llegadas (segundos).
        """
        self.intervalo_base = intervalo_base
        self._acumulador    : float = 0.0
        self._proximo_arribo: float = self._generar_intervalo()
        self._debe_generar  : bool  = False

    def _generar_intervalo(self) -> float:
        """
        Genera el próximo intervalo de llegada con distribución exponencial.
        Fórmula: -ln(U) / λ  donde U ~ Uniforme(0, 1)
        El mínimo garantizado es 0.5 s para evitar saturación instantánea.
        """
        u = random.random()
        # Evitar log(0) con un epsilon pequeño
        u = max(u, 1e-9)
        intervalo = -math.log(u) * self.intervalo_base
        return max(0.5, intervalo)

    def update(self, dt: float) -> None:
        """
        Acumula el tiempo transcurrido y activa la bandera de generación
        cuando se cumple el intervalo configurado.

        Parameters
        ----------
        dt : Tiempo transcurrido en el frame actual (segundos).
        """
        if self._debe_generar:
            # La generación anterior aún no fue consumida; no avanzar el reloj.
            return

        self._acumulador += dt

        if self._acumulador >= self._proximo_arribo:
            self._acumulador   -= self._proximo_arribo
            self._proximo_arribo = self._generar_intervalo()
            self._debe_generar   = True

    @property
    def debe_generar(self) -> bool:
        """True si es el momento de instanciar un nuevo cliente."""
        return self._debe_generar

    def reset_flag(self) -> None:
        """
        Confirma que la generación fue procesada.
        Debe llamarse después de instanciar al nuevo cliente.
        """
        self._debe_generar = False

    def generar_productos(self, min_prod: int = 1, max_prod: int = 20) -> int:
        """
        Genera aleatoriamente el número de productos que lleva un cliente nuevo.
        Distribución uniforme entre min_prod y max_prod.
        """
        return random.randint(min_prod, max_prod)

    def set_intervalo(self, nuevo_intervalo: float) -> None:
        """Actualiza la tasa de arribo en tiempo real (permite ajuste dinámico)."""
        self.intervalo_base  = max(0.5, nuevo_intervalo)
        self._proximo_arribo = self._generar_intervalo()
