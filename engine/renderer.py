# =============================================================================
# engine/renderer.py
# Encapsula el ciclo completo de renderizado por fotograma.
# Actúa como intermediario entre las entidades y el sistema YSorter.
# =============================================================================

from __future__ import annotations
import pygame
from engine.sorting import YSorter


class Renderer:
    """
    Gestor central de renderizado por frame.

    Flujo de uso en el bucle principal:
        1. renderer.begin()              → limpia la cola del frame anterior
        2. entity.draw(renderer)         → las entidades llaman renderer.submit(...)
        3. renderer.draw(screen_surface) → ordena y ejecuta todos los blits
    """

    def __init__(self) -> None:
        self._sorter = YSorter()

    def begin(self) -> None:
        """
        Debe llamarse al inicio de cada frame antes de procesar entidades.
        Vacía la cola de renderizado del frame anterior.
        """
        self._sorter.clear()

    def submit(
        self,
        surface  : pygame.Surface,
        dest_x   : int,
        dest_y   : int,
        sort_key : float
    ) -> None:
        """
        Encola una superficie con su clave de profundidad.
        Las entidades delegan aquí desde su método draw().

        Parameters
        ----------
        surface  : Sprite pre-renderizado con canal alfa.
        dest_x   : Coordenada X de pantalla (esquina superior-izquierda del sprite).
        dest_y   : Coordenada Y de pantalla (esquina superior-izquierda del sprite).
        sort_key : (gx + gy) * 32 — clave lógica de profundidad.
        """
        self._sorter.submit(surface, dest_x, dest_y, sort_key)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Ejecuta el ordenamiento de profundidad y pinta todos los sprites
        encolados sobre la superficie destino.
        """
        self._sorter.draw(surface)
