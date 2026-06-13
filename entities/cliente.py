# =============================================================================
# entities/cliente.py
# Entidad móvil que representa a un cliente en la simulación.
# Implementa una máquina de estados de navegación con movimiento fluido.
# =============================================================================

from __future__ import annotations
import random
import pygame
from entities.entity_base import Entity
from engine.renderer import Renderer
from graphics.sprites import SpriteFactory
from engine.iso import to_iso, grid_distance


# Estados de la máquina de estados del cliente
ESTADO_SPAWN           = "SPAWN"
ESTADO_CAMINANDO       = "CAMINANDO_PASILLO"
ESTADO_ENTRANDO_COLA   = "ENTRANDO_A_COLA"
ESTADO_ESPERANDO_FILA  = "ESPERANDO_FILA"
ESTADO_SIENDO_ATENDIDO = "SIENDO_ATENDIDO"
ESTADO_SALIENDO        = "SALIENDO"


class Cliente(Entity):
    """
    Avatar de cliente con navegación en ángulo recto y movimiento fluido.

    El movimiento interpola las coordenadas lógicas gx, gy hacia el objetivo
    a una velocidad constante en celdas/segundo, multiplicada por dt para
    que sea independiente del framerate.
    """

    # Contador global de IDs de clientes
    _id_counter: int = 0

    def __init__(
        self,
        gx       : float,
        gy       : float,
        productos: int,
        velocidad: float = 2.5
    ) -> None:
        # Asignar ID único y color aleatorio por cliente
        Cliente._id_counter += 1
        self.id        = Cliente._id_counter
        self.color     = (
            random.randint(60, 230),
            random.randint(60, 230),
            random.randint(60, 230)
        )
        self.productos = productos
        self.velocidad = velocidad   # Celdas por segundo

        # Estado de la máquina de navegación
        self.estado     : str   = ESTADO_SPAWN
        self.target_gx  : float = gx
        self.target_gy  : float = gy
        self.waypoints  : list[tuple[float, float]] = []  # Lista de puntos de ruta

        # Índice del cajero asignado
        self.cajero_asignado : int | None = None

        # Métricas individuales de tiempo
        self.tiempo_llegada     : float = 0.0  # Momento en que entró al sistema
        self.tiempo_inicio_cola : float = 0.0  # Momento en que se unió a la cola
        self.tiempo_espera      : float = 0.0  # Tiempo total esperando en cola

        # Señal para que el QueueManager inicie el servicio
        self.listo_para_servicio : bool = False

        # En Cliente.__init__, junto a los otros atributos
        self.pos_cola_asignada: tuple[float, float] | None = None

        # Construir sprite inicial
        sprite = SpriteFactory.create_cliente(self.color, self.productos)

        super().__init__(gx=gx, gy=gy, gz=0.0, sprite=sprite)

    # -------------------------------------------------------------------------
    # Actualización de movimiento (delta-time independiente del framerate)
    # -------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        """
        Actualiza la posición del cliente interpolando hacia su objetivo.

        El desplazamiento máximo por frame es: velocidad * dt [celdas].
        Si el cliente llega al objetivo actual, avanza al siguiente waypoint.
        """
        if self.estado == ESTADO_ESPERANDO_FILA:
            return
        
        if not self.waypoints:
            return

        # Objetivo actual: primer waypoint de la lista
        target_gx, target_gy = self.waypoints[0]

        # Vector de desplazamiento hacia el objetivo
        dx = target_gx - self.gx
        dy = target_gy - self.gy
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist < 1e-4:
            # Llegó al waypoint actual: snap exacto y avanzar al siguiente
            self.gx = target_gx
            self.gy = target_gy
            self.waypoints.pop(0)

            # Verificar si ha llegado al destino final (sin más waypoints)
            if not self.waypoints:
                self._on_waypoints_done()
        else:
            # Interpolación: avanzar máximo velocidad * dt en dirección al objetivo
            step = min(self.velocidad * dt, dist)
            self.gx += (dx / dist) * step
            self.gy += (dy / dist) * step

        # Actualizar coordenadas de pantalla
        self._update_screen_coords()

        # Regenerar sprite si el número de productos cambió
        # (se actualiza al comenzar la atención, pero optimizamos solo cuando cambia)

    # cliente.py — _on_waypoints_done

    def _on_waypoints_done(self) -> None:
        if self.estado == ESTADO_CAMINANDO:
            # Llegó al final de la ruta principal → ya está en su posición de cola
            self.estado = ESTADO_ESPERANDO_FILA   # antes pasaba a ENTRANDO_COLA primero

        elif self.estado == ESTADO_ENTRANDO_COLA:
            self.estado = ESTADO_ESPERANDO_FILA

        elif self.estado == ESTADO_SIENDO_ATENDIDO:
            self.listo_para_servicio = True

    # -------------------------------------------------------------------------
    # Control de waypoints y estado
    # -------------------------------------------------------------------------

    def set_ruta(self, waypoints: list[tuple[float, float]]) -> None:
        """Asigna una ruta de navegación como lista de (gx, gy) a recorrer."""
        self.waypoints = list(waypoints)
        if self.estado == ESTADO_SPAWN:
            self.estado = ESTADO_CAMINANDO

    def mover_a_cola(self, pos_cola: tuple[float, float]) -> None:
        """Mueve al cliente directamente a la posición de espera en la cola."""
        self.waypoints = [pos_cola]
        self.estado    = ESTADO_ENTRANDO_COLA
    
    def mover_a_cajero(self, cajero_gx: float, cajero_gy: float) -> None:
        """
        Define la posición del mostrador como destino final.
        El servicio comenzará cuando el cliente llegue físicamente.
        """
        self.waypoints            = [(cajero_gx, cajero_gy - 1.0)]
        self.estado               = ESTADO_SIENDO_ATENDIDO
        self.listo_para_servicio  = False

    def iniciar_salida(self, exit_gx: float, exit_gy: float) -> None:
        """Envía al cliente hacia la salida."""
        self.waypoints = [(exit_gx, exit_gy)]
        self.estado    = ESTADO_SALIENDO

    @property
    def ha_llegado_al_destino(self) -> bool:
        """True si no quedan waypoints pendientes."""
        return len(self.waypoints) == 0

    # -------------------------------------------------------------------------
    # Renderizado
    # -------------------------------------------------------------------------

    def draw(self, renderer: Renderer) -> None:
        """Renderiza el cliente con su sprite actualizado."""
        # Regenerar sprite con el conteo de productos actualizado
        self.sprite = SpriteFactory.create_cliente(self.color, self.productos)
        super().draw(renderer)

    @classmethod
    def reset_counter(cls) -> None:
        """Reinicia el contador global de IDs (para reset de simulación)."""
        cls._id_counter = 0
