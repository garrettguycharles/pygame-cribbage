import pygame
import globals
from utils import *
from nineslice import NineSlice

class Button(pygame.sprite.Sprite):
    font = pygame.font.SysFont("arial", globals.FONT_SIZE, bold=True)
    width = 64
    height = 64

    @staticmethod
    def default_on_click():
        print("button default on_click triggered")

    def __init__(self, image="", pressed_image = "", text="", on_click = default_on_click, args = [], center=(0, 0), is_toggle=False, dimensions = None):
        pygame.sprite.Sprite.__init__(self)
        globals.all_ui_elements.append(self)
        self.image_name = image
        self.pressed_image_name = pressed_image
        self.width = int(Button.width * globals.GAME_SCALE)
        self.height = int(Button.height * globals.GAME_SCALE)
        if len(self.image_name) > 0:
            self.base_image = load_image(self.image_name)
            if dimensions is None:
                self.width = self.base_image.get_width()
                self.height = self.base_image.get_height()
            else:
                dimensions = scale_coord_to_int(dimensions, globals.GAME_SCALE)
                self.width = dimensions[0]
                self.height = dimensions[1]
                self.base_image = pygame.transform.smoothscale(self.base_image, (self.width, self.height))

            if len(self.pressed_image_name) > 0:
                self.pressed_image = load_image(self.pressed_image_name)
                self.pressed_image = pygame.transform.smoothscale(self.pressed_image, (self.width, self.height))
            else:
                self.pressed_image = self.base_image

        self.text = text
        if len(self.text) < 1 and len(self.image_name) < 1:
            self.text = "default_button_text"

        if len(self.text) > 0:
            self.text_render = Button.font.render(self.text, True, globals.WHITE)
            self.text_render_rect = self.text_render.get_rect()
            self.width = max(self.width, self.text_render.get_width() + 2 * globals.padding)
            self.height = max(self.height, self.text_render.get_height() + 2 * globals.padding)

            if len(self.image_name) < 1:
                self.base_image = load_image("spr_button.png")
                self.base_image = NineSlice.get_nine(self.base_image, (16, 16, 16, 16), self.width, self.height)
                self.pressed_image = load_image("spr_button_pressed.png")
                self.pressed_image = NineSlice.get_nine(self.pressed_image, (16, 16, 16, 16), self.width, self.height)
            self.image = self.base_image
            self.rect = self.image.get_rect()
            self.text_render_rect.center = self.rect.center
            self.base_image.blit(self.text_render, self.text_render_rect)
            self.pressed_image.blit(self.text_render, self.text_render_rect)
            self.base_image.set_colorkey((0, 0, 0))
            self.pressed_image.set_colorkey((0, 0, 0))
            self.image = self.base_image
        else:
            self.image = self.base_image
            self.rect = self.image.get_rect()
        self.rect.center = center

        self.on_click = on_click
        self.args = args

        self.toggle = False
        self.is_toggle = is_toggle

        self.alpha = 0xff

    def end(self):
        globals.all_ui_elements.remove(self)

    def set_position(self, pos):
        self.rect.center = pos

    def draw(self):
        if self.is_toggle and self.toggle:
            toggle_surface = pygame.surface.Surface((self.rect.width + globals.padding, self.rect.height + globals.padding))
            toggle_surface_rect = toggle_surface.get_rect()
            pygame.draw.rect(toggle_surface, globals.WHITE, toggle_surface_rect, 0, globals.padding)
            toggle_surface_rect.center = self.rect.center
            toggle_surface.set_colorkey((0, 0, 0))
            toggle_surface.set_alpha(float_to_alpha(0.5))
            globals.screen.blit(toggle_surface, toggle_surface_rect)

        globals.screen.blit(self.image, self.rect)

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if not self.rect.collidepoint(*mouse_pos):
            self.image = self.base_image

    def on_mouse_down(self, pos, button):
        if self.rect.collidepoint(pos) and button == 1:
            self.image = self.pressed_image
            return True
        return False

    def on_mouse_up(self, pos, button):
        if self.rect.collidepoint(pos) and button == 1:
            self.image = self.base_image
            if self.is_toggle:
                self.toggle = not self.toggle
                self.on_click(self.toggle)
            else:
                self.on_click(*self.args)
                self.image = self.base_image
            return True
        return False


