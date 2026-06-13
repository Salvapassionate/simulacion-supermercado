# =============================================================================
# entities/cajero.py
# Representa una estación de cobro (servidor del modelo M/M/c).
# Administra el estado de atención, la cola de espera y el overlay visual.
# =============================================================================

from __future__ import annotations
import pygame
from entities.entity_base import Entity
from graphics.sprites import SpriteFactory
from engine.renderer import Renderer
from config.colors import (
    PROGRESS_BG, PROGRESS_OK, PROGRESS_LOW, PROGRESS_END,
    ACCENT_COLOR, TEXT_COLOR
)


class Cajero(Entity):
    """
    Servidor de atención isométrico.

    Mantiene:
        - Estado de ocupación (ocupado / libre).
        - Cola de espera de clientes asignados.
        - Referencia al cliente actualmente en servicio.
        - Temporizador de progreso de la atención actual.
        - Idle time acumulado (tiempo que el cajero estuvo sin atender).
        - Tiempo de servicio por producto configurable individualmente.
    """

    def __init__(
        self,
        indice              : int,
        gx                  : int,
        gy                  : int,
        tiempo_por_producto : float = 10.0
    ) -> None:
        self.indice  : int  = indice
        self.ocupado : bool = False
        self.cola    : list = []

        # Tiempo de servicio base por producto (configurable desde la pantalla de inicio)
        self.tiempo_por_producto : float = tiempo_por_producto

        # Cliente actualmente en servicio
        self.cliente_activo = None

        # Temporizador de servicio actual
        self.tiempo_servicio_total    : float = 0.0
        self.tiempo_servicio_restante : float = 0.0

        # ── Idle time ─────────────────────────────────────────────────────────
        # Tiempo acumulado (segundos) en que el cajero estuvo libre sin atender
        self.idle_time_acumulado : float = 0.0

        # Sprites según estado
        self._sprite_libre   = SpriteFactory.create_cajero(ocupado=False)
        self._sprite_ocupado = SpriteFactory.create_cajero(ocupado=True)

        # Sprite del operador fijo detrás del mostrador
        self._sprite_operador = SpriteFactory.create_cliente(
            color=(180, 140, 100),
            productos=0
        )
        # Posición del operador: ajuste visual (una celda diagonal hacia atrás)
        self._operador_gx = float(gx - 1)
        self._operador_gy = float(gy - 1)

        # Fuentes para el overlay
        self._font_id       = pygame.font.SysFont("monospace", 14, bold=True)
        self._font_progress = pygame.font.SysFont("monospace", 12)

        self.idle_time_acumulado = 0.0

        super().__init__(
            gx     = gx,
            gy     = gy,
            gz     = 0.0,
            sprite = self._sprite_libre
        )

    # -------------------------------------------------------------------------
    # Lógica de servicio
    # -------------------------------------------------------------------------

    def iniciar_servicio(self, cliente, duracion: float) -> None:
        """
        Inicia el servicio al cliente indicado.

        Parameters
        ----------
        cliente  : Instancia de Cliente que pasa a ser atendida.
        duracion : Duración total del servicio en segundos.
        """
        self.cliente_activo           = cliente
        self.ocupado                  = True
        self.tiempo_servicio_total    = duracion
        self.tiempo_servicio_restante = duracion
        self.sprite                   = self._sprite_ocupado

    def actualizar(self, dt: float) -> bool:
        """
        Descuenta el tiempo del servicio activo.
        Acumula idle time cuando el cajero está libre.

        Returns
        -------
        True si el servicio terminó en este frame, False en caso contrario.
        """
        if not self.ocupado:
            # Cajero libre: acumular idle time
            self.idle_time_acumulado += dt
            return False

        self.tiempo_servicio_restante -= dt

        if self.tiempo_servicio_restante <= 0.0:
            self.tiempo_servicio_restante = 0.0
            self.ocupado                  = False
            self.sprite                   = self._sprite_libre
            self.cliente_activo           = None
            return True

        return False

    def calcular_duracion_servicio(self, productos: int) -> float:
        """
        Calcula la duración del servicio para un número de productos dado,
        usando el tiempo_por_producto propio de este cajero.

        Parameters
        ----------
        productos : Número de productos del cliente.

        Returns
        -------
        Duración en segundos (mínimo 2.0).
        """
        import random
        base      = productos * self.tiempo_por_producto
        variacion = random.uniform(-1.0, 2.0)
        return max(2.0, base + variacion)

    @property
    def progreso_porcentaje(self) -> float:
        """Fracción de 0.0 a 1.0 del tiempo de servicio consumido."""
        if self.tiempo_servicio_total <= 0:
            return 0.0
        consumido = self.tiempo_servicio_total - self.tiempo_servicio_restante
        return min(1.0, consumido / self.tiempo_servicio_total)

    # -------------------------------------------------------------------------
    # Renderizado del overlay flotante
    # -------------------------------------------------------------------------

    def draw_overlay(self, surface: pygame.Surface) -> None:
        """
        Pinta el overlay flotante sobre la estación:
        - Operador fijo detrás del mostrador.
        - Etiqueta de ID ("C-1", "C-2", ...).
        - Barra de progreso pixelada de la atención actual.
        """
        from engine.iso import to_iso

        self._update_screen_coords()

        ox = self.screen_x
        oy = self.screen_y - self.sprite.get_height() - 4

        # ── Operador fijo detrás del mostrador ───────────────────────────────
        op_sx, op_sy = to_iso(self._operador_gx, self._operador_gy, 0)
        op_sy -= self._sprite_operador.get_height() // 2
        surface.blit(self._sprite_operador, (
            op_sx - self._sprite_operador.get_width() // 2,
            op_sy
        ))

        # ── Etiqueta de ID ────────────────────────────────────────────────────
        label      = f"C-{self.indice + 1}"
        label_surf = self._font_id.render(label, True, ACCENT_COLOR)
        label_x    = ox - label_surf.get_width() // 2
        label_y    = oy - 26
        shadow     = self._font_id.render(label, True, (0, 0, 0))
        surface.blit(shadow, (label_x + 1, label_y + 1))
        surface.blit(label_surf, (label_x, label_y))

        # ── Barra de progreso ─────────────────────────────────────────────────
        if self.ocupado:
            bar_w = 48
            bar_h = 6
            bar_x = ox - bar_w // 2
            bar_y = oy - 10

            pygame.draw.rect(surface, PROGRESS_BG, (bar_x, bar_y, bar_w, bar_h))

            progreso = self.progreso_porcentaje
            if progreso < 0.5:
                bar_color = PROGRESS_OK
            elif progreso < 0.8:
                bar_color = PROGRESS_LOW
            else:
                bar_color = PROGRESS_END

            fill_w = int(bar_w * progreso)
            if fill_w > 0:
                pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_w, bar_h))

            pygame.draw.rect(surface, ACCENT_COLOR, (bar_x, bar_y, bar_w, bar_h), 1)

            pct_text = f"{int(progreso * 100)}%"
            pct_surf = self._font_progress.render(pct_text, True, TEXT_COLOR)
            surface.blit(pct_surf, (bar_x + bar_w + 3, bar_y - 3))

    def draw(self, renderer: Renderer) -> None:
        """Sobreescribe para actualizar el sprite según estado antes del submit."""
        self.sprite = self._sprite_ocupado if self.ocupado else self._sprite_libre
        super().draw(renderer)