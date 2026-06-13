# =============================================================================
# graphics/floor.py
# Renderizado del piso isométrico ajedrezado.
# Recorre el grid lógico y dibuja rombos con patrón bicolor retro.
# =============================================================================

import pygame
from engine.iso import to_iso
from config.settings import STORE_WIDTH, STORE_HEIGHT, TILE_W, TILE_H
from config.colors import TILE_A, TILE_B, TILE_BORDER

COLOR_ACERA = (140, 145, 150)       # Gris concreto exterior
COLOR_CALLE = (90, 95, 100)         # Gris oscuro asfalto
COLOR_LINEA_MALL = (180, 185, 190)  # Detalle de acera


class IsoFloor:
    """
    Genera y dibuja la cuadrícula del piso isométrico.

    El piso se prerenderiza en una superficie de cache durante la inicialización
    para no recalcular los polígonos cada frame (optimización de rendimiento).
    """

    def __init__(self) -> None:
        # Pre-renderizamos el piso completo una sola vez en un Surface de cache
        self._cache: pygame.Surface | None = None

    def _build_cache(self, target_size: tuple[int, int]) -> None:
        """
        Construye la superficie de cache del piso.
        Se llama en el primer draw() para asegurar que Pygame está inicializado.
        """
        self._cache = pygame.Surface(target_size, pygame.SRCALPHA)
        self._draw_grid(self._cache)

    def _draw_grid(self, surface: pygame.Surface) -> None:
        """
        Recorre las celdas del layout. Si es exterior pinta entorno urbano,
        si es interior pinta el clásico ajedrezado.
        """
        from maps.store_layout import STORE_LAYOUT

        for gy in range(STORE_HEIGHT):
            for gx in range(STORE_WIDTH):
                cx, cy = to_iso(gx, gy)

                pts = [
                    (cx,               cy - TILE_H // 2),
                    (cx + TILE_W // 2, cy),
                    (cx,               cy + TILE_H // 2),
                    (cx - TILE_W // 2, cy),
                ]

                # Obtener qué tipo de celda es según nuestro plano
                tipo_celda = STORE_LAYOUT[gy][gx]

                if tipo_celda in ('A', 'E', 'X'):
                    # --- RENDER DE ENTORNO EXTERIOR (Centro Comercial / Calle) ---
                    color_suelo = COLOR_CALLE if gy == 0 and gx > 14 else COLOR_ACERA
                    pygame.draw.polygon(surface, color_suelo, pts)
                    # Líneas de división exteriores señeras
                    pygame.draw.polygon(surface, COLOR_LINEA_MALL, pts, 1)
                else:
                    # --- RENDER INTERIOR DEL SUPERMERCADO ---
                    tile_color = TILE_A if (gx + gy) % 2 == 0 else TILE_B
                    pygame.draw.polygon(surface, tile_color, pts)
                    pygame.draw.polygon(surface, TILE_BORDER, pts, 1)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Dibuja el piso prerenderizado sobre la superficie destino.
        Construye el cache en el primer llamado.
        """
        if self._cache is None:
            self._build_cache(surface.get_size())

        surface.blit(self._cache, (0, 0))
