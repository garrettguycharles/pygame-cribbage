import pygame
import globals
from utils import *
from nineslice import NineSlice

class FloatingMessage(pygame.sprite.Sprite):
    font_size = globals.FONT_SIZE * 2
    font = pygame.font.SysFont("arial", font_size, bold=True)

    def __init__(self, message, start_pos, dest_pos, font_size=None, in_motion_message=None, color=None, end_scale = 1, execute_on_arrival=None, execute_args = [], await_animation=True, anim_delay=1.0, fade_in = True, fade_out = True, transition_duration = 0.15, fade_in_delay = 0):
        pygame.sprite.Sprite.__init__(self)
        self.font_size = font_size
        self.fade_in_delay = int(fade_in_delay * globals.FPS)
        if self.font_size == None:
            self.font_size = FloatingMessage.font_size
        self.font = FloatingMessage.font
        globals.all_visual_fx.append(self)
        self.start_pos = start_pos
        self.await_animation = await_animation
        self.message = message
        self.in_motion_message = in_motion_message
        if (self.in_motion_message == None):
            self.in_motion_message = self.message
        self.execute_on_arrival = execute_on_arrival
        self.transition_duration = 1 + globals.FPS * transition_duration
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.fade_out_timer = self.transition_duration
        self.anim_delay = globals.FPS * anim_delay
        self.base_anim_delay = self.anim_delay
        self.move_fraction = 0.01
        self.color = color
        self.alpha = 0
        self.execute_args = execute_args
        self.set_image_with_message(self.message)
        self.move_to_target = True
        self.target_position = dest_pos
        self.base_target_distance = 1 + get_distance(start_pos, dest_pos)
        self.scale = 1
        self.end_scale = end_scale

    def set_image_with_message(self, message):
        if self.color == None:
            self.text_render = self.font.render(message, True, globals.BLACK)
            ratio = self.font_size / FloatingMessage.font_size
            new_text_dims = scale_coord((self.text_render.get_width(), self.text_render.get_height()), ratio)
            self.text_render = pygame.transform.smoothscale(self.text_render,
                                                            (int(new_text_dims[0]), int(new_text_dims[1])))
            self.base_image = pygame.image.load(os.path.join(globals.img_folder, "spr_card.png"))
            self.base_image = NineSlice.get_nine(self.base_image, (8, 8, 8, 8),
                                                 self.text_render.get_width() + (globals.padding * 2),
                                                 self.text_render.get_height() + globals.padding * 2)
        else:
            self.text_render = self.font.render(message, True, globals.WHITE)
            ratio = self.font_size / FloatingMessage.font_size
            new_text_dims = scale_coord((self.text_render.get_width(), self.text_render.get_height()), ratio)
            self.text_render = pygame.transform.smoothscale(self.text_render,
                                                            (int(new_text_dims[0]), int(new_text_dims[1])))
            circle_diameter = (self.text_render.get_height() + globals.padding)
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

        if self.fade_in_delay > 0:
            self.fade_in_delay -= 1
            return

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
            lerp_val = 1 - round(get_distance(self.rect.center, self.target_position) / self.base_target_distance, 2)
            self.scale = lerp(1, self.end_scale, lerp_val)
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
                globals.all_visual_fx.remove(self)
        else:
            self.fade_out_timer = self.transition_duration + 1


    def draw(self):
        globals.screen.blit(self.image, get_rect_kept_on_screen(self.rect))

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
            self.move_fraction = 0.005
            self.move_to_target = False

    def is_moving(self):
        if self.await_animation:
            return self.move_to_target
        return False


