# =============================================================================
# entities/entity_base.py
# Clase base para todas las entidades visuales de la simulación.
# Gestiona posición en el grid lógico y delegación al sistema de renderizado.
# =============================================================================

from __future__ import annotations
import pygame
from engine.iso import to_iso
from engine.renderer import Renderer


class Entity:
    """
    Clase base de entidad isométrica.

    Toda entidad conoce su posición en el grid lógico (gx, gy, gz) y delega
    su propio renderizado al Renderer mediante el patrón submit().

    REGLA DE ANCLAJE:
    El punto de blit se calcula como:
        dest_x = screen_x - sprite.get_width()  // 2
        dest_y = screen_y - sprite.get_height()

    Esto asegura que la BASE INFERIOR CENTRAL del sprite coincida con el
    centro del rombo isométrico de la celda (screen_x, screen_y).
    """

    def __init__(
        self,
        gx     : float,
        gy     : float,
        gz     : float = 0.0,
        sprite : pygame.Surface | None = None
    ) -> None:
        self.gx     = gx        # Coordenada lógica X en el grid
        self.gy     = gy        # Coordenada lógica Y en el grid
        self.gz     = gz        # Coordenada lógica Z (altura, en unidades de tile)
        self.sprite = sprite    # Superficie pygame pre-renderizada

        # Coordenadas de pantalla calculadas (se actualizan en update/draw)
        self.screen_x: int = 0
        self.screen_y: int = 0

        self._update_screen_coords()

    def _update_screen_coords(self) -> None:
        """Recalcula las coordenadas de pantalla a partir de la posición lógica."""
        self.screen_x, self.screen_y = to_iso(self.gx, self.gy, self.gz)

    @property
    def sort_key(self) -> float:
        """
        Clave de profundidad para el sistema Y-Sort.
        Se basa en las coordenadas lógicas del grid para evitar parpadeos.
        Fórmula: (gx + gy) * 32
        """
        return (self.gx + self.gy) * 32

    def draw(self, renderer: Renderer) -> None:
        """
        Envía el sprite al gestor de renderizado con el anclaje correcto.
        Las subclases pueden sobreescribir este método para lógica adicional.
        """
        if self.sprite is None:
            return

        self._update_screen_coords()

        # Cálculo del punto de blit con la regla de anclaje geométrico:
        #   dest_x = screen_x - ancho  // 2  → centrado horizontal
        #   dest_y = screen_y - alto          → base del sprite en screen_y
        dest_x = self.screen_x - self.sprite.get_width()  // 2
        dest_y = self.screen_y - self.sprite.get_height()

        renderer.submit(self.sprite, dest_x, dest_y, self.sort_key)
