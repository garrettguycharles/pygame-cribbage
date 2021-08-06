import pygame
import os
from nineslice import NineSlice

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'images')
anim_folder = os.path.join(game_folder, 'anim')

display_info = pygame.display.Info()

FULLSCREEN_WIDTH = display_info.current_w
FULLSCREEN_HEIGHT = display_info.current_h

GAME_SCALE = 0.75

WINDOWED_WIDTH = int(display_info.current_w * GAME_SCALE) #1778
WINDOWED_HEIGHT = int(display_info.current_h * GAME_SCALE) #1000

WIDTH = WINDOWED_WIDTH
HEIGHT = WINDOWED_HEIGHT

CARD_WIDTH = int(GAME_SCALE * 64) #48 #96
CARD_HEIGHT = int(GAME_SCALE * 90) #67 #135
FONT_SIZE = int(GAME_SCALE * 20)
FPS = 30
CLICK_DELAY = int(FPS / 3.0)
padding = int(GAME_SCALE * 10) # 5



PLAY_WIDTH = WIDTH - ((padding * 3) * 12 + padding * 4)
TABLE_WIDTH = HEIGHT
TABLE_MARGIN = (PLAY_WIDTH - TABLE_WIDTH) / 2
TABLE_RECT = pygame.rect.Rect(TABLE_MARGIN + padding, padding, TABLE_WIDTH - padding * 2, HEIGHT - padding * 2)
TABLE_RECT.topleft = (TABLE_MARGIN + padding, padding)

fast_forward = False

BLACK = (15, 15, 15)
WHITE = (240, 240, 240)
GREEN = (0, 74, 20)
TURN_COLOR = (0, 46, 12)

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
screen.fill(BLACK)
display_icon = pygame.image.load(os.path.join(img_folder, "spr_spade.png"))
display_icon = pygame.transform.smoothscale(display_icon, (32,32))
display_icon.set_colorkey((0, 0, 0))
pygame.display.set_icon(display_icon)
pygame.display.set_caption("Cribbage")
clock = pygame.time.Clock()
screen_message = "Welcome to Cribbage!"

all_card_collections = []
all_visual_fx = []
all_ui_elements = []

game = None
running = True
num_players_in_game = 4
room = "start_screen"