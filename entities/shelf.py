# =============================================================================
# entities/shelf.py
# Representa una góndola (estantería) estática bloqueante en el grid.
# =============================================================================

from __future__ import annotations
from entities.entity_base import Entity
from graphics.sprites import SpriteFactory


class Shelf(Entity):
    """
    Estante estático bloqueante.

    Los clientes no pueden atravesar celdas ocupadas por estantes.
    La verificación de colisión se realiza en el QueueManager durante
    la planificación de la ruta de navegación.
    """

    # Sprite compartido por todas las instancias (cache de clase)
    _shared_sprite = None

    def __init__(self, gx: int, gy: int) -> None:
        # Lazy-init del sprite compartido (requiere Pygame inicializado)
        if Shelf._shared_sprite is None:
            Shelf._shared_sprite = SpriteFactory.create_shelf()

        super().__init__(
            gx     = gx,
            gy     = gy,
            gz     = 0.0,
            sprite = Shelf._shared_sprite
        )

    @classmethod
    def reset_cache(cls) -> None:
        """Invalida el cache del sprite (útil al reiniciar la simulación)."""
        cls._shared_sprite = None
