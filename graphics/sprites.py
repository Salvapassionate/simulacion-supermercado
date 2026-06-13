# =============================================================================
# graphics/sprites.py
# Fábrica procedural de sprites pixel-art generados en memoria.
# Sin recursos externos: todos los gráficos se construyen con primitivas Pygame.
# Estética inspirada en Theme Hospital / The Sims 1 (PC clásico, años 90).
#
# REGLA DE ANCLAJE GEOMÉTRICO:
# El punto de origen del blit en pantalla es la BASE INFERIOR CENTRAL del objeto.
# Las fórmulas de posicionamiento son:
#   dest_x = screen_x - surface_width  // 2
#   dest_y = screen_y - surface_height
# Todos los polígonos internos respetan que el "suelo" del objeto esté alineado
# con el centro del rombo isométrico de su celda.
# =============================================================================

import pygame
import random
from config.colors import (
    SHELF_TOP, SHELF_FRONT, SHELF_SIDE, SHELF_PLANK,
    CAJERO_FREE, CAJERO_BUSY, CAJERO_TOP, CAJERO_FRONT, CAJERO_SIDE,
    SCREEN_GREEN, SKIN_COLOR, LEGS_COLOR, BUBBLE_BG, BUBBLE_TEXT
)
from config.settings import TILE_W, TILE_H


