# =============================================================================
# config/settings.py
# Configuración global del proyecto "Simulación de Supermercado Retro 2.5D"
# Materia: TDS115 - Técnicas de Simulación | Universidad de El Salvador
# =============================================================================

# --- Dimensiones de la ventana principal ---
WIDTH       = 1550   # Ancho total de la ventana en píxeles
HEIGHT      = 750   # Alto total de la ventana en píxeles
FPS         = 60     # Fotogramas por segundo objetivo
SIDEBAR_W   = 420    # Ancho del panel lateral de métricas (interfaz 2D)

# Área activa de simulación isométrica (zona de renderizado del grid)
SIM_W = WIDTH - SIDEBAR_W   # = 1100 px

# --- Geometría isométrica estándar (proyección de 30 grados, proporción 2:1) ---
# El rombo base mide 64 px de ancho y 32 px de alto, garantizando la
# proporción matemática correcta: tan(30°) ≈ 0.577, aproximado a 0.5 con 2:1.
TILE_W = 64   # Ancho total del rombo isométrico (eje X visual)
TILE_H = 32   # Alto total del rombo isométrico (eje Y visual)

# --- Dimensiones lógicas del grid del supermercado ---
STORE_WIDTH  = 18   # Columnas lógicas del grid
STORE_HEIGHT = 16   # Aumentado para ampliar el piso de la tienda

# --- Centro de proyección isométrica ---
# Centra el piso perfectamente dentro de la zona de simulación SIM_W x HEIGHT.
# Se desplaza 50 px hacia arriba para dar espacio visual a las entidades altas.
ISO_CENTER_X = SIDEBAR_W + (WIDTH - SIDEBAR_W) // 2   # = 1100 // 2 + 300 = 850
ISO_CENTER_Y = HEIGHT // 2 - 200                       # Ajustado para centrar el layout ampliado

# --- Parámetros del modelo de colas M/M/c ---
MAX_CAJEROS         = 8    # Número máximo de servidores (cajeros) habilitados
MAX_COLA            = 10   # Longitud máxima de la cola por caja
TIEMPO_POR_PRODUCTO = 5   # Segundos de servicio base por cada producto del cliente

# --- Velocidad de movimiento de los clientes (en celdas por segundo) ---
VELOCIDAD_CLIENTE = 8

# --- Tasa de arribos base (segundos entre generaciones de clientes) ---
INTERVALO_ARRIBO = 3.0   # Promedio de segundos entre llegadas (proceso de Poisson)