class AnimatedIcon(pygame.sprite.Sprite):
    font = pygame.font.SysFont("arial", globals.FONT_SIZE, bold=True)
    def __init__(self, name = "scissors", message="", angle=0, loop_repeat=2, pause_duration = 4, transition_duration = 0.5, center = (globals.WIDTH / 2, globals.HEIGHT / 2), height = 128, point_towards = None, osc_radius = (0, 0), fps=24):
        pygame.sprite.Sprite.__init__(self)
        globals.all_visual_fx.append(self)
        self.name = name
        self.images = load_anim(name)
        self.message = message
        self.image_index = 0
        self.loop_repeat = loop_repeat
        self.pause_duration = pause_duration
        self.point_towards = point_towards
        self.image = self.images[self.image_index]
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.osc_radius = osc_radius
        self.osc_origin = self.rect.center
        self.osc_timer = 0
        self.transition_duration = globals.FPS * transition_duration
        self.anim_FPS = fps
        self.base_frame_delay = globals.FPS / self.anim_FPS
        self.state_timer = len(self.images) * self.loop_repeat - 1
        self.state_lengths = {"loop": len(self.images) * self.loop_repeat - 1, "pause": globals.FPS * self.pause_duration}
        self.state = "loop"
        self.frame_delay = -1
        self.start_alpha = 0x00
        self.alpha = 0x00
        self.target_alpha = 0xff
        self.start_angle = 0
        self.angle = 0
        self.target_angle = angle
        self.scale = globals.GAME_SCALE * height / self.images[0].get_height()
        self.start_pos = self.rect.center
        self.target_position = self.rect.center
        self.base_target_distance = 0
        self.move_to_target = False
        self.move_speed = 1 / globals.FPS
        self.target_progress = 0
        for i in range(len(self.images)):
            image = self.images[i]
            self.images[i] = pygame.transform.smoothscale(image, scale_coord_to_int((image.get_width(), image.get_height()), self.scale))
        self.is_end = False

    def tick_fps(self):
        self.frame_delay -= 1
        if self.frame_delay < 1:
            self.frame_delay = self.base_frame_delay
            return True
        return False

    def set_position(self, pos):
        self.osc_origin = pos

    def set_target_position(self, targ_pos):
        self.move_to_target = True
        self.start_pos = self.osc_origin
        self.target_position = targ_pos
        self.base_target_distance = get_distance(self.start_pos, self.target_position)
        self.target_progress = 0

    def set_loop_repeat(self, num):
        self.loop_repeat = num
        self.state_lengths["loop"] = len(self.images) * self.loop_repeat - 1

    def set_pause_duration(self, num):
        self.pause_duration = num
        self.state_lengths["pause"] = globals.FPS * self.pause_duration

    def next_frame(self):
        if self.state == "loop":

            if self.tick_fps():
                self.image_index = (self.image_index + 1) % len(self.images)
                self.state_timer -= 1
                if self.state_timer < 0:
                    self.state_timer = self.state_lengths["pause"]
                    self.state = "pause"
                    return

        if self.state == "pause":
            if self.tick_fps():
                self.state_timer = max(self.state_timer - 1, -1)
                if self.state_timer < 0 and self.loop_repeat > 0:
                    self.state_timer = self.state_lengths["loop"]
                    self.state = "loop"
                    return

    def draw(self):
        if len(self.message) > 0:
            text = AnimatedIcon.font.render(self.message, True, globals.WHITE)
            text.set_colorkey((0, 0, 0))
            text_rect = text.get_rect()
            text_base = pygame.surface.Surface((text.get_width() + globals.padding * 4, text.get_height() + globals.padding * 4))
            text_base_rect = text_base.get_rect()
            pygame.draw.rect(text_base, globals.BLACK, text_base_rect, 0, text_base_rect.height)
            text_base.set_colorkey((0, 0, 0))

            text_rect.center = text_base_rect.center
            text_base.blit(text, text_rect)
            text_base_rect.bottomright = self.rect.center
            draw_transformed(text_base, text_base_rect, alpha=self.alpha)

        draw_transformed(self.image, self.rect, angle=self.angle, alpha=self.alpha)


    def oscillate(self):
        self.osc_timer += 1
        if self.osc_timer > 360:
            self.osc_timer = 1
        self.rect.centerx = self.osc_origin[0] + math.cos(math.radians(self.osc_timer)) * self.osc_radius[0]
        self.rect.centery = self.osc_origin[1] + math.sin(math.radians(self.osc_timer)) * self.osc_radius[1]

    def update(self):
        self.next_frame()
        self.oscillate()
        temp = self.rect.center
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect()
        self.rect.center = temp
        self.image.set_colorkey((0, 0, 0))

        if self.move_to_target:
            self.target_progress += self.move_speed
            move_frac = cos_interp(0, 1, self.target_progress)
            self.set_position(move_step(self.base_target_distance * move_frac, self.start_pos, self.target_position))
            if self.target_progress >= 1:
                self.move_to_target = False
                self.set_position(self.target_position)

        if self.point_towards != None:
            self.target_angle = get_angle_between_points(self.rect.center, self.point_towards)

        if self.angle != self.target_angle:
            self.angle += (self.target_angle - self.angle) * 0.3
            if abs(self.target_angle - self.angle) < 3:
                self.angle = self.target_angle

        if self.alpha != self.target_alpha:
            self.alpha += (self.target_alpha - self.start_alpha) * (1 / self.transition_duration)
            if abs(self.target_alpha - self.alpha) < 3:
                self.alpha = self.target_alpha
                if self.is_end:
                    globals.all_visual_fx.remove(self)


    def is_moving(self):
        return False

    def end(self):
        self.target_alpha = 0
        self.start_alpha = self.alpha
        self.is_end = True


