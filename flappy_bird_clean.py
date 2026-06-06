"""
Flappy Bird - Ultimate Edition
Modular implementation with separate asset files

This file serves as the main entry point.
All game logic is organized in the assets package.
"""

from assets.game import Game

if __name__ == "__main__":
    Game().run()
import pygame
import random
import math
import json
import os
from enum import Enum

# ============================================================================
# CẤU HÌNH & HẰNG SỐ CƠ BẢN
# ============================================================================
class GameState(Enum):
    WELCOME = 0
    GET_READY = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60

BIRD_WIDTH, BIRD_HEIGHT = 34, 24
PIPE_WIDTH, PIPE_HEIGHT = 52, 320

GROUND_WIDTH, GROUND_HEIGHT = 336, 112
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

# --- MÀU SẮC CHUẨN ---
C_OUTLINE = (84, 56, 71)
C_WHITE = (255, 255, 255)
C_ORANGE_BTN = (232, 97, 1)
C_BOARD = (222, 216, 149)
C_TEXT_ORANGE = (244, 150, 30)

# MÀU THEO CHẾ ĐỘ CHƠI
MODE_COLORS = {
    "EASY": (116, 191, 46),   # Xanh lá
    "NORMAL": (232, 97, 1),   # Cam
    "HARD": (220, 50, 50)     # Đỏ
}

# ============================================================================
# HELPER: VẼ TEXT VÀ NÚT BẤM CHUẨN PIXEL-ART
# ============================================================================
def draw_outlined_text(surface, text, font, color, outline_color, pos, center=True, shadow=False):
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
    shadow_rect = pygame.Rect(rect.x - 2, rect.y - 2, rect.width + 4, rect.height + 6)
    pygame.draw.rect(surface, C_OUTLINE, shadow_rect, border_radius=4)
    white_rect = pygame.Rect(rect.x, rect.y, rect.width, rect.height)
    pygame.draw.rect(surface, C_WHITE, white_rect, border_radius=3)
    inner_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
    pygame.draw.rect(surface, color, inner_rect, border_radius=2)
    draw_outlined_text(surface, text, font, C_WHITE, C_OUTLINE, rect.center)

# ============================================================================
# SPRITE CLASSES
# ============================================================================
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y, gravity, flap_power):
        super().__init__()
        self.x, self.y, self.start_y = float(x), float(y), float(y)
        self.velocity, self.tilt = 0.0, 0.0
        self.frame, self.frame_counter, self.hover_tick = 0, 0, 0
        
        self.gravity = gravity
        self.flap_power = flap_power
        
        self.images = []
        frames = ['upflap', 'midflap', 'downflap']
        for fname in frames:
            try: img = pygame.image.load(f"assets/sprites/yellowbird-{fname}.png").convert_alpha()
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
    
    def is_offscreen(self): return self.rect.right < 0

class Ground(pygame.sprite.Sprite):
    def __init__(self, x, ground_img, speed):
        super().__init__()
        self.image = ground_img
        self.speed = speed
        self.rect = self.image.get_rect(topleft=(x, GROUND_Y))
        self.mask = pygame.mask.from_surface(self.image)
    
    def update(self): self.rect.x -= self.speed

# ============================================================================
# MANAGERS
# ============================================================================
class ScoreManager:
    SCORE_FILE = "highscore.json"
    def __init__(self):
        self.score = 0
        data = self.load_data()
        self.high_score = data.get("high_score", 0)
        self.recent_scores = data.get("recent_scores", [])
        self.last_mode = data.get("last_mode", "NORMAL")
    
    def load_data(self):
        if os.path.exists(self.SCORE_FILE):
            try:
                with open(self.SCORE_FILE, 'r') as f: return json.load(f)
            except: pass
        return {}
    
    def save_data(self):
        data = {
            "high_score": self.high_score,
            "recent_scores": self.recent_scores,
            "last_mode": self.last_mode
        }
        with open(self.SCORE_FILE, 'w') as f: json.dump(data, f)
    
    def add_point(self):
        self.score += 1
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_data()
            
    def save_game_score(self):
        self.recent_scores.insert(0, self.score)
        if len(self.recent_scores) > 3:
            self.recent_scores = self.recent_scores[:3]
        self.save_data()
    
    def reset(self): self.score = 0
    
    def get_medal(self):
        if self.score >= 40: return "platinum"
        elif self.score >= 30: return "gold"
        elif self.score >= 20: return "silver"
        elif self.score >= 10: return "bronze"
        return None

