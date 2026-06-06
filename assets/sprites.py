import pygame
import math
from assets.config import *

# ============================================================================
# SPRITE CLASSES
# ============================================================================

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, gravity, flap_power, bird_color="yellow"):
        super().__init__()
        self.x, self.y, self.start_y = float(x), float(y), float(y)
        self.velocity, self.tilt = 0.0, 0.0
        self.frame, self.frame_counter, self.hover_tick = 0, 0, 0
        
        self.gravity = gravity
        self.flap_power = flap_power
        
        self.images = []
        frames = ['upflap', 'midflap', 'downflap']
        for fname in frames:
            try: 
                img = pygame.image.load(f"assets/sprites/{bird_color}bird-{fname}.png").convert_alpha()
            except: 
                img = pygame.Surface((BIRD_WIDTH, BIRD_HEIGHT), pygame.SRCALPHA)
                pygame.draw.ellipse(img, (255, 200, 0), (0, 0, BIRD_WIDTH, BIRD_HEIGHT))
            self.images.append(img)
        
        self.image = self.images[0]
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
    
    def hover(self):
        self.hover_tick += 1
        self.y = self.start_y + math.sin(self.hover_tick * 0.1) * 6
        self.rect.centery = int(self.y)
        self.tilt = 0
        self._animate_wings()
    
    def update_playing(self):
        self.velocity = min(self.velocity + self.gravity, 10)
        if self.velocity < -9: self.velocity = -9
        self.y += self.velocity
        
        if self.velocity < 0: self.tilt = min(self.tilt + 4, 25)
        else: self.tilt = max(self.tilt - 3, -90)
        
        self._animate_wings()
        self._update_image()
    
    def update_dead(self):
        if self.rect.bottom < GROUND_Y:
            self.velocity = min(self.velocity + self.gravity * 1.5, 12)
            self.y += self.velocity
            self.tilt = max(self.tilt - 6, -90)
            self._update_image()
        else:
            self.y = GROUND_Y - self.rect.height // 2
            self.rect.centery = int(self.y)

    def _animate_wings(self):
        self.frame_counter += 1
        if self.frame_counter >= 5:
            self.frame_counter = 0
            self.frame = (self.frame + 1) % 3
            self._update_image()

    def _update_image(self):
        self.image = pygame.transform.rotate(self.images[self.frame], self.tilt)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center=(self.x, self.y))
    
    def flap(self):
        self.velocity = self.flap_power
        self.tilt = 25


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, gap_y, is_top, pipe_img, gap, speed):
        super().__init__()
        self.x, self.is_top, self.passed = float(x), is_top, False
        self.speed = speed
        self.image = pygame.transform.flip(pipe_img, False, True) if is_top else pipe_img
        self.rect = self.image.get_rect()
        self.rect.x = int(self.x)
        self.rect.y = gap_y - PIPE_HEIGHT if is_top else gap_y + gap
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self):
        self.x -= self.speed
        self.rect.x = int(self.x)
    
    def is_offscreen(self): 
        return self.rect.right < 0


class Ground(pygame.sprite.Sprite):
    def __init__(self, x, ground_img, speed):
        super().__init__()
        self.image = ground_img
        self.speed = speed
        self.rect = self.image.get_rect(topleft=(x, GROUND_Y))
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self): 
        self.rect.x -= self.speed
