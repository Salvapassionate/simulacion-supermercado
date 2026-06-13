# =============================================================================
# simulation/supermarket.py
# =============================================================================

from __future__ import annotations
import random
from maps.store_layout import (
    STORE_LAYOUT, find_spawn, find_exit, find_cajeros, find_shelves, is_walkable
)
from entities.shelf    import Shelf
from entities.wall     import Wall  # ◄── PASO 5: Importamos la nueva entidad de Pared
from entities.cajero   import Cajero
from entities.cliente  import (
    Cliente,
    ESTADO_SALIENDO, ESTADO_SIENDO_ATENDIDO, ESTADO_ENTRANDO_COLA, ESTADO_ESPERANDO_FILA
)
from simulation.metrics        import Metrics
from simulation.arrival_system import ArrivalSystem
from simulation.queue_manager  import QueueManager
from config.settings import MAX_CAJEROS, VELOCIDAD_CLIENTE, INTERVALO_ARRIBO


class Supermarket:
    """
    Clase central que orquesta todos los componentes de la simulación.

    config keys:
        "cajeros_activos"  : int   — cuántos cajeros instanciar
        "tiempos_cajero"   : list  — segundos/producto por cajero
        "duracion"         : float — segundos totales de simulación (0 = infinito)
    """

    def __init__(self, config: dict | None = None) -> None:
        if config is None:
            config = {
                "cajeros_activos": MAX_CAJEROS,
                "tiempos_cajero": [2] * MAX_CAJEROS,
                "duracion": 0.0
            }

        cajeros_activos : int   = config.get("cajeros_activos", MAX_CAJEROS)
        tiempos_cajero  : list  = config.get("tiempos_cajero",  [5] * MAX_CAJEROS)
        duracion        : float = float(config.get("duracion", 0.0))

        self._config = config

        # ── Reloj y límite de tiempo ──────────────────────────────────────────
        self.metrics         = Metrics()
        self.sim_time        = 0.0
        self.duracion        = duracion       # 0 = sin límite
        self.arribos_activos  = True   # False cuando se acaba el tiempo
        self.sim_terminada    = False  # True cuando no quedan clientes
        self._tiempo_vaciando = 0.0   # Segundos transcurridos desde que se detuvieron arribos

        # ── Coordenadas de spawn y salida ─────────────────────────────────────
        spawn = find_spawn()
        self.spawn_gx : int = spawn[0]
        self.spawn_gy : int = spawn[1]

        exit_pos = find_exit()
        self.exit_gx : float = float(exit_pos[0])
        self.exit_gy : float = float(exit_pos[1])

        # ── Entidades estáticas y dinámicas ───────────────────────────────────
        self.static_entities : list = []  # ◄── Lista unificada para Paredes y Estantes
        self.cajeros         : list[Cajero]  = []
        self.clientes        : list[Cliente] = []

        # ◄── PASO 5: Recorremos todo el plano para instanciar tanto 'S' como 'W'
        for gy, row in enumerate(STORE_LAYOUT):
            for gx, cell in enumerate(row):
                if cell == 'S':
                    self.static_entities.append(Shelf(gx, gy))
                elif cell == 'W':
                    self.static_entities.append(Wall(gx, gy))

        cajero_positions = find_cajeros()[:cajeros_activos]
        for indice, (gx, gy) in enumerate(cajero_positions):
            t = tiempos_cajero[indice] if indice < len(tiempos_cajero) else 10
            self.cajeros.append(Cajero(indice, gx, gy, tiempo_por_producto=float(t)))

        # ── Subsistemas ───────────────────────────────────────────────────────
        self.arrival_system = ArrivalSystem(intervalo_base=INTERVALO_ARRIBO)
        self.queue_manager  = QueueManager(
            cajeros  = self.cajeros,
            spawn_gx = self.spawn_gx,
            spawn_gy = self.spawn_gy
        )

        Cliente.reset_counter()

    # -------------------------------------------------------------------------
    # Actualización frame a frame
    # -------------------------------------------------------------------------

    def update(self, dt: float) -> None:
        if self.sim_terminada:
            return

        self.sim_time += dt

        if self.duracion > 0 and self.sim_time >= self.duracion:
            self.sim_time        = self.duracion
            self.arribos_activos = False

        if not self.arribos_activos:
            self._tiempo_vaciando += dt
            clientes_en_cajeros = any(cajero.cola or cajero.ocupado for cajero in self.cajeros)
            sistema_vacio = (
                not self.clientes
                and not self.queue_manager.cola_entrada
                and not clientes_en_cajeros
            )
            if sistema_vacio or self._tiempo_vaciando > 120.0:
                self.sim_terminada = True
                return

        if self.arribos_activos:
            self.arrival_system.update(dt)
            if self.arrival_system.debe_generar:
                self.arrival_system.reset_flag()
                self._generar_cliente()

        self.queue_manager.update(dt, self.sim_time, self.metrics)

        for cliente in self.clientes:
            cliente.update(dt)

        self._procesar_llegadas_a_cola()
        self._procesar_servicios_completados()
        self._limpiar_clientes_salidos()

    # -------------------------------------------------------------------------
    # Generación de clientes
    # -------------------------------------------------------------------------

    def _generar_cliente(self) -> None:
        productos = self.arrival_system.generar_productos(1, 18)

        nuevo = Cliente(
            gx        = float(self.spawn_gx),
            gy        = float(self.spawn_gy),
            productos = productos,
            velocidad = VELOCIDAD_CLIENTE
        )
        nuevo.tiempo_llegada = self.sim_time

        asignado = self.queue_manager.asignar_cajero(nuevo, self.sim_time)

        if asignado:
            self.clientes.append(nuevo)
            self.metrics.registrar_llegada()
        else:
            self.metrics.registrar_rechazo()

    def forzar_cliente(self) -> None:
        self._generar_cliente()

    # -------------------------------------------------------------------------
    # Procesamiento de estados
    # -------------------------------------------------------------------------

    def _procesar_llegadas_a_cola(self) -> None:
        for cliente in self.clientes:
            if cliente.estado == ESTADO_ENTRANDO_COLA and cliente.ha_llegado_al_destino:
                cliente.estado = ESTADO_ESPERANDO_FILA

    def _procesar_servicios_completados(self) -> None:
        for cliente in self.clientes:
            if (
                cliente.estado == ESTADO_SIENDO_ATENDIDO
                and cliente.ha_llegado_al_destino
                and not cliente.listo_para_servicio
            ):
                cajero = self._cajero_del_cliente(cliente)

                if (
                    cajero
                    and not cajero.ocupado
                    and cajero.cliente_activo is None
                ):
                    self.queue_manager.procesar_salida(
                        cliente,
                        self.exit_gx,
                        self.exit_gy
                    )

    def _cajero_del_cliente(self, cliente: Cliente) -> Cajero | None:
        if cliente.cajero_asignado is None: 
            return None
        for cajero in self.cajeros:
            if cajero.indice == cliente.cajero_asignado:
                return cajero
        return None

    def _limpiar_clientes_salidos(self) -> None:
        restantes = []
        for cliente in self.clientes:
            if (
                cliente.estado == ESTADO_SALIENDO
                and cliente.ha_llegado_al_destino
            ):
                self.metrics.registrar_salida(cliente, self.sim_time)
                continue
            restantes.append(cliente)
        self.clientes = restantes

    # -------------------------------------------------------------------------
    # Tiempo restante (para la UI)
    # -------------------------------------------------------------------------

    @property
    def tiempo_restante(self) -> float:
        if self.duracion <= 0:
            return -1.0
        if not self.arribos_activos:
            return 0.0
        return max(0.0, self.duracion - self.sim_time)

    # -------------------------------------------------------------------------
    # Acceso para el renderizador
    # -------------------------------------------------------------------------

    def get_all_entities(self) -> list:
        # ◄── PASO 5: Unimos las estructuras estáticas (Paredes + Estantes) con Cajeros y Clientes
        return list(self.static_entities) + list(self.cajeros) + list(self.clientes)

    def reset(self) -> None:
        # ◄── PASO 5: Limpiamos los cachés estáticos al reiniciar
        Shelf.reset_cache()
        Wall.reset_cache()
        self.__init__(config=self._config)