# ============================================================================
# MAIN GAME
# ============================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - Ultimate Edition")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.WELCOME
        self.prev_state = GameState.WELCOME
        
        # --- LOAD FONTS ---
        try:
            font_path = "assets/fonts/flappy-font.ttf"
            self.font_title = pygame.font.Font(font_path, 48)
            self.font_score = pygame.font.Font(font_path, 60)
            self.font_medium = pygame.font.Font(font_path, 32)
            self.font_val = pygame.font.Font(font_path, 26) 
            self.font_btn = pygame.font.Font(font_path, 24)
            self.font_board = pygame.font.Font(font_path, 18)
        except:
            self.font_title = pygame.font.SysFont("impact", 48)
            self.font_score = pygame.font.SysFont("impact", 60)
            self.font_medium = pygame.font.SysFont("impact", 32)
            self.font_val = pygame.font.SysFont("impact", 26)
            self.font_btn = pygame.font.SysFont("impact", 24)
            self.font_board = pygame.font.SysFont("impact", 18)
        
        # --- LOAD ASSETS ---
        try: self.bg_img = pygame.image.load("assets/sprites/background-day.png").convert()
        except: self.bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); self.bg_img.fill((112, 197, 206))

        try: self.pipe_img = pygame.image.load("assets/sprites/pipe-green.png").convert_alpha()
        except: self.pipe_img = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT)); self.pipe_img.fill((116, 191, 46))

        try: self.ground_img = pygame.image.load("assets/sprites/base.png").convert_alpha()
        except: self.ground_img = pygame.Surface((GROUND_WIDTH, GROUND_HEIGHT)); self.ground_img.fill(C_BOARD)

        # --- SOUNDS ---
        pygame.mixer.init()
        self.sounds = {}
        for key in ['wing', 'point', 'hit', 'die', 'swoosh']:
            try: self.sounds[key] = pygame.mixer.Sound(f"assets/audio/{key}.wav")
            except: self.sounds[key] = None
        
        self.bird_group = pygame.sprite.GroupSingle()
        self.pipe_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.score_mgr = ScoreManager()
        
        # --- RECTS GIAO DIỆN ---
        center_x = SCREEN_WIDTH // 2
        self.btn_play_rect = pygame.Rect(center_x - 100, 350, 90, 40)
        self.btn_rank_rect = pygame.Rect(center_x + 10, 350, 90, 40)
        self.btn_menu_rect = pygame.Rect(center_x - 45, 400, 90, 40) # Nút về Menu
        
        self.about_btn_rect = pygame.Rect(SCREEN_WIDTH - 45, SCREEN_HEIGHT - 45, 30, 30)
        
        # Nút góc trái trên
        self.btn_mode_rect = pygame.Rect(10, 10, 90, 35) # Chỉnh độ khó
        self.btn_pause_rect = pygame.Rect(10, 10, 40, 40) # Pause khi chơi
        
        # Nút cho màn hình Pause
        self.btn_resume_pause = pygame.Rect(center_x - 100, 300, 90, 40)
        self.btn_menu_pause = pygame.Rect(center_x + 10, 300, 90, 40)
        
        self.show_about_popup = False
        self.show_recent_scores = False
        
        # Thiết lập độ khó ban đầu từ lần chơi cuối
        self.mode = self.score_mgr.last_mode
        self.apply_difficulty()
        self._init_game()
    
    def play_sound(self, key):
        if self.sounds[key]: self.sounds[key].play()
        
    def toggle_mode(self):
        """Chuyển đổi độ khó"""
        modes = ["EASY", "NORMAL", "HARD"]
        idx = modes.index(self.mode)
        self.mode = modes[(idx + 1) % 3]
        self.score_mgr.last_mode = self.mode
        self.score_mgr.save_data()
        self.apply_difficulty()
        self._init_game()
        self.play_sound('swoosh')

    def apply_difficulty(self):
        """Thiết lập thông số vật lý và Mật độ cột (spawn_interval)"""
        if self.mode == "EASY":
            self.d_gap = 140
            self.d_speed = 2.5
            self.d_grav = 0.4
            self.d_flap = -6.5
            self.d_spawn = 115   # Cột cách rất xa nhau (chờ 115 frame)
        elif self.mode == "NORMAL":
            self.d_gap = 100
            self.d_speed = 3.0
            self.d_grav = 0.5
            self.d_flap = -7.5
            self.d_spawn = 90    # Chuẩn gốc (90 frame)
        elif self.mode == "HARD":
            self.d_gap = 85
            self.d_speed = 4.0
            self.d_grav = 0.6
            self.d_flap = -8.0
            self.d_spawn = 65    # Cột san sát nhau, liên tục (65 frame)
    
    def _init_game(self):
        self.bird_group.add(Bird(SCREEN_WIDTH * 0.3, 240, self.d_grav, self.d_flap))
        self.pipe_group.empty()
        self.ground_group.empty()
        for i in range(2): self.ground_group.add(Ground(i * GROUND_WIDTH, self.ground_img, self.d_speed))
        
        self.score_mgr.reset()
        self.pipe_spawn_counter = 0
        self.flash_alpha, self.shake_frames = 0, 0
        self.scoreboard_y = SCREEN_HEIGHT
        self.show_about_popup = False
        self.show_recent_scores = False
    
    def _spawn_pipe(self):
        gap_y = random.randint(120, GROUND_Y - self.d_gap - 60)
        self.pipe_group.add(Pipe(SCREEN_WIDTH + 10, gap_y, True, self.pipe_img, self.d_gap, self.d_speed))
        self.pipe_group.add(Pipe(SCREEN_WIDTH + 10, gap_y, False, self.pipe_img, self.d_gap, self.d_speed))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_recent_scores:
                    self.show_recent_scores = False
                    self.play_sound('swoosh')
                    continue
                if self.show_about_popup:
                    self.show_about_popup = False
                    continue

                if self.state == GameState.WELCOME:
                    if self.about_btn_rect.collidepoint(event.pos):
                        self.show_about_popup = True
                        self.play_sound('swoosh')
                    elif self.btn_mode_rect.collidepoint(event.pos):
                        self.toggle_mode()
                    elif self.btn_play_rect.collidepoint(event.pos):
                        self.state = GameState.GET_READY
                        self.bird_group.sprite.start_y = 240
                        self.bird_group.sprite.y = 240
                        self.play_sound('swoosh')
                    elif self.btn_rank_rect.collidepoint(event.pos):
                        self.show_recent_scores = True
                        self.play_sound('swoosh')
                
                elif self.state == GameState.GET_READY:
                    if self.btn_pause_rect.collidepoint(event.pos):
                        self.prev_state = GameState.GET_READY
                        self.state = GameState.PAUSED
                        self.play_sound('swoosh')
                    else:
                        self.state = GameState.PLAYING
                        self.bird_group.sprite.flap()
                        self.play_sound('wing')
                        self._spawn_pipe()

                elif self.state == GameState.PLAYING:
                    if self.btn_pause_rect.collidepoint(event.pos):
                        self.prev_state = GameState.PLAYING
                        self.state = GameState.PAUSED
                        self.play_sound('swoosh')
                    else:
                        self.bird_group.sprite.flap()
                        self.play_sound('wing')
                
                elif self.state == GameState.PAUSED:
                    # Nút góc trái hoặc nút Resume
                    if self.btn_pause_rect.collidepoint(event.pos) or self.btn_resume_pause.collidepoint(event.pos):
                        self.state = self.prev_state
                        self.play_sound('swoosh')
                    # Nút về Menu
                    elif self.btn_menu_pause.collidepoint(event.pos):
                        self.state = GameState.WELCOME
                        self._init_game()
                        self.play_sound('swoosh')
                
                elif self.state == GameState.GAME_OVER:
                    if self.bird_group.sprite.rect.bottom >= GROUND_Y and self.scoreboard_y <= 160:
                        if self.btn_play_rect.collidepoint(event.pos):
                            self.state = GameState.GET_READY
                            self._init_game()
                            self.play_sound('swoosh')
                        elif self.btn_rank_rect.collidepoint(event.pos):
                            self.show_recent_scores = True
                            self.play_sound('swoosh')
                        elif self.btn_menu_rect.collidepoint(event.pos):
                            self.state = GameState.WELCOME
                            self._init_game()
                            self.play_sound('swoosh')
            
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.state == GameState.GET_READY:
                    self.state = GameState.PLAYING
                    self.bird_group.sprite.flap()
                    self.play_sound('wing')
                    self._spawn_pipe()
                elif self.state == GameState.PLAYING:
                    self.bird_group.sprite.flap()
                    self.play_sound('wing')
    
    def update(self):
        if self.state in [GameState.WELCOME, GameState.GET_READY]:
            self.bird_group.sprite.hover()
            self.ground_group.update()
            self._manage_ground()
        
        elif self.state == GameState.PLAYING:
            self.bird_group.sprite.update_playing()
            self.pipe_group.update()
            self.ground_group.update()
            self._manage_ground()
            
            dead_pipes = [p for p in self.pipe_group if p.is_offscreen()]
            for p in dead_pipes: self.pipe_group.remove(p)
            
            # -----------------------------------------------------
            # SPAWN ỐNG DỰA THEO ĐỘ KHÓ (self.d_spawn)
            # -----------------------------------------------------
            self.pipe_spawn_counter += 1
            if self.pipe_spawn_counter >= self.d_spawn:
                self._spawn_pipe()
                self.pipe_spawn_counter = 0
            
            for pipe in self.pipe_group:
                if pipe.is_top and not pipe.passed and pipe.rect.right < self.bird_group.sprite.rect.left:
                    pipe.passed = True
                    self.score_mgr.add_point()
                    self.play_sound('point')
            self._check_collisions()
            
        elif self.state == GameState.GAME_OVER:
            self.bird_group.sprite.update_dead()
            if self.bird_group.sprite.rect.bottom >= GROUND_Y:
                target_y = 160
                if self.scoreboard_y > target_y:
                    self.scoreboard_y -= max(2, (self.scoreboard_y - target_y) * 0.15)
            if self.flash_alpha > 0: self.flash_alpha = max(0, self.flash_alpha - 20)
            if self.shake_frames > 0: self.shake_frames -= 1
    
    def _manage_ground(self):
        grounds = self.ground_group.sprites()
        if len(grounds) > 0 and grounds[0].rect.right <= 0:
            self.ground_group.remove(grounds[0])
            self.ground_group.add(Ground(grounds[-1].rect.right, self.ground_img, self.d_speed))
    
    def _check_collisions(self):
        bird = self.bird_group.sprite
        if pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False, pygame.sprite.collide_mask) or bird.rect.top < -50:
            self.play_sound('hit')
            self.play_sound('die')
            self._trigger_game_over()
        elif pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False, pygame.sprite.collide_mask):
            self.play_sound('hit')
            self._trigger_game_over()
    
    def _trigger_game_over(self):
        self.state = GameState.GAME_OVER
        self.flash_alpha, self.shake_frames = 255, 10
        self.score_mgr.save_game_score()
    
    def draw(self):
        self.screen.blit(self.bg_img, (0, 0))
        if self.state == GameState.WELCOME: self._draw_welcome()
        elif self.state == GameState.GET_READY: self._draw_get_ready()
        elif self.state == GameState.PLAYING: self._draw_playing()
        elif self.state == GameState.PAUSED: self._draw_paused()
        elif self.state == GameState.GAME_OVER: self._draw_game_over()
        pygame.display.flip()
    
    def _draw_welcome(self):
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        
        draw_outlined_text(self.screen, "Flappy Bird", self.font_title, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, 120), shadow=True)
        draw_flappy_button(self.screen, self.btn_play_rect, "PLAY", self.font_btn)
        draw_flappy_button(self.screen, self.btn_rank_rect, "SCORE", self.font_btn)
        
        # Nút MODE ở góc trái trên
        btn_color = MODE_COLORS.get(self.mode, C_ORANGE_BTN)
        draw_flappy_button(self.screen, self.btn_mode_rect, self.mode, self.font_board, color=btn_color)
        
        # Nút About (?)
        pygame.draw.circle(self.screen, C_OUTLINE, self.about_btn_rect.center, 15)
        pygame.draw.circle(self.screen, C_ORANGE_BTN, self.about_btn_rect.center, 13)
        draw_outlined_text(self.screen, "?", self.font_board, C_WHITE, C_OUTLINE, self.about_btn_rect.center)
        
        if self.show_about_popup: self._draw_about_popup()
        if self.show_recent_scores: self._draw_recent_scores()

    def _draw_about_popup(self):
        popup_rect = pygame.Rect((SCREEN_WIDTH - 220) // 2, 140, 220, 160)
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        pygame.draw.rect(self.screen, C_BOARD, popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, C_OUTLINE, popup_rect, 4, border_radius=10)
        draw_outlined_text(self.screen, "ABOUT", self.font_medium, C_WHITE, C_OUTLINE, (SCREEN_WIDTH//2, 165))
        f_txt = pygame.font.SysFont("arial", 14, bold=True)
        self.screen.blit(f_txt.render("Dev by: Minh", True, C_OUTLINE), (popup_rect.x + 20, 200))
        self.screen.blit(f_txt.render("Ultimate Edition", True, C_OUTLINE), (popup_rect.x + 20, 225))
        self.screen.blit(f_txt.render("(Click outside to close)", True, (200, 50, 50)), (popup_rect.x + 25, 270))

    def _draw_get_ready(self):
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        draw_outlined_text(self.screen, "Get Ready!", self.font_medium, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, 130), shadow=True)
        tap_y = 300
        pygame.draw.polygon(self.screen, C_WHITE, [(SCREEN_WIDTH//2, tap_y), (SCREEN_WIDTH//2-10, tap_y+15), (SCREEN_WIDTH//2+10, tap_y+15)])
        pygame.draw.polygon(self.screen, C_OUTLINE, [(SCREEN_WIDTH//2, tap_y), (SCREEN_WIDTH//2-10, tap_y+15), (SCREEN_WIDTH//2+10, tap_y+15)], 2)
        draw_outlined_text(self.screen, "TAP TO FLAP", self.font_board, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, tap_y + 35))
        
        # Nút Pause nhỏ
        draw_flappy_button(self.screen, self.btn_pause_rect, "II", self.font_board, color=C_BOARD)

    def _draw_playing(self):
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        draw_outlined_text(self.screen, str(self.score_mgr.score), self.font_score, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, 80), shadow=True)
        
        # Nút Pause
        draw_flappy_button(self.screen, self.btn_pause_rect, "II", self.font_board, color=C_BOARD)
    
    def _draw_paused(self):
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        draw_outlined_text(self.screen, "PAUSED", self.font_title, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40), shadow=True)
        
        # Nút RESUME (Trái) và MENU (Phải)
        draw_flappy_button(self.screen, self.btn_resume_pause, "RESUME", self.font_btn, color=(116, 191, 46))
        draw_flappy_button(self.screen, self.btn_menu_pause, "MENU", self.font_btn, color=C_ORANGE_BTN)
    
    def _draw_game_over(self):
        dx, dy = (random.randint(-4, 4), random.randint(-4, 4)) if self.shake_frames > 0 else (0, 0)
        tsurf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        tsurf.blit(self.bg_img, (0, 0))
        self.pipe_group.draw(tsurf); self.ground_group.draw(tsurf); self.bird_group.draw(tsurf)
        self.screen.blit(tsurf, (dx, dy))
        
        if self.flash_alpha > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, int(self.flash_alpha)))
            self.screen.blit(flash, (0, 0))
        
        if self.bird_group.sprite.rect.bottom >= GROUND_Y:
            self._draw_scoreboard()
    
    def _draw_scoreboard(self):
        draw_outlined_text(self.screen, "GAME OVER", self.font_title, C_TEXT_ORANGE, C_OUTLINE, (SCREEN_WIDTH // 2, self.scoreboard_y - 60), shadow=True)
        
        board = pygame.Rect((SCREEN_WIDTH - 220) // 2, self.scoreboard_y, 220, 115)
        pygame.draw.rect(self.screen, C_BOARD, board, border_radius=8)
        pygame.draw.rect(self.screen, C_OUTLINE, board, 3, border_radius=8)
        
        medal_pos = (board.x + 50, board.y + 58)
        pygame.draw.circle(self.screen, C_OUTLINE, (medal_pos[0], medal_pos[1] + 2), 22)
        pygame.draw.circle(self.screen, (200, 190, 130), medal_pos, 22)
        
        medal_type = self.score_mgr.get_medal()
        if medal_type:
            medal_colors = {"bronze": (205, 127, 50), "silver": (230, 230, 230), "gold": (255, 215, 0), "platinum": (200, 240, 240)}
            color = medal_colors.get(medal_type, (200, 200, 200))
            pygame.draw.circle(self.screen, color, medal_pos, 22)
            pygame.draw.circle(self.screen, C_WHITE, medal_pos, 22, width=2)
            highlight = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(highlight, (255, 255, 255, 150), (6, 6), 6)
            self.screen.blit(highlight, (medal_pos[0] - 10, medal_pos[1] - 10))

        right_margin = board.right - 25
        lbl_score = self.font_board.render("SCORE", True, C_TEXT_ORANGE)
        self.screen.blit(lbl_score, (right_margin - lbl_score.get_width(), board.y + 15))
        draw_outlined_text(self.screen, str(self.score_mgr.score), self.font_val, C_WHITE, C_OUTLINE, (right_margin - lbl_score.get_width()//2, board.y + 45))
        
        lbl_best = self.font_board.render("BEST", True, C_TEXT_ORANGE)
        self.screen.blit(lbl_best, (right_margin - lbl_best.get_width(), board.y + 65))
        draw_outlined_text(self.screen, str(self.score_mgr.high_score), self.font_val, C_WHITE, C_OUTLINE, (right_margin - lbl_best.get_width()//2, board.y + 95))
        
        if self.scoreboard_y <= 160:
            # 3 NÚT: PLAY, RANK, VÀ MENU MỚI Ở DƯỚI
            draw_flappy_button(self.screen, self.btn_play_rect, "PLAY", self.font_btn)
            draw_flappy_button(self.screen, self.btn_rank_rect, "SCORE", self.font_btn)
            draw_flappy_button(self.screen, self.btn_menu_rect, "MENU", self.font_btn, color=(100, 150, 200))
            
            if self.show_recent_scores: self._draw_recent_scores()

    def _draw_recent_scores(self):
        popup_w, popup_h = 200, 210
        popup_y = (SCREEN_HEIGHT - popup_h) // 2
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        popup_rect = pygame.Rect((SCREEN_WIDTH - popup_w) // 2, popup_y, popup_w, popup_h)
        pygame.draw.rect(self.screen, C_BOARD, popup_rect, border_radius=10)
        pygame.draw.rect(self.screen, C_OUTLINE, popup_rect, 4, border_radius=10)
        
        draw_outlined_text(self.screen, "RECENT", self.font_medium, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, popup_y + 30))
        
        recent = self.score_mgr.recent_scores
        for i in range(3):
            y_pos = popup_y + 80 + i * 35
            if i < len(recent):
                draw_outlined_text(self.screen, f"#{i+1}:   {recent[i]}", self.font_val, C_TEXT_ORANGE, C_OUTLINE, (SCREEN_WIDTH // 2, y_pos))
            else:
                draw_outlined_text(self.screen, "--", self.font_board, C_OUTLINE, C_OUTLINE, (SCREEN_WIDTH // 2, y_pos))
        
        f_txt = pygame.font.SysFont("arial", 13, bold=True)
        self.screen.blit(f_txt.render("(Click anywhere to close)", True, (200, 50, 50)), (popup_rect.x + 20, popup_y + popup_h - 25))

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    Game().run()