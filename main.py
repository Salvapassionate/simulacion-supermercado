# =============================================================================
# main.py
# =============================================================================

import sys
import pygame

from config.settings  import WIDTH, HEIGHT, FPS, SIDEBAR_W, SIM_W, MAX_CAJEROS
from config.colors    import BG_COLOR, SIDEBAR_COLOR

from engine.renderer  import Renderer
from engine.camera    import Camera

from graphics.floor   import IsoFloor
from graphics.ui      import SidebarUI

from simulation.supermarket import Supermarket


# =============================================================================
# PANTALLA DE CONFIGURACIÓN PREVIA
# =============================================================================

def run_config_screen(screen: pygame.Surface, clock: pygame.time.Clock) -> dict:
    """
    Pantalla de configuración previa a la simulación.

    Filas navegables:
        0          → Duración (segundos, 0 = infinito)
        1          → Cajeros activos
        2..N+1     → Tiempo de servicio por cajero N

    Retorna dict con claves:
        "duracion"         : float
        "cajeros_activos"  : int
        "tiempos_cajero"   : list[int]
    """

    font_title  = pygame.font.SysFont("monospace", 28, bold=True)
    font_sub    = pygame.font.SysFont("monospace", 15)
    font_label  = pygame.font.SysFont("monospace", 17)
    font_value  = pygame.font.SysFont("monospace", 17, bold=True)
    font_hint   = pygame.font.SysFont("monospace", 13)

    # Estado de configuración
    duracion        = 120          # Segundos (0 = infinito)
    cajeros_activos = MAX_CAJEROS
    tiempos         = [2] * MAX_CAJEROS
    fila_activa     = 0

    # Fila 0: duración | Fila 1: cajeros activos | Filas 2..N+1: tiempos
    total_filas = 2 + MAX_CAJEROS

    COLOR_BG        = (18, 22, 30)
    COLOR_PANEL     = (28, 34, 46)
    COLOR_BORDER    = (60, 80, 110)
    COLOR_TITLE     = (255, 210, 60)
    COLOR_LABEL     = (170, 185, 210)
    COLOR_VALUE     = (100, 220, 140)
    COLOR_SELECTED  = (255, 255, 255)
    COLOR_SEL_BG    = (45, 65, 100)
    COLOR_HINT      = (100, 115, 140)
    COLOR_ENTER     = (60, 180, 100)
    COLOR_ENTER_TXT = (10, 20, 15)
    COLOR_INACTIVE  = (80, 90, 105)

    def duracion_label(val: int) -> str:
        return "Infinita" if val == 0 else f"{val}s"

    def draw_config(fila: int, dur: int, cajeros: int, tiempos_list: list) -> None:
        screen.fill(COLOR_BG)

        panel_w, panel_h = 640, 580
        panel_x = (WIDTH - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_BORDER, panel_rect, 2, border_radius=10)

        title = font_title.render("SUPERMARKET SIMULATION", True, COLOR_TITLE)
        screen.blit(title, (panel_x + (panel_w - title.get_width()) // 2, panel_y + 20))

        sub = font_sub.render("TDS115 · Universidad de El Salvador", True, COLOR_HINT)
        screen.blit(sub, (panel_x + (panel_w - sub.get_width()) // 2, panel_y + 56))

        pygame.draw.line(screen, COLOR_BORDER,
                         (panel_x + 20, panel_y + 82),
                         (panel_x + panel_w - 20, panel_y + 82), 1)

        content_x = panel_x + 30
        y = panel_y + 100

        # ── Fila 0: Duración ──────────────────────────────────────────────────
        es_activa = (fila == 0)
        row_rect = pygame.Rect(panel_x + 16, y - 4, panel_w - 32, 30)
        if es_activa:
            pygame.draw.rect(screen, COLOR_SEL_BG, row_rect, border_radius=4)

        arrow_l = "◄ " if es_activa else "  "
        arrow_r = " ►" if es_activa else "  "
        lbl = font_label.render("Duración simulación:", True,
                                COLOR_SELECTED if es_activa else COLOR_LABEL)
        val = font_value.render(f"{arrow_l}{duracion_label(dur)}{arrow_r}", True,
                                COLOR_VALUE if es_activa else COLOR_VALUE)
        screen.blit(lbl, (content_x, y))
        screen.blit(val, (panel_x + panel_w - val.get_width() - 30, y))
        y += 14

        hint_dur = font_hint.render("  ← → en pasos de 30s  |  mín. 30s  |  0 = sin límite", True, COLOR_HINT)
        screen.blit(hint_dur, (content_x, y))
        y += 28

        pygame.draw.line(screen, COLOR_BORDER,
                         (panel_x + 20, y),
                         (panel_x + panel_w - 20, y), 1)
        y += 12

        # ── Fila 1: Cajeros activos ───────────────────────────────────────────
        es_activa = (fila == 1)
        row_rect = pygame.Rect(panel_x + 16, y - 4, panel_w - 32, 30)
        if es_activa:
            pygame.draw.rect(screen, COLOR_SEL_BG, row_rect, border_radius=4)

        arrow_l = "◄ " if es_activa else "  "
        arrow_r = " ►" if es_activa else "  "
        lbl = font_label.render("Cajeros activos:", True,
                                COLOR_SELECTED if es_activa else COLOR_LABEL)
        val = font_value.render(f"{arrow_l}{cajeros}{arrow_r}", True,
                                COLOR_VALUE if es_activa else COLOR_VALUE)
        screen.blit(lbl, (content_x, y))
        screen.blit(val, (panel_x + panel_w - val.get_width() - 30, y))
        y += 38

        pygame.draw.line(screen, COLOR_BORDER,
                         (panel_x + 20, y),
                         (panel_x + panel_w - 20, y), 1)
        y += 14

        enc = font_hint.render("Tiempo de servicio por cajero (seg/producto):", True, COLOR_HINT)
        screen.blit(enc, (content_x, y))
        y += 24

        # ── Filas 2..N+1: tiempo por cajero ──────────────────────────────────
        for i in range(MAX_CAJEROS):
            fila_idx = i + 2
            es_activa_fila = (fila == fila_idx)
            activo = (i < cajeros)

            row_rect = pygame.Rect(panel_x + 16, y - 3, panel_w - 32, 26)
            if es_activa_fila and activo:
                pygame.draw.rect(screen, COLOR_SEL_BG, row_rect, border_radius=4)

            color_lbl = COLOR_INACTIVE if not activo else (
                COLOR_SELECTED if es_activa_fila else COLOR_LABEL)
            color_val = COLOR_INACTIVE if not activo else (
                COLOR_VALUE if es_activa_fila else (140, 200, 160))

            arrow_l = "◄ " if (es_activa_fila and activo) else "  "
            arrow_r = " ►" if (es_activa_fila and activo) else "  "

            estado_txt = "" if activo else "  [inactivo]"
            lbl = font_label.render(f"  Cajero {i + 1}:{estado_txt}", True, color_lbl)
            val = font_value.render(f"{arrow_l}{tiempos_list[i]}s{arrow_r}", True, color_val)

            screen.blit(lbl, (content_x, y))
            screen.blit(val, (panel_x + panel_w - val.get_width() - 30, y))
            y += 28

        # ── Botón ENTER ───────────────────────────────────────────────────────
        y = panel_y + panel_h - 64
        pygame.draw.line(screen, COLOR_BORDER,
                         (panel_x + 20, y - 10),
                         (panel_x + panel_w - 20, y - 10), 1)

        btn_rect = pygame.Rect(panel_x + panel_w // 2 - 130, y, 260, 38)
        pygame.draw.rect(screen, COLOR_ENTER, btn_rect, border_radius=6)
        btn_txt = font_value.render("[ ENTER ]  Iniciar simulación", True, COLOR_ENTER_TXT)
        screen.blit(btn_txt, (btn_rect.centerx - btn_txt.get_width() // 2,
                               btn_rect.centery - btn_txt.get_height() // 2))

        hint = font_hint.render("↑↓ navegar    ←→ ajustar    ESC salir", True, COLOR_HINT)
        screen.blit(hint, (panel_x + (panel_w - hint.get_width()) // 2,
                           panel_y + panel_h - 18))

        pygame.display.flip()

    # ── Bucle pantalla de configuración ──────────────────────────────────────
    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(0)

                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return {
                        "duracion":        float(duracion),
                        "cajeros_activos": cajeros_activos,
                        "tiempos_cajero":  tiempos[:cajeros_activos]
                    }

                elif event.key == pygame.K_UP:
                    fila_activa = (fila_activa - 1) % total_filas

                elif event.key == pygame.K_DOWN:
                    fila_activa = (fila_activa + 1) % total_filas

                elif event.key == pygame.K_LEFT:
                    if fila_activa == 0:
                        # Pasos de 30s, mínimo 0
                        duracion = max(0, duracion - 30)
                    elif fila_activa == 1:
                        cajeros_activos = max(1, cajeros_activos - 1)
                    else:
                        i = fila_activa - 2
                        if i < cajeros_activos:
                            tiempos[i] = max(1, tiempos[i] - 1)

                elif event.key == pygame.K_RIGHT:
                    if fila_activa == 0:
                        # Pasos de 30s, máximo 3600 (1 hora)
                        if duracion == 0:
                            duracion = 30
                        else:
                            duracion = min(3600, duracion + 30)
                    elif fila_activa == 1:
                        cajeros_activos = min(MAX_CAJEROS, cajeros_activos + 1)
                    else:
                        i = fila_activa - 2
                        if i < cajeros_activos:
                            tiempos[i] = min(60, tiempos[i] + 1)

        draw_config(fila_activa, duracion, cajeros_activos, tiempos)


# =============================================================================
# PANTALLA DE ESTADÍSTICAS FINALES
# =============================================================================

def run_stats_screen(
    screen     : pygame.Surface,
    clock      : pygame.time.Clock,
    supermarket: Supermarket
) -> str:
    """
    Muestra las estadísticas finales al terminar el tiempo de simulación.

    Retorna:
        "restart" → ir a pantalla de configuración
        "quit"    → salir de la aplicación
    """
    font_title  = pygame.font.SysFont("monospace", 26, bold=True)
    font_head   = pygame.font.SysFont("monospace", 16, bold=True)
    font_body   = pygame.font.SysFont("monospace", 15)
    font_hint   = pygame.font.SysFont("monospace", 13)

    COLOR_BG     = (18, 22, 30)
    COLOR_PANEL  = (28, 34, 46)
    COLOR_BORDER = (60, 80, 110)
    COLOR_TITLE  = (255, 210, 60)
    COLOR_HEAD   = (100, 220, 140)
    COLOR_BODY   = (170, 185, 210)
    COLOR_HINT   = (100, 115, 140)
    COLOR_BTN_R  = (60, 180, 100)
    COLOR_BTN_Q  = (180, 60, 60)
    COLOR_TXT    = (10, 20, 15)

    m = supermarket.metrics

    def draw_stats() -> None:
        screen.fill(COLOR_BG)

        panel_w, panel_h = 660, 480
        panel_x = (WIDTH  - panel_w) // 2
        panel_y = (HEIGHT - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, COLOR_PANEL,  panel_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_BORDER, panel_rect, 2, border_radius=10)

        # Título
        title = font_title.render("SIMULACIÓN FINALIZADA", True, COLOR_TITLE)
        screen.blit(title, (panel_x + (panel_w - title.get_width()) // 2, panel_y + 18))

        pygame.draw.line(screen, COLOR_BORDER,
                         (panel_x + 20, panel_y + 56),
                         (panel_x + panel_w - 20, panel_y + 56), 1)

        cx = panel_x + 40
        y  = panel_y + 70

        # ── Métricas globales ─────────────────────────────────────────────────
        head = font_head.render("ESTADÍSTICAS GLOBALES", True, COLOR_HEAD)
        screen.blit(head, (cx, y)); y += 28

        datos = [
            ("Clientes atendidos",   str(len(m.tiempos_en_sistema))),
            ("Clientes rechazados",  str(m.rechazados)),
            ("Esp. promedio",        f"{m.espera_promedio:.1f} s"),
            ("Esp. máximo",          f"{m.espera_maxima:.1f} s"),
            ("T. sistema promedio",  f"{m.tiempo_sistema_promedio:.1f} s"),
        ]

        col2_x = panel_x + panel_w // 2 + 20
        for i, (lbl, val) in enumerate(datos):
            lbl_surf = font_body.render(lbl + ":", True, COLOR_BODY)
            val_surf = font_body.render(val,        True, COLOR_HEAD)
            row_y = y + i * 26
            screen.blit(lbl_surf, (cx,      row_y))
            screen.blit(val_surf, (cx + 250, row_y))

        y += len(datos) * 26 + 14
        pygame.draw.line(screen, COLOR_BORDER,
                         (panel_x + 20, y),
                         (panel_x + panel_w - 20, y), 1)
        y += 14

        # ── Idle time por cajero ──────────────────────────────────────────────
        head2 = font_head.render("IDLE TIME POR CAJERO", True, COLOR_HEAD)
        screen.blit(head2, (cx, y)); y += 28

        cajeros = supermarket.cajeros
        cols    = 4
        for i, cajero in enumerate(cajeros):
            col  = i % cols
            row  = i // cols
            cx_c = cx + col * 150
            cy_c = y  + row * 24
            idle = getattr(cajero, "idle_time_acumulado", 0.0)
            txt  = font_body.render(f"C-{cajero.indice + 1}: {idle:.1f}s", True, COLOR_BODY)
            screen.blit(txt, (cx_c, cy_c))

        # ── Botones ───────────────────────────────────────────────────────────
        btn_y = panel_y + panel_h - 60

        pygame.draw.line(screen, COLOR_BORDER,
                         (panel_x + 20, btn_y - 10),
                         (panel_x + panel_w - 20, btn_y - 10), 1)

        btn_r = pygame.Rect(panel_x + panel_w // 2 - 270, btn_y, 240, 36)
        btn_q = pygame.Rect(panel_x + panel_w // 2 +  30, btn_y, 240, 36)

        pygame.draw.rect(screen, COLOR_BTN_R, btn_r, border_radius=6)
        pygame.draw.rect(screen, COLOR_BTN_Q, btn_q, border_radius=6)

        t_r = font_body.render("[ R ]  Nueva simulación", True, COLOR_TXT)
        t_q = font_body.render("[ ESC ]  Salir",          True, COLOR_TXT)

        screen.blit(t_r, (btn_r.centerx - t_r.get_width() // 2,
                          btn_r.centery - t_r.get_height() // 2))
        screen.blit(t_q, (btn_q.centerx - t_q.get_width() // 2,
                          btn_q.centery - t_q.get_height() // 2))

        hint = font_hint.render("R — reiniciar con nueva configuración    ESC — salir", True, COLOR_HINT)
        screen.blit(hint, (panel_x + (panel_w - hint.get_width()) // 2,
                           panel_y + panel_h - 14))

        pygame.display.flip()

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"
                elif event.key == pygame.K_r:
                    return "restart"

        draw_stats()


# =============================================================================
# BUCLE PRINCIPAL
# =============================================================================

def main() -> None:
    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Supermarket Sim · TDS115 UES")
    clock  = pygame.time.Clock()

    config      = run_config_screen(screen, clock)
    renderer    = Renderer()
    camera      = Camera()
    floor       = IsoFloor()
    ui          = SidebarUI()
    supermarket = Supermarket(config=config)

    sim_clip_rect = pygame.Rect(SIDEBAR_W, 0, SIM_W, HEIGHT)

    paused  = False
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        # ── Detectar fin de simulación ────────────────────────────────────────
        if supermarket.sim_terminada:
            accion = run_stats_screen(screen, clock, supermarket)
            if accion == "quit":
                break
            elif accion == "restart":
                config      = run_config_screen(screen, clock)
                supermarket = Supermarket(config=config)
                paused      = False
            continue

        # ── Eventos ───────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mx, my = event.pos
                    if 14 <= mx <= SIDEBAR_W - 14 and 92 <= my <= 120:
                        paused = not paused

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_F1:
                    supermarket.forzar_cliente()

                elif event.key == pygame.K_r:
                    config      = run_config_screen(screen, clock)
                    supermarket = Supermarket(config=config)
                    paused      = False

                elif event.key == pygame.K_SPACE:
                    paused = not paused

        # ── Lógica ────────────────────────────────────────────────────────────
        if not paused and not supermarket.sim_terminada:
            supermarket.update(dt)

        # ── Renderizado ───────────────────────────────────────────────────────
        screen.fill(BG_COLOR)
        screen.set_clip(sim_clip_rect)
        floor.draw(screen)
        renderer.begin()

        for entity in supermarket.get_all_entities():
            entity.draw(renderer)

        renderer.draw(screen)
        screen.set_clip(None)

        for cajero in supermarket.cajeros:
            cajero.draw_overlay(screen)

        ui.draw(
            surface   = screen,
            metrics   = supermarket.metrics.to_dict(),
            cajeros   = supermarket.cajeros,
            sim_time  = supermarket.sim_time,
            paused    = paused,
            tiempo_restante = supermarket.tiempo_restante
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()