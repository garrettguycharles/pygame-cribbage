import pygame
from globals import *
from utils import *
from nineslice import NineSlice

class FloatingMessage(pygame.sprite.Sprite):
    font_size = FONT_SIZE * 2
    font = pygame.font.SysFont("arial", font_size, bold=True)

    def __init__(self, message, start_pos, dest_pos, font_size=None, in_motion_message=None, color=None, max_scale = 1, execute_on_arrival=None, execute_args = [], await_animation=True, anim_delay=1.0, fade_in = True, fade_out = True, transition_duration = 0.15):
        pygame.sprite.Sprite.__init__(self)
        self.font_size = font_size
        if self.font_size == None:
            self.font_size = FloatingMessage.font_size
        self.font = FloatingMessage.font
        all_visual_fx.append(self)
        self.start_pos = start_pos
        self.await_animation = await_animation
        self.message = message
        self.in_motion_message = in_motion_message
        if (self.in_motion_message == None):
            self.in_motion_message = self.message
        self.execute_on_arrival = execute_on_arrival
        self.transition_duration = 1 + FPS * transition_duration
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.fade_out_timer = self.transition_duration
        self.anim_delay = FPS * anim_delay
        self.base_anim_delay = self.anim_delay
        self.move_fraction = 0.01
        self.color = color
        self.alpha = 1
        self.execute_args = execute_args
        self.set_image_with_message(self.message)
        self.move_to_target = True
        self.target_position = dest_pos
        self.base_target_distance = 1 + get_distance(start_pos, dest_pos)
        self.scale = 1
        self.max_scale = max_scale

    def set_image_with_message(self, message):
        if self.color == None:
            self.text_render = self.font.render(message, True, BLACK)
            ratio = self.font_size / FloatingMessage.font_size
            new_text_dims = scale_coord((self.text_render.get_width(), self.text_render.get_height()), ratio)
            self.text_render = pygame.transform.smoothscale(self.text_render,
                                                            (int(new_text_dims[0]), int(new_text_dims[1])))
            self.base_image = pygame.image.load(os.path.join(img_folder, "spr_card.png"))
            self.base_image = NineSlice.get_nine(self.base_image, (8, 8, 8, 8),
                                                 self.text_render.get_width() + (padding * 2),
                                                 self.text_render.get_height() + padding * 2)
        else:
            self.text_render = self.font.render(message, True, WHITE)
            ratio = self.font_size / FloatingMessage.font_size
            new_text_dims = scale_coord((self.text_render.get_width(), self.text_render.get_height()), ratio)
            self.text_render = pygame.transform.smoothscale(self.text_render,
                                                            (int(new_text_dims[0]), int(new_text_dims[1])))
            circle_diameter = (self.text_render.get_height() + padding)
            circle_radius = circle_diameter / 2
            base_w = max(circle_diameter, self.text_render.get_width() + circle_diameter)
            base_h = circle_diameter
            self.base_image = pygame.surface.Surface((int(base_w), int(base_h)))
            pygame.draw.rect(self.base_image, get_color_from_name(self.color), self.base_image.get_rect(), 0, int(circle_radius))
        text_rect = self.text_render.get_rect()
        base_rect = self.base_image.get_rect()
        text_rect.center = base_rect.center
        self.base_image.blit(self.text_render, text_rect)
        self.base_image.set_colorkey((0, 0, 0))
        self.base_width = self.base_image.get_width()
        self.base_height = self.base_image.get_height()
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.rect.center = self.start_pos

    def update(self):

        if self.anim_delay > 0:
            self.anim_delay -= 1
            self.scale = (min((self.base_anim_delay - self.anim_delay), self.transition_duration) / self.transition_duration)
            if self.fade_in:
                self.alpha = float_to_alpha(self.scale)
        elif self.anim_delay == 0:
            self.set_image_with_message(self.in_motion_message)
            self.anim_delay = -1
        else:
            self.move_towards_target()
            self.move_fraction += 0.005
            self.scale = 1 + (self.max_scale - 1) * round(get_distance(self.rect.center, self.target_position) / self.base_target_distance, 2)
            self.alpha = float_to_alpha(self.fade_out_timer / self.transition_duration)
        self.image = pygame.transform.smoothscale(self.base_image, (int(self.base_width * self.scale), int(self.base_height * self.scale)))
        self.image.set_alpha(self.alpha)
        temp = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = temp
        if not self.move_to_target:
            self.fade_out_timer -= 1
            if self.fade_out_timer < 1:
                if self.execute_on_arrival != None:
                    self.execute_on_arrival(*self.execute_args)
                all_visual_fx.remove(self)
        else:
            self.fade_out_timer = self.transition_duration + 1


    def draw(self):
        screen.blit(self.image, get_rect_kept_on_screen(self.rect))

    def move_towards_target(self):
        move_x = (self.target_position[0] - self.rect.centerx) * self.move_fraction
        move_y = (self.target_position[1] - self.rect.centery) * self.move_fraction
        if (abs(self.rect.centerx - self.target_position[0]) == 0) and (abs(self.rect.centery - self.target_position[1]) > 0):
            self.rect.centery += get_sign(move_y) * max(abs(move_y), 1)
        elif (abs(self.rect.centerx - self.target_position[0]) > 0) and (abs(self.rect.centery - self.target_position[1]) == 0):
            self.rect.centerx += get_sign(move_x) * max(abs(move_x), 1)
        else:
            self.rect.centerx += get_sign(move_x) * max(abs(move_x), 1)
            self.rect.centery += get_sign(move_y) * max(abs(move_y), 1)
        if (abs(self.rect.centerx - self.target_position[0]) < 2 and abs(self.rect.centery - self.target_position[1]) < 2):
            self.rect.center = self.target_position
            self.move_to_target = False

    def is_moving(self):
        if self.await_animation:
            return self.move_to_target
        return False





