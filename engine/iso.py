# =============================================================================
# engine/iso.py
# Motor matemático de transformación entre espacio de grid lógico y pantalla.
# Implementa proyección isométrica estándar de 30 grados (proporción 2:1).
# =============================================================================

from config.settings import ISO_CENTER_X, ISO_CENTER_Y, TILE_W, TILE_H


def to_iso(gx: float, gy: float, gz: float = 0) -> tuple[int, int]:
    """
    Transforma coordenadas del grid lógico (gx, gy, gz) a coordenadas
    de pantalla isométricas (sx, sy).

    Fórmulas estándar de proyección isométrica 2:1:
        sx = centro_x + (gx - gy) * (TILE_W / 2)
        sy = centro_y + (gx + gy) * (TILE_H / 2) - (gz * TILE_H)

    El eje gz eleva verticalmente los objetos con altura (en unidades de tile).
    Retorna coordenadas enteras para evitar artefactos de sub-píxel.
    """
    sx = ISO_CENTER_X + (gx - gy) * (TILE_W // 2)
    sy = ISO_CENTER_Y + (gx + gy) * (TILE_H // 2) - (gz * TILE_H)
    return int(sx), int(sy)


def from_iso(sx: int, sy: int) -> tuple[float, float]:
    """
    Desproyección inversa: transforma coordenadas de pantalla (sx, sy) de
    regreso a coordenadas del grid lógico (gx, gy).

    Invirtiendo el sistema de ecuaciones de to_iso (gz=0):
        sx - cx = (gx - gy) * (TILE_W / 2)   =>  A = (sx - cx) / (TILE_W / 2)
        sy - cy = (gx + gy) * (TILE_H / 2)   =>  B = (sy - cy) / (TILE_H / 2)

        gx = (A + B) / 2
        gy = (B - A) / 2
    """
    # Desplazamiento normalizado respecto al centro de proyección
    dx = (sx - ISO_CENTER_X) / (TILE_W / 2)
    dy = (sy - ISO_CENTER_Y) / (TILE_H / 2)

    gx = (dx + dy) / 2
    gy = (dy - dx) / 2

    return gx, gy


def grid_distance(ax: float, ay: float, bx: float, by: float) -> float:
    """
    Calcula la distancia euclídea entre dos puntos en el espacio del grid lógico.
    Utilizado para detectar la llegada de un cliente a su destino.
    """
    return ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
