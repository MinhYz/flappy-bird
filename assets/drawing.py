import pygame
from assets.config import *

# ============================================================================
# DRAWING UTILITIES
# ============================================================================

def draw_outlined_text(surface, text, font, color, outline_color, pos, center=True, shadow=False):
    """Draw text with outlined/bold effect"""
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=pos) if center else text_surf.get_rect(topleft=pos)
    
    if shadow:
        shadow_surf = font.render(text, True, outline_color)
        surface.blit(shadow_surf, (text_rect.x + 3, text_rect.y + 4))
        
    for dx, dy in [(-2,-2), (2,-2), (-2,2), (2,2), (-2,0), (2,0), (0,-2), (0,2)]:
        out_surf = font.render(text, True, outline_color)
        out_rect = out_surf.get_rect(center=(pos[0]+dx, pos[1]+dy)) if center else out_surf.get_rect(topleft=(pos[0]+dx, pos[1]+dy))
        surface.blit(out_surf, out_rect)
        
    surface.blit(text_surf, text_rect)


def draw_flappy_button(surface, rect, text, font, color=C_ORANGE_BTN):
    """Draw a Flappy Bird styled button"""
    shadow_rect = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 6)
    pygame.draw.rect(surface, C_OUTLINE, shadow_rect, border_radius=4)
    white_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
    pygame.draw.rect(surface, C_WHITE, white_rect, border_radius=3)
    inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
    pygame.draw.rect(surface, color, inner_rect, border_radius=2)
    draw_outlined_text(surface, text, font, C_WHITE, C_OUTLINE, rect.center)
