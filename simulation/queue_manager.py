# =============================================================================
# simulation/queue_manager.py
# =============================================================================

from __future__ import annotations
from entities.cliente import (
    Cliente,
    ESTADO_SPAWN,
    ESTADO_CAMINANDO,
    ESTADO_ENTRANDO_COLA,
    ESTADO_ESPERANDO_FILA,
    ESTADO_SIENDO_ATENDIDO,
    ESTADO_SALIENDO
)
from entities.cajero import Cajero
from maps.store_layout import is_walkable, STORE_LAYOUT
from config.settings import MAX_COLA, MAX_CAJEROS
from engine.iso import grid_distance

# Máximo de clientes por cola de cajero
MAX_COLA_CAJERO   = 5
# Columna y rango de filas de la zona de espera en entrada
ENTRADA_GX        = 16
ENTRADA_GY_MIN    = 1
ENTRADA_GY_MAX    = 12
MAX_ESPERA_ENTRADA = ENTRADA_GY_MAX - ENTRADA_GY_MIN + 1   # 12 slots


class QueueManager:
    """
    Gestor central de colas y flujo de atención.

    Añade una zona de espera física en la entrada (gx=16, gy=1-12).
    Cuando todas las colas de cajeros están llenas (MAX_COLA_CAJERO),
    los clientes se acumulan allí ordenados por orden de llegada.
    Cuando se libera espacio en algún cajero, el primero en espera
    es asignado automáticamente.
    """

    def __init__(self, cajeros: list[Cajero], spawn_gx: int, spawn_gy: int) -> None:
        self.cajeros   = cajeros
        self.spawn_gx  = spawn_gx
        self.spawn_gy  = spawn_gy

        # Cola de espera en la entrada — orden FIFO
        # Cada elemento es un Cliente esperando ser asignado a un cajero
        self.cola_entrada: list[Cliente] = []

    # -------------------------------------------------------------------------
    # 1. Asignación de cajero (Shortest Queue Algorithm)
    # -------------------------------------------------------------------------

    def asignar_cajero(self, cliente: Cliente, sim_time: float) -> bool:
        """
        Intenta asignar al cliente la caja con menor carga.

        Si todas las colas están en MAX_COLA_CAJERO pero hay espacio
        en la zona de entrada, el cliente espera allí.

        Returns True si el cliente fue admitido al sistema (cajero o entrada).
        Returns False si tanto las colas como la entrada están llenas.
        """
        mejor_cajero = self._buscar_mejor_cajero()

        if mejor_cajero is not None:
            self._asignar_a_cajero(cliente, mejor_cajero, sim_time)
            return True

        # Colas llenas: intentar encolar en la entrada
        if len(self.cola_entrada) < MAX_ESPERA_ENTRADA:
            self._encolar_en_entrada(cliente, sim_time)
            return True

        # Sistema saturado
        return False

    def _buscar_mejor_cajero(self) -> Cajero | None:
        """Devuelve el cajero con menor carga que no supere MAX_COLA_CAJERO."""
        mejor_cajero = None
        menor_carga  = MAX_COLA_CAJERO + 1

        for cajero in self.cajeros:
            carga = len(cajero.cola) + (1 if cajero.ocupado else 0)
            if carga < menor_carga:
                menor_carga  = carga
                mejor_cajero = cajero

        # None si todos superan o igualan MAX_COLA_CAJERO
        if mejor_cajero is not None and menor_carga >= MAX_COLA_CAJERO:
            return None
        return mejor_cajero

    def _asignar_a_cajero(
        self, cliente: Cliente, cajero: Cajero, sim_time: float
    ) -> None:
        cajero.cola.append(cliente)
        indice_en_cola = len(cajero.cola)
        pos_en_cola    = self._calcular_posicion_cola(cajero, indice_en_cola)
        ruta = self._planificar_ruta(
            inicio  = (cliente.gx, cliente.gy),
            destino = pos_en_cola
        )
        cliente.set_ruta(ruta)
        cliente.pos_cola_asignada  = pos_en_cola
        cliente.tiempo_inicio_cola = sim_time
        cliente.cajero_asignado    = cajero.indice

    def _encolar_en_entrada(self, cliente: Cliente, sim_time: float) -> None:
        """Coloca al cliente en la zona de espera física de la entrada."""
        self.cola_entrada.append(cliente)
        pos = self._calcular_posicion_entrada(len(self.cola_entrada))
        ruta = self._planificar_ruta(
            inicio  = (cliente.gx, cliente.gy),
            destino = pos
        )
        cliente.set_ruta(ruta)
        cliente.pos_cola_asignada  = pos
        cliente.tiempo_inicio_cola = sim_time

    def _calcular_posicion_entrada(self, posicion_1based: int) -> tuple[float, float]:
        """
        Posición física en la columna de entrada.
        posicion=1 → gy=1 (más cercano al spawn), posicion=12 → gy=12.
        """
        gy = ENTRADA_GY_MIN + (posicion_1based - 1)
        gy = min(gy, ENTRADA_GY_MAX)
        return (float(ENTRADA_GX), float(gy))

    def _calcular_posicion_cola(
        self, cajero: Cajero, posicion_en_fila: int
    ) -> tuple[float, float]:
        return (float(cajero.gx), cajero.gy - posicion_en_fila)

    # -------------------------------------------------------------------------
    # 2. Planificación de ruta ortogonal
    # -------------------------------------------------------------------------

    def _planificar_ruta(
        self,
        inicio  : tuple[float, float],
        destino : tuple[float, float]
    ) -> list[tuple[float, float]]:
        ix, iy = int(round(inicio[0])),  int(round(inicio[1]))
        dx, dy = int(round(destino[0])), int(round(destino[1]))

        pasillos_y = self._encontrar_pasillos_horizontales()
        waypoints: list[tuple[float, float]] = []

        pasillo_objetivo = self._pasillo_mas_cercano(iy, dy, pasillos_y)

        if pasillo_objetivo != iy:
            waypoints.append((float(ix), float(pasillo_objetivo)))

        if ix != dx:
            waypoints.append((float(dx), float(pasillo_objetivo)))

        waypoints.append((float(dx), float(dy)))
        return waypoints

    def _encontrar_pasillos_horizontales(self) -> list[int]:
        pasillos = []
        for gy, row in enumerate(STORE_LAYOUT):
            if all(cell != 'S' for cell in row):
                pasillos.append(gy)
        return pasillos

    def _pasillo_mas_cercano(
        self, gy_origen: int, gy_destino: int, pasillos: list[int]
    ) -> int:
        if not pasillos:
            return gy_origen

        entre = [
            p for p in pasillos
            if min(gy_origen, gy_destino) <= p <= max(gy_origen, gy_destino)
        ]

        if entre:
            return min(entre, key=lambda p: abs(p - gy_destino))

        return min(pasillos, key=lambda p: abs(p - gy_destino))

    # -------------------------------------------------------------------------
    # 3. Actualización del flujo de atención
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 3. Actualización del flujo de atención
    # -------------------------------------------------------------------------

    def update(self, dt: float, sim_time: float, metrics) -> None:
        for cajero in self.cajeros:
            # 1. Actualizar el temporizador del cajero
            servicio_terminado = cajero.actualizar(dt)

            # Si el servicio terminó en este frame, liberamos la posición física sacándolo de la cola
            if servicio_terminado:
                if cajero.cola:
                    # El cliente que acaba de terminar era el que estaba al frente
                    cajero.cola.pop(0)
                
                # avanza físicamente un paso al resto de la fila
                self._reposicionar_cola(cajero)
                
                # Intentar rellenar el espacio vacío promoviendo a alguien desde la entrada
                self._promover_desde_entrada(cajero, sim_time)

            # 2. Iniciar servicio si el cajero está completamente libre y hay alguien esperando
            if not cajero.ocupado and cajero.cola:
                siguiente = cajero.cola[0]

                #  Solo se inicia el servicio si el cliente ya llegó físicamente a la caja
                # y no ha iniciado su atención.
                if siguiente.estado == ESTADO_ESPERANDO_FILA:
                    duracion = cajero.calcular_duracion_servicio(siguiente.productos)
                    siguiente.tiempo_espera = sim_time - siguiente.tiempo_inicio_cola
                    siguiente.mover_a_cajero(cajero.gx, cajero.gy)
                    cajero.iniciar_servicio(siguiente, duracion)

    def _promover_desde_entrada(self, cajero: Cajero, sim_time: float) -> None:
        """
        Si hay clientes esperando en la entrada y el cajero tiene espacio,
        asigna al primero de la fila de entrada.
        """
        if not self.cola_entrada:
            return

        carga = len(cajero.cola) + (1 if cajero.ocupado else 0)
        if carga >= MAX_COLA_CAJERO:
            return

        cliente = self.cola_entrada.pop(0)
        self._asignar_a_cajero(cliente, cajero, sim_time)

        # Reposicionar al resto de la cola de entrada
        self._reposicionar_entrada()

    def _reposicionar_entrada(self) -> None:
        """Actualiza posiciones físicas de los clientes en la zona de entrada."""
        for i, cliente in enumerate(self.cola_entrada):
            nueva_pos = self._calcular_posicion_entrada(i + 1)
            cliente.pos_cola_asignada = nueva_pos

            if cliente.estado == ESTADO_ESPERANDO_FILA:
                cliente.mover_a_cola(nueva_pos)
            elif cliente.estado in (ESTADO_CAMINANDO, ESTADO_ENTRANDO_COLA):
                if cliente.waypoints:
                    cliente.waypoints[-1] = nueva_pos
                else:
                    cliente.waypoints = [nueva_pos]
                    cliente.estado = ESTADO_ENTRANDO_COLA

    def _reposicionar_cola(self, cajero: Cajero) -> None:
        for i, cliente in enumerate(cajero.cola):
            nueva_pos = self._calcular_posicion_cola(cajero, i + 1)
            cliente.pos_cola_asignada = nueva_pos

            if cliente.estado == ESTADO_ESPERANDO_FILA:
                cliente.mover_a_cola(nueva_pos)
            elif cliente.estado in (ESTADO_CAMINANDO, ESTADO_ENTRANDO_COLA):
                if cliente.waypoints:
                    cliente.waypoints[-1] = nueva_pos
                else:
                    cliente.waypoints = [nueva_pos]
                    cliente.estado = ESTADO_ENTRANDO_COLA

    def procesar_salida(
        self, cliente: Cliente, exit_gx: float, exit_gy: float
    ) -> None:
        cliente.iniciar_salida(exit_gx, exit_gy)