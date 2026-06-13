# =============================================================================
# entities/wall.py
# Representa un bloque de pared estática elevada en el borde del plano.
# =============================================================================

from __future__ import annotations
from entities.entity_base import Entity
from graphics.sprites import SpriteFactory
from maps.store_layout import STORE_LAYOUT


class Wall(Entity):
    """
    Pared estructural limítrofe del centro comercial.
    Incluye corrección de profundidad isométrica para evitar solapamientos.
    """
    _shared_sprite = None

    def __init__(self, gx: int, gy: int) -> None:
        if Wall._shared_sprite is None:
            Wall._shared_sprite = SpriteFactory.create_wall()

        # Determinamos si es una pared de la esquina superior o del extremo derecho
        # para aplicar un ajuste sutil en el eje Z de renderizado.
        # Esto sumerge la base del bloque lo suficiente para que las góndolas 
        # adyacentes pasen al frente en el Y-Sort.
        es_borde_derecho = (gx >= len(STORE_LAYOUT[0]) - 3)
        ajuste_profundidad = -0.5 if es_borde_derecho else 0.0

        super().__init__(
            gx     = gx,
            gy     = gy,
            gz     = ajuste_profundidad,  # ◄── Ajuste de eje Z dinámico
            sprite = Wall._shared_sprite
        )

    @classmethod
    def reset_cache(cls) -> None:
        cls._shared_sprite = None