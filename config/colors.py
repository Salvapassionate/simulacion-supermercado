# =============================================================================
# config/colors.py
# Paleta de colores del proyecto. Estética retro inspirada en Theme Hospital
# y juegos de estrategia/simulación de PC de los años 90.
# =============================================================================

# --- Colores base de la interfaz ---
BG_COLOR      = (18, 20, 28)       # Fondo general: negro-azul oscuro
SIDEBAR_COLOR = (28, 32, 48)       # Panel lateral: gris-azul retro profundo
TEXT_COLOR    = (220, 215, 195)    # Texto general: beige cálido legible
ACCENT_COLOR  = (255, 200, 50)     # Acento: amarillo/dorado pixel-art
SHADOW_COLOR  = (0, 0, 0, 120)     # Sombra proyectada: negro con alpha

# --- Colores del piso isométrico (patrón ajedrezado retro) ---
TILE_A = (195, 190, 178)           # Baldosa clara: beige grisáceo
TILE_B = (175, 170, 158)           # Baldosa oscura: gris complementario
TILE_BORDER = (140, 136, 128)      # Borde perimetral de los mosaicos

# --- Colores de entidades ---
SHELF_TOP    = (80, 95, 115)       # Cara superior de la góndola (azul-gris)
SHELF_FRONT  = (55, 68, 85)        # Cara frontal de la góndola (más oscura)
SHELF_SIDE   = (65, 80, 100)       # Cara lateral de la góndola
SHELF_PLANK  = (100, 115, 135)     # Estantes horizontales internos

CAJERO_FREE  = (60, 180, 80)       # Indicador cajero libre: verde
CAJERO_BUSY  = (220, 60, 60)       # Indicador cajero ocupado: rojo
CAJERO_TOP   = (90, 80, 70)        # Superficie del mostrador (madera oscura)
CAJERO_FRONT = (70, 60, 50)        # Frente del mostrador
CAJERO_SIDE  = (80, 70, 58)        # Lateral del mostrador
SCREEN_GREEN = (60, 220, 100)      # Pantalla CRT verde retro

# --- Colores de la barra de progreso del cajero ---
PROGRESS_BG  = (40, 40, 40)        # Fondo de la barra de progreso
PROGRESS_OK  = (80, 200, 100)      # Progreso activo: verde
PROGRESS_LOW = (220, 140, 40)      # Progreso bajo: naranja
PROGRESS_END = (220, 60, 60)       # Casi terminado: rojo

# --- Colores de la piel del avatar cliente ---
SKIN_COLOR  = (230, 185, 140)      # Color piel cabeza
LEGS_COLOR  = (45, 45, 65)         # Piernas: azul-gris oscuro (pantalón)
BUBBLE_BG   = (20, 20, 30, 200)    # Fondo del indicador de productos (alpha)
BUBBLE_TEXT = (255, 220, 60)       # Texto del indicador de productos

# --- Colores de la UI sidebar ---
PANEL_DIVIDER = (55, 62, 85)       # Líneas separadoras del panel
METRIC_LABEL  = (140, 155, 185)    # Etiquetas de métricas (gris-azul)
METRIC_VALUE  = (255, 210, 60)     # Valores de métricas (amarillo)
HELP_COLOR    = (100, 120, 150)    # Texto de ayuda/leyenda
TITLE_COLOR   = (255, 230, 100)    # Título del panel
