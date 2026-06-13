# Simulación de Supermercado Retro 2.5D

**Materia:** TDS115 - Técnicas de Simulación  
**Universidad de El Salvador**  
**Motor:** Python 3.10+ / Pygame 2.5+  
**Estética:** Pixel-art isométrico inspirado en Theme Hospital / The Sims 1

---

## Descripción

Simulación discreta de un supermercado modelada con colas **M/M/c** sobre un
entorno isométrico 2.5D generado completamente en memoria (sin recursos externos).

### Características técnicas implementadas

- Proyección isométrica estándar 2:1 (30 grados) con fórmulas exactas.
- Sistema Y-Sort basado en coordenadas lógicas del grid (sin parpadeos).
- Sprites pixel-art procedurales con canal alfa (Pygame SRCALPHA).
- Navegación ortogonal anti-diagonal: los clientes nunca atraviesan góndolas.
- Movimiento fluido interpolado por delta-time (independiente del FPS).
- Flujo de atención físico: sin teleportación al mostrador.
- Panel lateral con métricas en tiempo real.

---

## Estructura del proyecto

```
supermarket_sim/
├── main.py                         ← Punto de entrada
├── requirements.txt
├── config/
│   ├── settings.py                 ← Parámetros globales (resolución, grid, colas)
│   └── colors.py                   ← Paleta de colores retro
├── engine/
│   ├── iso.py                      ← Transformaciones isométricas (to_iso / from_iso)
│   ├── sorting.py                  ← Sistema Y-Sort por clave lógica de grid
│   ├── renderer.py                 ← Gestor de renderizado por frame
│   └── camera.py                   ← Cámara base (extensible a paneo/zoom)
├── graphics/
│   ├── sprites.py                  ← Fábrica procedural de sprites pixel-art
│   ├── floor.py                    ← Renderizado del piso isométrico ajedrezado
│   └── ui.py                       ← Panel lateral 2D de métricas
├── entities/
│   ├── entity_base.py              ← Clase base con anclaje geométrico correcto
│   ├── shelf.py                    ← Góndola estática bloqueante
│   ├── cajero.py                   ← Servidor M/M/c con overlay de progreso
│   └── cliente.py                  ← Avatar móvil con máquina de estados
├── maps/
│   └── store_layout.py             ← Mapa 2D (E/S/C/.)
└── simulation/
    ├── metrics.py                  ← Consolidación de métricas estadísticas
    ├── arrival_system.py           ← Proceso de Poisson (distribución exponencial)
    ├── queue_manager.py            ← Algoritmo Shortest Queue + navegación ortogonal
    └── supermarket.py              ← Orquestador central de la simulación
```

---

## Instalación y ejecución

```bash
# 1. Clonar o extraer el proyecto
cd supermarket_sim

# 2. Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate.bat       # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
python main.py
```

**Requisitos mínimos:** Python 3.10 · Pygame 2.5 · 60 FPS estables

---

## Controles

| Tecla | Acción |
|-------|--------|
| `ESC` | Cerrar la aplicación |
| `F1`  | Inyectar un cliente manualmente |
| `R`   | Reiniciar toda la simulación |

---

## Parámetros ajustables (`config/settings.py`)

| Parámetro           | Valor por defecto | Descripción                          |
|---------------------|-------------------|--------------------------------------|
| `MAX_CAJEROS`       | 8                 | Número de servidores activos         |
| `MAX_COLA`          | 10                | Longitud máxima de cola por caja     |
| `TIEMPO_POR_PRODUCTO` | 10 s            | Segundos de servicio por producto    |
| `VELOCIDAD_CLIENTE` | 2.5 cel/s         | Velocidad de movimiento de clientes  |
| `INTERVALO_ARRIBO`  | 3.0 s             | Tiempo promedio entre llegadas       |

---

## Modelo de colas implementado

**M/M/c** con:
- **λ** (tasa de llegadas): configurable mediante `INTERVALO_ARRIBO`
- **μ** (tasa de servicio): determinada por `productos × TIEMPO_POR_PRODUCTO`
- **c** (servidores): determinado por `MAX_CAJEROS`
- **Capacidad del sistema**: `MAX_COLA` por servidor
- **Disciplina de cola**: FIFO + Shortest Queue al arribo
