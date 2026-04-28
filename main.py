import pygame
import random

# --- CONFIGURACIÓN ---
pygame.init()
WIDTH, HEIGHT = 1100, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación de Supermercado - Dashboard Final")

# --- COLORES ---
BG_COLOR = (240, 240, 245)
SIDEBAR_COLOR = (44, 62, 80)
WHITE = (255, 255, 255)
TEXT_COLOR = (236, 240, 241)
ACCENT_COLOR = (241, 196, 15)
CAJERO_LIBRE = (46, 204, 113)
CAJERO_OCUPADO = (231, 76, 60)

font_bold = pygame.font.SysFont("Arial", 22, bold=True)
font_small = pygame.font.SysFont("Arial", 16)
font_tiny = pygame.font.SysFont("Arial", 14)
clock = pygame.time.Clock()

# --- VARIABLES ---
num_cajeros = 3
max_cajeros = 8
velocidad_llegada = 3
tiempo_por_producto = 10 
MAX_COLA = 10
clientes_atendidos = 0
suma_tiempos_espera = 0
running_simulation = False 

# --- LÓGICA DE CLIENTES ---
class Cliente:
    def __init__(self):
        self.productos = random.randint(1, 10)
        self.tiempo_proceso = self.productos * tiempo_por_producto
        self.color = (random.randint(80, 220), random.randint(80, 220), random.randint(80, 220))
        self.frames_en_espera = 0

colas = [[] for _ in range(max_cajeros)]
cajeros = [None for _ in range(max_cajeros)]

def reset_sim():
    global colas, cajeros, clientes_atendidos, suma_tiempos_espera, running_simulation
    colas = [[] for _ in range(max_cajeros)]
    cajeros = [None for _ in range(max_cajeros)]
    clientes_atendidos = 0
    suma_tiempos_espera = 0
    running_simulation = False

def draw_button(txt, x, y, w, h, color_base, color_hover):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    current_color = color_hover if rect.collidepoint(mouse) else color_base
    pygame.draw.rect(screen, current_color, rect, border_radius=5)
    surf = font_small.render(txt, True, WHITE)
    screen.blit(surf, surf.get_rect(center=rect.center))
    return rect.collidepoint(mouse) and click[0]

# --- BUCLE PRINCIPAL ---
running = True
while running:
    screen.fill(BG_COLOR)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP: num_cajeros = min(max_cajeros, num_cajeros + 1)
            if event.key == pygame.K_DOWN: num_cajeros = max(1, num_cajeros - 1)
            if event.key == pygame.K_RIGHT: velocidad_llegada = min(20, velocidad_llegada + 1)
            if event.key == pygame.K_LEFT: velocidad_llegada = max(1, velocidad_llegada - 1)
            if event.key == pygame.K_w: tiempo_por_producto = min(50, tiempo_por_producto + 2)
            if event.key == pygame.K_s: tiempo_por_producto = max(2, tiempo_por_producto - 2)
            if event.key == pygame.K_SPACE: running_simulation = not running_simulation
            if event.key == pygame.K_r: reset_sim()

    if running_simulation:
        if random.randint(0, 100) < velocidad_llegada:
            nuevo = Cliente()
            cola_corta = min(colas[:num_cajeros], key=len)
            if len(cola_corta) < MAX_COLA: cola_corta.append(nuevo)

        for i in range(num_cajeros):
            for c in colas[i]: c.frames_en_espera += 1
            if cajeros[i] is None and len(colas[i]) > 0:
                cajeros[i] = colas[i].pop(0)
                suma_tiempos_espera += cajeros[i].frames_en_espera
            if cajeros[i] is not None:
                cajeros[i].tiempo_proceso -= 1
                if cajeros[i].tiempo_proceso <= 0:
                    cajeros[i] = None
                    clientes_atendidos += 1

    # --- DIBUJAR SIDEBAR ---
    pygame.draw.rect(screen, SIDEBAR_COLOR, (0, 0, 280, HEIGHT))
    
    # 1. MÉTRICAS
    y_met = 30
    screen.blit(font_bold.render("MÉTRICAS", True, WHITE), (20, y_met))
    pygame.draw.line(screen, (127, 140, 141), (20, y_met+30), (260, y_met+30), 2)
    
    espera_prom = round(suma_tiempos_espera / clientes_atendidos, 1) if clientes_atendidos > 0 else 0
    metrics = [
        ("Cajeros:", f"{num_cajeros}"),
        ("Atendidos:", f"{clientes_atendidos}"),
        ("Llegada:", f"{velocidad_llegada}%"),
        ("Espera Prom:", f"{espera_prom}"),
        ("En Sistema:", f"{sum(len(c) for c in colas[:num_cajeros]) + sum(1 for c in cajeros[:num_cajeros] if c)}")
    ]
    for label, val in metrics:
        y_met += 45
        screen.blit(font_small.render(label, True, TEXT_COLOR), (20, y_met))
        v_surf = font_small.render(val, True, ACCENT_COLOR)
        screen.blit(v_surf, v_surf.get_rect(topright=(260, y_met)))

    # 2. BOTONES INTERACTIVOS
    y_btns = 320
    screen.blit(font_small.render("ACCIONES", True, (149, 165, 166)), (20, y_btns))
    if draw_button("START", 20, y_btns+25, 70, 35, (46, 204, 113), (39, 174, 96)): running_simulation = True
    if draw_button("PAUSE", 105, y_btns+25, 70, 35, (230, 126, 34), (211, 84, 0)): running_simulation = False
    if draw_button("RESET", 190, y_btns+25, 70, 35, (231, 76, 60), (192, 57, 43)): reset_sim()

    # 3. LEYENDA DE CONTROLES (TECLADO)
    y_ctrl = 420
    pygame.draw.line(screen, (127, 140, 141), (20, y_ctrl), (260, y_ctrl), 1)
    screen.blit(font_small.render("CONTROLES DE TECLADO", True, (149, 165, 166)), (20, y_ctrl + 10))
    
    controles = [
        ("UP / DOWN", "Sumar/Restar Cajeros"),
        ("LEFT / RIGHT", "Ajustar tasa llegada"),
        ("W / S", "Velocidad de atención"),
        ("SPACE", "Pausar / Reanudar"),
        ("R", "Resetear simulación")
    ]
    
    for i, (tecla, desc) in enumerate(controles):
        y_pos = y_ctrl + 40 + (i * 35)
        screen.blit(font_tiny.render(tecla, True, ACCENT_COLOR), (20, y_pos))
        screen.blit(font_tiny.render(desc, True, TEXT_COLOR), (20, y_pos + 15))

    # --- ÁREA DE CAJEROS ---
    start_x = 350
    for i in range(num_cajeros):
        x = start_x + (i * 95)
        color = CAJERO_OCUPADO if cajeros[i] else CAJERO_LIBRE
        pygame.draw.rect(screen, color, (x, 100, 65, 65), border_radius=8)
        screen.blit(font_small.render(f"C-{i+1}", True, (50, 50, 50)), (x+15, 75))
        for j, c in enumerate(colas[i]):
            cy = 185 + (j * 38)
            pygame.draw.circle(screen, c.color, (x+32, cy), 16)
            txt = font_small.render(str(c.productos), True, WHITE)
            screen.blit(txt, txt.get_rect(center=(x+32, cy)))

    pygame.display.flip()
    clock.tick(60)
pygame.quit()