class SpriteFactory:
    """
    Clase estática que fabrica superficies pygame con canal alfa.
    Cada método retorna una pygame.Surface lista para blit.
    No mantiene estado interno; todos los métodos son @staticmethod.
    """

    # -------------------------------------------------------------------------
    # Helpers internos de geometría isométrica
    # -------------------------------------------------------------------------

    @staticmethod
    def _iso_top_face(cx: int, cy: int, tw: int, th: int) -> list[tuple[int, int]]:
        """
        Genera los 4 vértices del rombo de la cara superior de un bloque
        isométrico centrado en (cx, cy), con ancho tw y alto th.
        """
        return [
            (cx,          cy - th // 2),   # vértice superior
            (cx + tw // 2, cy),            # vértice derecho
            (cx,          cy + th // 2),   # vértice inferior
            (cx - tw // 2, cy),            # vértice izquierdo
        ]

    @staticmethod
    def _iso_left_face(
        cx: int, cy: int, tw: int, th: int, height_px: int
    ) -> list[tuple[int, int]]:
        """Cara lateral izquierda (visible) de un bloque isométrico."""
        return [
            (cx - tw // 2, cy),                   # superior-izquierda del rombo
            (cx,           cy + th // 2),          # inferior-centro del rombo
            (cx,           cy + th // 2 + height_px),  # inferior-centro abajo
            (cx - tw // 2, cy + height_px),        # inferior-izquierda abajo
        ]

    @staticmethod
    def _iso_right_face(
        cx: int, cy: int, tw: int, th: int, height_px: int
    ) -> list[tuple[int, int]]:
        """Cara lateral derecha (visible) de un bloque isométrico."""
        return [
            (cx + tw // 2, cy),                   # superior-derecha del rombo
            (cx,           cy + th // 2),          # inferior-centro del rombo
            (cx,           cy + th // 2 + height_px),  # inferior-centro abajo
            (cx + tw // 2, cy + height_px),        # inferior-derecha abajo
        ]

    # -------------------------------------------------------------------------
    # Góndola (estantería de supermercado)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # Pared Estructural del Centro Comercial (Nuevo)
    # -------------------------------------------------------------------------
    @staticmethod
    def create_wall() -> pygame.Surface:
        """
        Genera un sprite procedural de una pared alta ladrillada/bloque
        para delimitar los costados del supermercado.
        """
        sw, sh = 72, 90
        surf = pygame.Surface((sw, sh), pygame.SRCALPHA)
        
        cx, cy = sw // 2, sh - TILE_H // 2
        wall_h = 45 # Altura considerable para tapar el fondo
        
        tw, th = TILE_W, TILE_H
        
        left_pts  = SpriteFactory._iso_left_face(cx, cy - wall_h, tw, th, wall_h)
        right_pts = SpriteFactory._iso_right_face(cx, cy - wall_h, tw, th, wall_h)
        top_pts   = SpriteFactory._iso_top_face(cx, cy - wall_h, tw, th)
        
        # Colores retro tipo ladrillo de concreto / bloque de mall
        COLOR_PARED_IZQ = (110, 115, 125)
        COLOR_PARED_DER = (135, 140, 150)
        COLOR_PARED_TOP = (165, 170, 180)
        
        pygame.draw.polygon(surf, COLOR_PARED_IZQ, left_pts)
        pygame.draw.polygon(surf, COLOR_PARED_DER, right_pts)
        pygame.draw.polygon(surf, COLOR_PARED_TOP, top_pts)
        
        # Detalles de bloques texturizados (líneas de construcción)
        for i in range(1, 4):
            h_offset = (wall_h // 4) * i
            pygame.draw.line(surf, (80, 85, 95), (cx - tw//2, cy - h_offset), (cx, cy + th//2 - h_offset), 1)
            pygame.draw.line(surf, (95, 100, 110), (cx, cy + th//2 - h_offset), (cx + tw//2, cy - h_offset), 1)
            
        return surf

    # -------------------------------------------------------------------------
    # Góndola Tuneada con Productos Reales de Colores
    # -------------------------------------------------------------------------
    @staticmethod
    def create_shelf() -> pygame.Surface:
        """
        Dibuja una góndola retro en perspectiva isométrica mejorada con productos reales.
        """
        sw, sh = 72, 80
        surf = pygame.Surface((sw, sh), pygame.SRCALPHA)

        cx, cy = sw // 2, sh - TILE_H // 2 - 2
        block_h = 32 # Un poco más alta para que quepan bien los productos

        # Sombra proyectada en el suelo
        shadow_rect = (cx - TILE_W // 2 + 4, cy - TILE_H // 2 + 2, TILE_W - 8, TILE_H - 4)
        pygame.draw.ellipse(surf, (0, 0, 0, 75), shadow_rect)

        tw, th = TILE_W - 6, TILE_H - 4

        # Estructura de madera/metal trasera
        left_pts   = SpriteFactory._iso_left_face(cx, cy - block_h, tw, th, block_h)
        right_pts  = SpriteFactory._iso_right_face(cx, cy - block_h, tw, th, block_h)
        top_pts    = SpriteFactory._iso_top_face(cx, cy - block_h, tw, th)

        pygame.draw.polygon(surf, SHELF_SIDE, left_pts)
        pygame.draw.polygon(surf, SHELF_FRONT, right_pts)
        pygame.draw.polygon(surf, SHELF_TOP, top_pts)

        # Paleta de productos coloridos (Cereales, cajas, latas)
        PRODUCT_COLORS = [
            (230, 60, 60),   # Rojo (Salsa/Ketchup)
            (60, 120, 240),  # Azul (Cajas de detergente)
            (240, 200, 40),  # Amarillo (Cajas de cereal)
            (40, 180, 100),  # Verde (Conservas)
            (210, 100, 40)   # Naranja
        ]

        # Renderizado de repisas y relleno de productos
        levels = [block_h // 4, block_h // 2, (3 * block_h) // 4]
        for h_offset in levels:
            ry = cy - block_h + h_offset
            
            # Dibujar las repisas físicas (Líneas base)
            pygame.draw.line(surf, SHELF_PLANK, (cx - tw // 2, ry), (cx, ry + th // 2), 2)
            pygame.draw.line(surf, SHELF_PLANK, (cx, ry + th // 2), (cx + tw // 2, ry), 2)
            
            # Colocar cajitas/píxeles imitando productos alineados en la repisa derecha
            for slot in range(4):
                px = cx + 4 + (slot * 6)
                py = ry + 2 + (slot * 3)
                p_color = random.choice(PRODUCT_COLORS)
                p_height = random.randint(4, 7)
                # Dibujar bloque de producto individual
                pygame.draw.rect(surf, p_color, (px, py - p_height, 4, p_height))
                pygame.draw.rect(surf, (20, 20, 20), (px, py - p_height, 4, p_height), 1) # Borde pixel-art

        # Pilares del armazón frontal
        pillar_color = (50, 55, 65)
        pygame.draw.line(surf, pillar_color, (cx, cy - block_h + th // 2), (cx, cy + th // 2), 2)
        pygame.draw.line(surf, pillar_color, (cx - tw // 2, cy - block_h), (cx - tw // 2, cy), 1)
        pygame.draw.line(surf, pillar_color, (cx + tw // 2, cy - block_h), (cx + tw // 2, cy), 1)

        return surf

    # -------------------------------------------------------------------------
    # Cajero / terminal de cobro
    # -------------------------------------------------------------------------

    @staticmethod
    def create_cajero(ocupado: bool = False) -> pygame.Surface:
        """
        Dibuja una estación de cobro retro isométrica:
        - Mostrador con caja registradora pixelada.
        - Pantalla CRT verde retro.
        - Indicador luminoso: verde (libre) / rojo (ocupado).

        Dimensiones: 72 x 68 px
        """
        sw, sh = 72, 68
        surf = pygame.Surface((sw, sh), pygame.SRCALPHA)

        cx, cy = sw // 2, sh - TILE_H // 2 - 2
        block_h = 22

        # ── Cuerpo principal del mostrador ────────────────────────────────────
        top_pts   = SpriteFactory._iso_top_face(cx, cy - block_h, TILE_W - 8, TILE_H - 4)
        left_pts  = SpriteFactory._iso_left_face(cx, cy - block_h, TILE_W - 8, TILE_H - 4, block_h)
        right_pts = SpriteFactory._iso_right_face(cx, cy - block_h, TILE_W - 8, TILE_H - 4, block_h)

        pygame.draw.polygon(surf, CAJERO_FRONT, right_pts)
        pygame.draw.polygon(surf, CAJERO_SIDE,  left_pts)
        pygame.draw.polygon(surf, CAJERO_TOP,   top_pts)

        # Bordes del mostrador
        for pts in [top_pts, left_pts, right_pts]:
            pygame.draw.polygon(surf, (40, 32, 25), pts, 1)

        # ── Caja registradora sobre el mostrador ──────────────────────────────
        reg_x = cx - 4
        reg_y = cy - block_h - 12
        # Cuerpo de la registradora
        pygame.draw.rect(surf, (55, 50, 45), (reg_x - 8, reg_y, 16, 10))
        pygame.draw.rect(surf, (35, 30, 25), (reg_x - 8, reg_y, 16, 10), 1)
        # Pantalla CRT verde
        pygame.draw.rect(surf, SCREEN_GREEN, (reg_x - 6, reg_y + 1, 8, 5))
        # Teclado numérico pixelado (3x3 puntos)
        for kr in range(3):
            for kc in range(3):
                pygame.draw.rect(surf, (80, 75, 70),
                                 (reg_x + 2 + kc * 3, reg_y + 2 + kr * 2, 2, 1))

        # ── Indicador luminoso de estado ──────────────────────────────────────
        indicator_color = CAJERO_BUSY if ocupado else CAJERO_FREE
        ind_x = cx + 18
        ind_y = cy - block_h - 4
        # Halo del indicador
        pygame.draw.circle(surf, (*indicator_color[:3], 80), (ind_x, ind_y), 5)
        # Núcleo del indicador
        pygame.draw.circle(surf, indicator_color, (ind_x, ind_y), 3)
        pygame.draw.circle(surf, (255, 255, 255), (ind_x - 1, ind_y - 1), 1)

        return surf

    # -------------------------------------------------------------------------
    # Cliente / avatar de comprador
    # -------------------------------------------------------------------------

    @staticmethod
    def create_cliente(color: tuple[int, int, int], productos: int) -> pygame.Surface:
        """
        Dibuja un avatar pixel-art de comprador:
        - Piernas oscuras, torso del color provisto, cabeza color piel.
        - Indicador circular flotante superior con el número de productos.

        Dimensiones: 32 x 52 px (incluye burbuja de productos)
        """
        sw, sh = 32, 52
        surf = pygame.Surface((sw, sh), pygame.SRCALPHA)

        # Punto de anclaje: base del sprite → el centro X y el fondo Y
        # están alineados con el centro del rombo de suelo.
        cx = sw // 2   # = 16

        # ── Piernas ──────────────────────────────────────────────────────────
        # Pierna izquierda
        pygame.draw.rect(surf, LEGS_COLOR, (cx - 7, sh - 18, 5, 14))
        # Pierna derecha
        pygame.draw.rect(surf, LEGS_COLOR, (cx + 2,  sh - 18, 5, 14))
        # Zapatos
        pygame.draw.rect(surf, (30, 28, 40), (cx - 8, sh - 6,  6, 4))
        pygame.draw.rect(surf, (30, 28, 40), (cx + 2,  sh - 6,  6, 4))

        # ── Torso ────────────────────────────────────────────────────────────
        pygame.draw.rect(surf, color, (cx - 7, sh - 30, 14, 14))
        # Línea de cuello
        pygame.draw.line(surf, (max(0, color[0] - 40), max(0, color[1] - 40),
                                max(0, color[2] - 40)),
                         (cx - 7, sh - 30), (cx + 6, sh - 30), 1)
        # Detalle de bolsillo
        pygame.draw.rect(surf, (max(0, color[0] - 50), max(0, color[1] - 50),
                                max(0, color[2] - 50)),
                         (cx - 5, sh - 27, 4, 3))

        # ── Brazos ───────────────────────────────────────────────────────────
        pygame.draw.rect(surf, color, (cx - 11, sh - 29, 4, 9))
        pygame.draw.rect(surf, color, (cx + 7,  sh - 29, 4, 9))
        # Manos
        pygame.draw.rect(surf, SKIN_COLOR, (cx - 11, sh - 22, 4, 3))
        pygame.draw.rect(surf, SKIN_COLOR, (cx + 7,  sh - 22, 4, 3))

        # ── Cabeza ───────────────────────────────────────────────────────────
        head_y = sh - 42
        pygame.draw.rect(surf, SKIN_COLOR, (cx - 5, head_y, 10, 10))
        # Ojos
        pygame.draw.rect(surf, (40, 35, 30), (cx - 3, head_y + 3, 2, 2))
        pygame.draw.rect(surf, (40, 35, 30), (cx + 1, head_y + 3, 2, 2))
        # Cabello pixelado
        hair_color = (80, 55, 30)
        pygame.draw.rect(surf, hair_color, (cx - 5, head_y,     10, 2))
        pygame.draw.rect(surf, hair_color, (cx - 5, head_y,     2,  5))
        pygame.draw.rect(surf, hair_color, (cx + 3, head_y,     2,  5))

        # ── Indicador flotante de productos ──────────────────────────────────
        bubble_r = 8
        bubble_cx = cx + 8
        bubble_cy = 6
        # Fondo semi-transparente del globo
        bubble_surf = pygame.Surface((bubble_r * 2 + 2, bubble_r * 2 + 2), pygame.SRCALPHA)
        pygame.draw.circle(bubble_surf, BUBBLE_BG, (bubble_r, bubble_r), bubble_r)
        pygame.draw.circle(bubble_surf, ACCENT_COLOR := (255, 200, 50),
                           (bubble_r, bubble_r), bubble_r, 1)
        surf.blit(bubble_surf, (bubble_cx - bubble_r - 1, bubble_cy - bubble_r - 1))
        # Número de productos
        font = pygame.font.SysFont("monospace", 9, bold=True)
        txt = font.render(str(min(productos, 99)), True, BUBBLE_TEXT)
        surf.blit(txt, (bubble_cx - txt.get_width() // 2,
                        bubble_cy - txt.get_height() // 2))

        return surf
