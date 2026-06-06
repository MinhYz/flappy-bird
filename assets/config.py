# ============================================================================
# CONFIG & CONSTANTS
# ============================================================================
from enum import Enum

# Screen & Game
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60

# Bird & Pipe
BIRD_WIDTH, BIRD_HEIGHT = 34, 24
PIPE_WIDTH, PIPE_HEIGHT = 52, 320

# Ground
GROUND_WIDTH, GROUND_HEIGHT = 336, 112
GROUND_Y = SCREEN_HEIGHT - GROUND_HEIGHT

# --- COLORS ---
C_OUTLINE = (84, 56, 71)      # Dark outline
C_WHITE = (255, 255, 255)     # White
C_ORANGE_BTN = (232, 97, 1)   # Orange button
C_BOARD = (222, 216, 149)     # Board yellow
C_TEXT_ORANGE = (244, 150, 30) # Text orange

# Mode colors
MODE_COLORS = {
    "EASY": (116, 191, 46),   # Green
    "NORMAL": (232, 97, 1),   # Orange
    "HARD": (220, 50, 50)     # Red
}

# Game states
class GameState(Enum):
    WELCOME = 0
    GET_READY = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

# Birds and Pipes
BIRD_COLORS = ["yellow", "blue", "red"]
PIPE_COLORS = ["green", "red"]
BACKGROUND_TYPES = ["day", "night"]
