# =============================================================================
# engine/sorting.py
# Sistema de ordenamiento de profundidad visual (Y-Sort / Depth Sorting).
#
# SOLUCIÓN CRÍTICA ANTI-PARPADEO:
# El orden de profundidad NO usa screen_y (que cambia píxel a píxel durante
# el movimiento) sino la clave lógica del grid: (gx + gy) * 32.
# Esto garantiza transiciones de profundidad suaves y sin flickering entre
# las góndolas estáticas y los clientes en movimiento.
# =============================================================================

from __future__ import annotations
import pygame
from typing import NamedTuple


class RenderItem(NamedTuple):
    """
    Paquete de renderizado que el sistema de ordenamiento encola por frame.

    Campos:
        sort_key  : Clave de profundidad lógica basada en coordenadas del grid.
                    Calculada como (gx + gy) * 32 para evitar parpadeos.
        dest_x    : Coordenada X de pantalla del punto de anclaje superior-izquierdo.
        dest_y    : Coordenada Y de pantalla del punto de anclaje superior-izquierdo.
        surface   : Superficie pygame.Surface lista para blit.
    """
    sort_key : float
    dest_x   : int
    dest_y   : int
    surface  : pygame.Surface


class YSorter:
    """
    Gestor de ordenamiento de profundidad por frame.

    Los objetos más cercanos visualmente (mayor valor de gx + gy) se dibujan
    después, solapando correctamente a los que están más atrás.
    """

    def __init__(self) -> None:
        self._queue: list[RenderItem] = []

    def clear(self) -> None:
        """Vacía la cola de renderizado al inicio de cada frame."""
        self._queue.clear()

    def submit(
        self,
        surface  : pygame.Surface,
        dest_x   : int,
        dest_y   : int,
        sort_key : float
    ) -> None:
        """
        Encola una superficie para renderizado con su clave de profundidad.

        Parameters
        ----------
        surface  : Sprite ya dibujado listo para blit.
        dest_x   : Posición X de pantalla (punto superior-izquierdo del sprite).
        dest_y   : Posición Y de pantalla (punto superior-izquierdo del sprite).
        sort_key : Valor de profundidad lógica (gx + gy) * 32.
        """
        self._queue.append(RenderItem(sort_key, dest_x, dest_y, surface))

    def draw(self, surface: pygame.Surface) -> None:
        """
        Ordena la cola de forma ascendente por sort_key y ejecuta todos los blits.
        Los objetos con sort_key mayor (más al frente en el grid) se pintan encima.
        """
        self._queue.sort(key=lambda item: item.sort_key)
        for item in self._queue:
            surface.blit(item.surface, (item.dest_x, item.dest_y))
