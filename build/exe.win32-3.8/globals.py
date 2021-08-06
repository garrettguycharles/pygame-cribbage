import pygame
import os

game_folder = os.path.dirname(__file__)
img_folder = os.path.join(game_folder, 'images')

info = pygame.display.Info()

WIDTH = info.current_w #1778
HEIGHT = info.current_h #1000

CARD_WIDTH = 64 #48 #96
CARD_HEIGHT = 90 #67 #135
FONT_SIZE = 20
FPS = 30
CLICK_DELAY = int(FPS / 3.0)
padding = 10 # 5

PLAY_WIDTH = WIDTH - (128 + padding * 2)

BLACK = (15, 15, 15)
WHITE = (240, 240, 240)
GREEN = (0, 74, 20)
TURN_COLOR = (0, 46, 12)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
screen.fill(GREEN)
display_icon = pygame.image.load(os.path.join(img_folder, "spr_spade.png"))
display_icon = pygame.transform.smoothscale(display_icon, (32,32))
display_icon.set_colorkey((0, 0, 0))
pygame.display.set_icon(display_icon)
pygame.display.set_caption("Cribbage")
clock = pygame.time.Clock()
screen_message = "Welcome to Cribbage!"

all_card_collections = []
all_visual_fx = []

game = None
running = True