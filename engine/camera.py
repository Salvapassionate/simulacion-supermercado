# =============================================================================
# engine/camera.py
# Clase base de cámara isométrica con offset estático.
# Diseñada para ser extendida en el futuro con soporte de paneo y zoom.
# =============================================================================

from __future__ import annotations


class Camera:
    """
    Cámara base con desplazamiento estático en (0, 0).

    Por el momento retorna las coordenadas directas sin transformación.
    Para implementar paneo, modificar offset_x y offset_y en una subclase
    o mediante métodos de movimiento (pan, center_on, etc.).
    """

    def __init__(self, offset_x: int = 0, offset_y: int = 0) -> None:
        self.offset_x = offset_x
        self.offset_y = offset_y

    def apply(self, x: int, y: int) -> tuple[int, int]:
        """
        Aplica el offset de cámara a una coordenada de pantalla.
        En la versión base, retorna las coordenadas sin modificación.
        """
        return x + self.offset_x, y + self.offset_y

    def reset(self) -> None:
        """Reinicia la cámara a la posición de origen."""
        self.offset_x = 0
        self.offset_y = 0

    # -----------------------------------------------------------------------
    # Métodos stub para futura extensión (paneo y zoom)
    # -----------------------------------------------------------------------

    def pan(self, dx: int, dy: int) -> None:
        """Desplaza la cámara en dx, dy píxeles (para paneo con teclado/ratón)."""
        self.offset_x += dx
        self.offset_y += dy

    def center_on(self, screen_x: int, screen_y: int, win_w: int, win_h: int) -> None:
        """Centra la vista sobre un punto de pantalla específico."""
        self.offset_x = win_w // 2 - screen_x
        self.offset_y = win_h // 2 - screen_y
