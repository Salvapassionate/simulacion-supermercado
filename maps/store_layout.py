# =============================================================================
# maps/store_layout.py
# =============================================================================

# Leyenda de caracteres ampliada:
#   'E' → Entrada de clientes (Acera exterior)
#   'X' → Salida del supermercado (Acera exterior)
#   'W' → Pared alta estructural (Bloqueante)
#   'A' → Acera / Entorno exterior del Centro Comercial
#   'S' → Celda ocupada por estantería (Bloqueante)
#   'C' → Terminal de cobro (Servidor)
#   '.' → Espacio peatonal libre interno (Transitable)

STORE_LAYOUT = [
    # gx: 0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17
    [  'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'A', 'E', 'X'  ], # gy=0 (Exterior/Entrada)
    [  'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', 'W', '.', '.'  ], # gy=1 (Línea de Paredes traseras)
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=2
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=3
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=4
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=5
    [  'W', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'  ], # gy=6
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=7
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=8
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=9
    [  'W', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.', 'S', 'S', '.', '.'  ], # gy=10
    [  'W', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'  ], # gy=11
    [  'W', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'  ], # gy=12
    [  'W', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'  ], # gy=13
    [  'W', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'  ], # gy=14
    [  'W', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'  ], # gy=15
    [  'W', '.', 'C', '.', 'C', '.', 'C', '.', 'C', '.', 'C', '.', 'C', '.', 'C', '.', 'C', '.'  ], # gy=16
    [  'W', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.', '.'  ], # gy=17
]

def find_spawn() -> tuple[int, int]:
    for gy, row in enumerate(STORE_LAYOUT):
        for gx, cell in enumerate(row):
            if cell == 'E': return gx, gy
    return 16, 0

def find_cajeros() -> list[tuple[int, int]]:
    return [(gx, gy) for gy, row in enumerate(STORE_LAYOUT) for gx, cell in enumerate(row) if cell == 'C']

def find_shelves() -> list[tuple[int, int]]:
    return [(gx, gy) for gy, row in enumerate(STORE_LAYOUT) for gx, cell in enumerate(row) if cell == 'S']

def is_walkable(gx: int, gy: int) -> bool:
    if gy < 0 or gy >= len(STORE_LAYOUT) or gx < 0 or gx >= len(STORE_LAYOUT[0]):
        return False
    # Ahora NI las estanterías ('S') NI las paredes ('W') se pueden atravesar
    return STORE_LAYOUT[gy][gx] not in ('S', 'W')

def find_exit() -> tuple[int, int]:
    for gy, row in enumerate(STORE_LAYOUT):
        for gx, cell in enumerate(row):
            if cell == 'X': return gx, gy
    return 17, 0