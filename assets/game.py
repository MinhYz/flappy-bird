import pygame
import random
from assets.config import *
from assets.sprites import Bird, Pipe, Ground
from assets.managers import ScoreManager
from assets.drawing import draw_outlined_text, draw_flappy_button

# ============================================================================
# MAIN GAME CLASS
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
        
        # --- RANDOM ASSETS SELECTION ---
        self.bird_color = random.choice(BIRD_COLORS)
        self.pipe_color = random.choice(PIPE_COLORS)
        self.bg_type = random.choice(BACKGROUND_TYPES)
        
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
        try: 
            self.bg_img = pygame.image.load(f"assets/sprites/background-{self.bg_type}.png").convert()
        except: 
            self.bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); 
            self.bg_img.fill((112, 197, 206))

        try: 
            self.pipe_img = pygame.image.load(f"assets/sprites/pipe-{self.pipe_color}.png").convert_alpha()
        except: 
            self.pipe_img = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT)); 
            self.pipe_img.fill((116, 191, 46))

        try: 
            self.ground_img = pygame.image.load("assets/sprites/base.png").convert_alpha()
        except: 
            self.ground_img = pygame.Surface((GROUND_WIDTH, GROUND_HEIGHT)); 
            self.ground_img.fill(C_BOARD)
        
        # --- LOAD MESSAGE IMAGES ---
        try:
            self.gameover_img = pygame.image.load("assets/sprites/gameover.png").convert_alpha()
        except:
            self.gameover_img = None
        
        try:
            self.message_img = pygame.image.load("assets/sprites/message.png").convert_alpha()
        except:
            self.message_img = None

        # --- SOUNDS ---
        pygame.mixer.init()
        self.sounds = {}
        for key in ['wing', 'point', 'hit', 'die', 'swoosh']:
            try: 
                self.sounds[key] = pygame.mixer.Sound(f"assets/audio/{key}.wav")
            except: 
                self.sounds[key] = None
        
        self.bird_group = pygame.sprite.GroupSingle()
        self.pipe_group = pygame.sprite.Group()
        self.ground_group = pygame.sprite.Group()
        self.score_mgr = ScoreManager()
        
        # --- UI RECTS ---
        center_x = SCREEN_WIDTH // 2
        self.btn_play_rect = pygame.Rect(center_x - 100, 350, 90, 40)
        self.btn_rank_rect = pygame.Rect(center_x + 10, 350, 90, 40)
        self.btn_menu_rect = pygame.Rect(center_x - 45, 400, 90, 40)
        
        self.about_btn_rect = pygame.Rect(SCREEN_WIDTH - 45, SCREEN_HEIGHT - 45, 30, 30)
        
        self.btn_mode_rect = pygame.Rect(10, 10, 90, 35)
        self.btn_pause_rect = pygame.Rect(10, 10, 40, 40)
        
        self.btn_resume_pause = pygame.Rect(center_x - 100, 300, 90, 40)
        self.btn_menu_pause = pygame.Rect(center_x + 10, 300, 90, 40)
        
        self.show_about_popup = False
        self.show_recent_scores = False
        
        # Difficulty setup
        self.mode = self.score_mgr.last_mode
        self.apply_difficulty()
        self._init_game()
    
    def play_sound(self, key):
        if self.sounds[key]: 
            self.sounds[key].play()
        
    def toggle_mode(self):
        """Toggle game difficulty"""
        modes = ["EASY", "NORMAL", "HARD"]
        idx = modes.index(self.mode)
        self.mode = modes[(idx + 1) % 3]
        self.score_mgr.last_mode = self.mode
        self.score_mgr.save_data()
        self.apply_difficulty()
        self._init_game()
        self.play_sound('swoosh')

    def apply_difficulty(self):
        """Set physics parameters based on difficulty"""
        if self.mode == "EASY":
            self.d_gap = 140
            self.d_speed = 2.5
            self.d_grav = 0.4
            self.d_flap = -6.5
            self.d_spawn = 115
        elif self.mode == "NORMAL":
            self.d_gap = 100
            self.d_speed = 3.0
            self.d_grav = 0.5
            self.d_flap = -7.5
            self.d_spawn = 90
        elif self.mode == "HARD":
            self.d_gap = 85
            self.d_speed = 4.0
            self.d_grav = 0.6
            self.d_flap = -8.0
            self.d_spawn = 65
    
    def _init_game(self):
        # Randomize assets for each new game
        self.bird_color = random.choice(BIRD_COLORS)
        self.pipe_color = random.choice(PIPE_COLORS)
        self.bg_type = random.choice(BACKGROUND_TYPES)
        
        # Reload background and pipe with new colors
        try: 
            self.bg_img = pygame.image.load(f"assets/sprites/background-{self.bg_type}.png").convert()
        except: 
            self.bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)); 
            self.bg_img.fill((112, 197, 206))
        
        try: 
            self.pipe_img = pygame.image.load(f"assets/sprites/pipe-{self.pipe_color}.png").convert_alpha()
        except: 
            self.pipe_img = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT)); 
            self.pipe_img.fill((116, 191, 46))
        
        # Create bird with randomized color
        self.bird_group.empty()
        self.bird_group.add(Bird(SCREEN_WIDTH * 0.3, 240, self.d_grav, self.d_flap, self.bird_color))
        self.pipe_group.empty()
        self.ground_group.empty()
        for i in range(2): 
            self.ground_group.add(Ground(i * GROUND_WIDTH, self.ground_img, self.d_speed))
        
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
            if event.type == pygame.QUIT: 
                self.running = False
            
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
                    if self.btn_pause_rect.collidepoint(event.pos) or self.btn_resume_pause.collidepoint(event.pos):
                        self.state = self.prev_state
                        self.play_sound('swoosh')
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
            for p in dead_pipes: 
                self.pipe_group.remove(p)
            
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
            if self.flash_alpha > 0: 
                self.flash_alpha = max(0, self.flash_alpha - 20)
            if self.shake_frames > 0: 
                self.shake_frames -= 1
    
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
        if self.state == GameState.WELCOME: 
            self._draw_welcome()
        elif self.state == GameState.GET_READY: 
            self._draw_get_ready()
        elif self.state == GameState.PLAYING: 
            self._draw_playing()
        elif self.state == GameState.PAUSED: 
            self._draw_paused()
        elif self.state == GameState.GAME_OVER: 
            self._draw_game_over()
        pygame.display.flip()
    
    def _draw_welcome(self):
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        
        draw_outlined_text(self.screen, "Flappy Bird", self.font_title, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, 120), shadow=True)
        draw_flappy_button(self.screen, self.btn_play_rect, "PLAY", self.font_btn)
        draw_flappy_button(self.screen, self.btn_rank_rect, "SCORE", self.font_btn)
        
        btn_color = MODE_COLORS.get(self.mode, C_ORANGE_BTN)
        draw_flappy_button(self.screen, self.btn_mode_rect, self.mode, self.font_board, color=btn_color)
        
        pygame.draw.circle(self.screen, C_OUTLINE, self.about_btn_rect.center, 15)
        pygame.draw.circle(self.screen, C_ORANGE_BTN, self.about_btn_rect.center, 13)
        draw_outlined_text(self.screen, "?", self.font_board, C_WHITE, C_OUTLINE, self.about_btn_rect.center)
        
        if self.show_about_popup: 
            self._draw_about_popup()
        if self.show_recent_scores: 
            self._draw_recent_scores()

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
        # Background keeps running
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        
        # Draw message image (tap to flap) centered
        if self.message_img:
            msg_rect = self.message_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(self.message_img, msg_rect)
        else:
            draw_outlined_text(self.screen, "Get Ready!", self.font_medium, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, 130), shadow=True)
            tap_y = 300
            pygame.draw.polygon(self.screen, C_WHITE, [(SCREEN_WIDTH//2, tap_y), (SCREEN_WIDTH//2-10, tap_y+15), (SCREEN_WIDTH//2+10, tap_y+15)])
            pygame.draw.polygon(self.screen, C_OUTLINE, [(SCREEN_WIDTH//2, tap_y), (SCREEN_WIDTH//2-10, tap_y+15), (SCREEN_WIDTH//2+10, tap_y+15)], 2)
            draw_outlined_text(self.screen, "TAP TO FLAP", self.font_board, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, tap_y + 35))
        
        # Pause button
        draw_flappy_button(self.screen, self.btn_pause_rect, "II", self.font_board, color=C_BOARD)

    def _draw_playing(self):
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        draw_outlined_text(self.screen, str(self.score_mgr.score), self.font_score, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, 80), shadow=True)
        
        draw_flappy_button(self.screen, self.btn_pause_rect, "II", self.font_board, color=C_BOARD)
    
    def _draw_paused(self):
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)
        self.bird_group.draw(self.screen)
        
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        self.screen.blit(overlay, (0, 0))
        
        draw_outlined_text(self.screen, "PAUSED", self.font_title, C_WHITE, C_OUTLINE, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40), shadow=True)
        
        draw_flappy_button(self.screen, self.btn_resume_pause, "RESUME", self.font_btn, color=(116, 191, 46))
        draw_flappy_button(self.screen, self.btn_menu_pause, "MENU", self.font_btn, color=C_ORANGE_BTN)
    
    def _draw_game_over(self):
        dx, dy = (random.randint(-4, 4), random.randint(-4, 4)) if self.shake_frames > 0 else (0, 0)
        tsurf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        tsurf.blit(self.bg_img, (0, 0))
        self.pipe_group.draw(tsurf)
        self.ground_group.draw(tsurf)
        self.bird_group.draw(tsurf)
        self.screen.blit(tsurf, (dx, dy))
        
        if self.flash_alpha > 0:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, int(self.flash_alpha)))
            self.screen.blit(flash, (0, 0))
        
        if self.bird_group.sprite.rect.bottom >= GROUND_Y:
            self._draw_scoreboard()
    
    def _draw_scoreboard(self):
        # Draw GAMEOVER image
        if self.gameover_img:
            go_rect = self.gameover_img.get_rect(center=(SCREEN_WIDTH // 2, self.scoreboard_y - 40))
            self.screen.blit(self.gameover_img, go_rect)
        else:
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
            draw_flappy_button(self.screen, self.btn_play_rect, "PLAY", self.font_btn)
            draw_flappy_button(self.screen, self.btn_rank_rect, "SCORE", self.font_btn)
            draw_flappy_button(self.screen, self.btn_menu_rect, "MENU", self.font_btn, color=(100, 150, 200))
            
            if self.show_recent_scores: 
                self._draw_recent_scores()

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
