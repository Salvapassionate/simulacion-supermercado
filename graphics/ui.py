# =============================================================================
# graphics/ui.py
# =============================================================================

import pygame
from config.settings import SIDEBAR_W, HEIGHT, MAX_CAJEROS
from config.colors import (
    SIDEBAR_COLOR, TEXT_COLOR, ACCENT_COLOR, PANEL_DIVIDER,
    METRIC_LABEL, METRIC_VALUE, HELP_COLOR, TITLE_COLOR,
    CAJERO_FREE, CAJERO_BUSY
)


class SidebarUI:

    def __init__(self) -> None:
        self.font_title  = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_label  = pygame.font.SysFont("monospace", 16)
        self.font_value  = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_small  = pygame.font.SysFont("monospace", 14)
        self.font_medium = pygame.font.SysFont("monospace", 16, bold=True)

    def draw(
        self,
        surface         : pygame.Surface,
        metrics         : dict,
        cajeros         : list,
        sim_time        : float,
        paused          : bool,
        tiempo_restante : float = -1.0   # -1 = sin límite
    ) -> None:

        # ── Fondo del panel ───────────────────────────────────────────────────
        panel_rect = pygame.Rect(0, 0, SIDEBAR_W, HEIGHT)
        pygame.draw.rect(surface, SIDEBAR_COLOR, panel_rect)
        pygame.draw.line(surface, ACCENT_COLOR, (SIDEBAR_W - 2, 0), (SIDEBAR_W - 2, HEIGHT), 2)

        y = 14

        # ── Título ────────────────────────────────────────────────────────────
        self._draw_text(surface, "SUPERMERCADO SIM", 14, y, self.font_title, TITLE_COLOR)
        y += 28
        self._draw_text(surface, "TDS115 | UES", 14, y, self.font_small, METRIC_LABEL)
        y += 22
        self._divider(surface, y)
        y += 12

        # ── Tiempo de simulación ──────────────────────────────────────────────
        mins = int(sim_time) // 60
        secs = int(sim_time) % 60
        self._draw_pair(surface, y, "TIEMPO SIM:", f"{mins:02d}:{secs:02d}")
        y += 22

        # ── Tiempo restante (solo si hay límite) ──────────────────────────────
        if tiempo_restante >= 0:
            tr_mins = int(tiempo_restante) // 60
            tr_secs = int(tiempo_restante) % 60
            # Color de alerta cuando quedan menos de 30 segundos
            color_tr = (220, 80, 80) if tiempo_restante < 30 else (100, 220, 140)
            lbl_surf = self.font_label.render("Restante:", True, METRIC_LABEL)
            val_surf = self.font_value.render(f"{tr_mins:02d}:{tr_secs:02d}", True, color_tr)
            surface.blit(lbl_surf, (14, y))
            surface.blit(val_surf, (SIDEBAR_W - val_surf.get_width() - 14, y))
            y += 22

        y += 6

        # ── Botón pausa ───────────────────────────────────────────────────────
        btn_rect  = pygame.Rect(14, y, SIDEBAR_W - 28, 34)
        btn_color = CAJERO_BUSY if not paused else CAJERO_FREE
        pygame.draw.rect(surface, btn_color, btn_rect, 0, 4)
        btn_label = "PAUSAR SIM [ESPACIO]" if not paused else "INICIAR SIM [ESPACIO]"
        btn_surf  = self.font_value.render(btn_label, True, (255, 255, 255))
        surface.blit(btn_surf, (btn_rect.centerx - btn_surf.get_width()  // 2,
                                btn_rect.centery - btn_surf.get_height() // 2))
        y += 50

        # ── Métricas principales ──────────────────────────────────────────────
        self._divider(surface, y)
        y += 12
        self._draw_text(surface, "[ METRICAS ]", 14, y, self.font_medium, ACCENT_COLOR)
        y += 24

        self._draw_pair(surface, y, "Clientes totales:",
                        str(metrics.get("total_llegadas", 0)))
        y += 22
        self._draw_pair(surface, y, "Atendidos:",
                        str(metrics.get("total_atendidos", 0)))
        y += 22
        self._draw_pair(surface, y, "En sistema:",
                        str(metrics.get("en_sistema", 0)))
        y += 22
        self._draw_pair(surface, y, "Max. simultáneos:",
                        str(metrics.get("max_simultaneos", 0)))
        y += 22
        self._draw_pair(surface, y, "Rechazados:",
                        str(metrics.get("rechazados", 0)))
        y += 22

        # ── Estadísticas avanzadas ────────────────────────────────────────────
        self._divider(surface, y)
        y += 12
        self._draw_text(surface, "[ ESTADISTICAS ]", 14, y, self.font_medium, ACCENT_COLOR)
        y += 24

        self._draw_pair(surface, y, "Esp. promedio:",
                        f"{metrics.get('espera_promedio', 0.0):.1f}s")
        y += 22
        self._draw_pair(surface, y, "T. sistema prom:",
                        f"{metrics.get('tiempo_sistema_promedio', 0.0):.1f}s")
        y += 22
        self._draw_pair(surface, y, "Esp. maxima:",
                        f"{metrics.get('espera_maxima', 0.0):.1f}s")
        y += 26

        self._draw_text(surface, "IDLE TIME", 14, y, self.font_small, ACCENT_COLOR)
        y += 20

        for cajero in cajeros:
            self._draw_pair(
                surface, y,
                f"C-{cajero.indice + 1}:",
                f"{cajero.idle_time_acumulado:.1f}s"
            )
            y += 18

        # ── Estado de cajeros ─────────────────────────────────────────────────
        self._divider(surface, y + 4)
        y += 16
        self._draw_text(surface, "[ CAJEROS ]", 14, y, self.font_medium, ACCENT_COLOR)
        y += 24

        for cajero in cajeros:
            color  = CAJERO_BUSY if cajero.ocupado else CAJERO_FREE
            estado = "OCUP" if cajero.ocupado else "LIBRE"
            cola   = len(cajero.cola)
            label  = f"C-{cajero.indice + 1}: {estado} Q:{cola}"
            pygame.draw.circle(surface, color, (10, y + 8), 7)
            self._draw_text(surface, label, 20, y, self.font_small, TEXT_COLOR)
            y += 20

        # ── Controles ─────────────────────────────────────────────────────────
        self._divider(surface, y + 8)
        y += 22
        self._draw_text(surface, "[ CONTROLES ]", 14, y, self.font_medium, ACCENT_COLOR)
        y += 24

        controles = [
            ("SPACE", "Pausar/Iniciar"),
            ("ESC",   "Salir"),
            ("F1",    "Nuevo cliente"),
            ("R",     "Reiniciar"),
        ]
        for key, desc in controles:
            key_surf  = self.font_value.render(f"[{key}]", True, ACCENT_COLOR)
            desc_surf = self.font_small.render(f" {desc}", True, HELP_COLOR)
            surface.blit(key_surf,  (14, y))
            surface.blit(desc_surf, (14 + key_surf.get_width(), y + 1))
            y += 22

        # ── Pie ───────────────────────────────────────────────────────────────
        self._divider(surface, HEIGHT - 35)
        version_surf = self.font_small.render("v1.0 | Pygame DES 2.5D", True, METRIC_LABEL)
        surface.blit(version_surf, (14, HEIGHT - 24))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _draw_text(self, surface, text, x, y, font, color) -> None:
        surface.blit(font.render(text, True, color), (x, y))

    def _draw_pair(self, surface, y, label, value) -> None:
        lbl_surf = self.font_label.render(label, True, METRIC_LABEL)
        val_surf = self.font_value.render(value, True, METRIC_VALUE)
        surface.blit(lbl_surf, (14, y))
        surface.blit(val_surf, (SIDEBAR_W - val_surf.get_width() - 14, y))

    def _divider(self, surface, y) -> None:
        pygame.draw.line(surface, PANEL_DIVIDER, (8, y), (SIDEBAR_W - 8, y), 1)