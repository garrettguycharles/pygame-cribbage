import pygame
import globals
from utils import *
from nineslice import NineSlice

class PegSprite(pygame.sprite.Sprite):
    font = pygame.font.SysFont("arial", globals.FONT_SIZE * 4, bold=True)
    def __init__(self, pegboard, track = 0):
        pygame.sprite.Sprite.__init__(self)

        self.track = track

        self.color = "red"
        if self.track == 0:
            self.color = "red"

        if self.track == 1:
            self.color = "green"

        if self.track == 2:
            self.color = "blue"

        if self.track == 3:
            self.color = "tan"


        self.pegboard = pegboard

        self.score = 0

        self.score_draw_timer = -1

        self.build_images()

        self.image = self.full_peg_image
        self.rect = self.image.get_rect()
        self.move_to_target = False
        self.target_position = (0, 0)
        self.hover = False
        self.is_front = False

    def build_images(self):
        self.full_peg_image = load_image("spr_peg_" + self.color + ".png")
        self.half_peg_image = load_image("spr_peg_" + self.color + "_pegged.png")
        self.scale = 1.0 * globals.GAME_SCALE
        self.full_peg_image = pygame.transform.smoothscale(self.full_peg_image, scale_coord_to_int(
            (self.full_peg_image.get_width(), self.full_peg_image.get_height()), self.scale))
        self.half_peg_image = pygame.transform.smoothscale(self.half_peg_image, scale_coord_to_int(
            (self.half_peg_image.get_width(), self.half_peg_image.get_height()), self.scale))
        self.full_peg_image.set_colorkey((0, 0, 0))
        self.half_peg_image.set_colorkey((0, 0, 0))

    def on_window_rebuild(self):
        self.build_images()


    def set_move_target(self, _x, _y):
        self.move_to_target = True
        self.target_position = (_x, _y)
        temp = self.rect.midbottom
        self.image = self.full_peg_image
        self.rect = self.full_peg_image.get_rect()
        self.rect.midbottom = temp

    def set_score(self, score):
        self.score = score

        if self.score > 120:
            self.set_move_target(*get_absolute_coords(self.pegboard.winning_peghole_position, self.pegboard.rect))
        else:
            self.set_move_target(*get_absolute_coords(self.pegboard.peghole_positions[self.track][self.score], self.pegboard.rect))

    def set_position(self, new_pos):
        self.rect.midbottom = new_pos

    def get_position(self):
        return self.rect.center

    def is_moving(self):
        return self.move_to_target

    def update(self):
        if self.move_to_target:
            self.move_towards_target()
        mouse_pos = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse_pos)


    def draw(self):
        if self.is_moving():
            self.score_draw_timer = globals.FPS * 2

        if self.is_front:
            if self.hover:
                self.score_draw_timer = int(globals.FPS / 4) + 1
        else:
            self.score_draw_timer = -1

        if self.score_draw_timer >= 0:
            # TODO turn this into an fx message bubble
            self.score_draw_timer -= 1
            score_render = PegSprite.font.render(str(max(0, self.score)), True, globals.WHITE)
            score_render.set_colorkey((0, 0, 0))
            circle_diam = max(score_render.get_height() + globals.padding, score_render.get_width() + globals.padding)
            to_draw = pygame.surface.Surface((circle_diam, circle_diam))
            pygame.draw.circle(to_draw, get_color_from_name(self.color), to_draw.get_rect().center, min(to_draw.get_width(), to_draw.get_height()) / 2.0, 0)
            to_draw.set_colorkey((0, 0, 0))
            score_rect = score_render.get_rect()
            score_rect.center = (to_draw.get_width() / 2, to_draw.get_height() / 2)
            to_draw.blit(score_render, score_rect)
            dest_rect = to_draw.get_rect()
            dest_rect.midright = self.rect.midtop
            to_draw.set_alpha(int(0xff * self.score_draw_timer * 4 / globals.FPS))
            globals.screen.blit(to_draw, get_rect_kept_on_screen(dest_rect))
        globals.screen.blit(self.image, self.rect)

    def move_towards_target(self):
        move_x = (self.target_position[0] - self.rect.centerx) * 0.1
        move_y = (self.target_position[1] - self.rect.bottom) * 0.1
        if (abs(self.rect.centerx - self.target_position[0]) == 0) and (abs(self.rect.bottom - self.target_position[1]) > 0):
            self.rect.y += get_sign(move_y) * max(abs(move_y), 1)
        elif (abs(self.rect.centerx - self.target_position[0]) > 0) and (abs(self.rect.bottom - self.target_position[1]) == 0):
            self.rect.x += get_sign(move_x) * max(abs(move_x), 1)
        else:
            self.rect.x += get_sign(move_x) * max(abs(move_x), 1)
            self.rect.y += get_sign(move_y) * max(abs(move_y), 1)
        if (abs(self.rect.centerx - self.target_position[0]) < 2 and abs(self.rect.bottom - self.target_position[1]) < 2):
            self.rect.midbottom = self.target_position
            temp = self.rect.midbottom
            self.image = self.half_peg_image
            self.rect = self.half_peg_image.get_rect()
            self.rect.midbottom = temp
            self.move_to_target = False

    def set_is_front(self, is_front):
        self.is_front = is_front


class PegPair:
    def __init__(self, pegboard, track=0):
        self.track=track
        self.pegboard = pegboard
        self.back = PegSprite(pegboard, track)
        self.front = PegSprite(pegboard, track)
        self.color = self.back.color
        self.back.set_score(-1)
        self.front.set_score(-0)
        self.front.set_is_front(True)

        self.back.set_position(self.back.target_position)
        self.front.set_position(self.front.target_position)

    def on_window_rebuild(self):
        self.back.on_window_rebuild()
        self.front.on_window_rebuild()
        self.back.set_score(self.back.score)
        self.front.set_score(self.front.score)
        self.back.set_position(self.back.target_position)
        self.front.set_position(self.front.target_position)

    def draw(self):
        if self.front.score > 40 and self.front.score <= 83:
            self.back.draw()
            self.front.draw()
        else:
            self.front.draw()
            self.back.draw()



    def update(self):
        self.front.update()
        self.back.update()

    def set_score(self, score):
        if score == self.front.score:
            return
        self.back.set_score(score)
        temp = self.front
        self.front = self.back
        self.back = temp

        self.front.set_is_front(True)
        self.back.set_is_front(False)

    def is_moving(self):
        return self.back.is_moving() or self.front.is_moving()



class PegBoardSprite(pygame.sprite.Sprite):

    def __init__(self, num_lanes = 3):
        pygame.sprite.Sprite.__init__(self)
        self.num_lanes = num_lanes
        self.build_pegboard_image()
        '''
        self.image = pygame.image.load(os.path.join(img_folder, "spr_peg_board.png"))
        self.peghole_image = pygame.image.load(os.path.join(img_folder, "spr_peg_hole.png"))
        self.slices = (12, 20, 12, 28)
        self.image = NineSlice.get_nine(self.image, self.slices, self.image.get_width(), HEIGHT - 3 * globals.padding, stretch=True)
        self.track_height = self.image.get_height() - (self.slices[1] + self.slices[3])
        self.track_width = self.image.get_width() - (self.slices[0] + self.slices[2])
        self.peghole_height = int((self.track_height - (120 + globals.padding)) / 120)
        self.peghole_image = pygame.transform.smoothscale(self.peghole_image, (self.peghole_image.get_width(), self.peghole_height))
        self.rect = self.image.get_rect()
        self.peghole_rect = self.peghole_image.get_rect()
        self.finish_hole_position = (48, 10)
        for i in range(120):
            self.peghole_rect.center = (20, self.rect.height - (self.slices[3] + globals.padding + ((self.track_height - globals.padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        for i in range(120):
            self.peghole_rect.center = (39, self.rect.height - (self.slices[3] + globals.padding + ((self.track_height - globals.padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        for i in range(120):
            self.peghole_rect.center = (57, self.rect.height - (self.slices[3] + globals.padding + ((self.track_height - globals.padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        for i in range(120):
            self.peghole_rect.center = (76, self.rect.height - (self.slices[3] + globals.padding + ((self.track_height - globals.padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        '''

        self.peg_pairs = [PegPair(self, i) for i in range(self.num_lanes)]

    def build_pegboard_image(self):
        self.peghole_positions = [{} for i in range(self.num_lanes)]

        self.image = load_image("spr_peg_board.png")
        self.peghole_image = load_image("spr_peg_hole.png")
        self.peghole_image = pygame.transform.smoothscale(self.peghole_image, scale_coord_to_int(self.peghole_image.get_size(), globals.GAME_SCALE))
        self.slices = (12, 12, 12, 12)
        #
        self.track_height = globals.HEIGHT
        self.peghole_height = self.peghole_image.get_height()
        #
        self.lane_width = globals.padding * 3
        self.board_width = self.lane_width * self.num_lanes * 3 + globals.padding * 4 + self.slices[0] + self.slices[2]
        self.turn_height = self.board_width / 2
        self.minor_turn_height = self.lane_width * self.num_lanes + globals.padding / 2
        self.track_width = self.lane_width * self.num_lanes * 3 + globals.padding * 2
        self.straightaway_length = 35
        self.board_height = globals.HEIGHT - 2 * globals.padding
        self.straightaway_height = self.board_height - (2 * self.turn_height + self.slices[1] + self.slices[3])
        self.straightaway_spacing = (self.straightaway_height) / self.straightaway_length
        self.image = NineSlice.get_nine(self.image, self.slices, self.board_width, self.board_height)
        self.track_colors = [(0xb7, 0x62, 0x51), (0x4a, 0x70, 0x4a), (0x53, 0x66, 0x87), (0x7c, 0x70, 0x42)]
        self.rect = self.image.get_rect()
        self.top_turn_pivot = (self.board_width / 2, self.slices[1] + self.turn_height)
        self.bottom_turn_pivot = (self.board_width - (self.slices[2] + globals.padding * 3/2 + self.lane_width * self.num_lanes), self.board_height - (self.turn_height + self.slices[3]))
        self.winning_peghole_position = add_coords(self.top_turn_pivot, (0, -globals.padding))


        xoffset = globals.padding + self.slices[0]

        for i in range(self.num_lanes):
            to_draw_rect = (xoffset + i * self.lane_width, self.turn_height + self.slices[1] + self.straightaway_height + globals.padding, self.lane_width, self.lane_width * self.num_lanes - globals.padding / 2)
            pygame.draw.rect(self.image, self.track_colors[i], to_draw_rect, 0)

        for i in range(self.num_lanes):
            to_draw_rect = (xoffset + i * self.lane_width, self.turn_height + self.slices[1], self.lane_width, self.straightaway_height)
            pygame.draw.rect(self.image, self.track_colors[i], to_draw_rect, 0)

        xoffset += self.lane_width * self.num_lanes + globals.padding

        for i in range(self.num_lanes):
            to_draw_rect = (xoffset + i * self.lane_width, self.turn_height + self.slices[1], self.lane_width, self.straightaway_height)
            pygame.draw.rect(self.image, self.track_colors[i], to_draw_rect, 0)

        xoffset += self.lane_width * self.num_lanes + globals.padding

        for i in reversed(range(self.num_lanes)):
            to_draw_rect = (xoffset + i * self.lane_width, self.turn_height + self.slices[1], self.lane_width, self.straightaway_height)
            pygame.draw.rect(self.image, self.track_colors[self.num_lanes - i - 1], to_draw_rect, 0)

        for i in range(self.num_lanes):
            pygame.draw.circle(self.image, self.track_colors[i], self.top_turn_pivot, self.track_width / 2 - i * self.lane_width, self.lane_width, draw_top_left=True, draw_top_right=True, draw_bottom_left=False, draw_bottom_right=False)

        for i in range(self.num_lanes):
            pygame.draw.circle(self.image, self.track_colors[i], self.bottom_turn_pivot, (self.lane_width * self.num_lanes * 2 + globals.padding) / 2 - i * self.lane_width, self.lane_width, draw_top_left=False, draw_top_right=False, draw_bottom_left=True, draw_bottom_right=True)

        self.peghole_rect = self.peghole_image.get_rect()
        self.peghole_rect.midbottom = self.winning_peghole_position
        self.image.blit(self.peghole_image, self.peghole_rect)

        self.start_spacing = (self.minor_turn_height - globals.padding) / 3

        # Draw pegholes onto the board
        for j in range(self.num_lanes):

            for i in range(3):
                self.peghole_rect.center = ((self.slices[0] + globals.padding + self.lane_width * (1 + 2 * j) / 2), self.bottom_turn_pivot[1] + (self.lane_width * self.num_lanes + globals.padding / 2) - (self.start_spacing * (1 + 2 * i) / 2))
                self.image.blit(self.peghole_image, self.peghole_rect)
                self.peghole_positions[j][-2 + i] = self.peghole_rect.midbottom

            for i in range(self.straightaway_length):
                self.peghole_rect.center = (self.slices[0] + globals.padding + self.lane_width * (1 + 2 * j) / 2, self.board_height - (self.slices[3] + self.turn_height + globals.padding + i * self.straightaway_spacing))
                self.image.blit(self.peghole_image, self.peghole_rect)
                self.peghole_positions[j][1 + i] = self.peghole_rect.midbottom

            for i in range(10):
                self.peghole_rect.center = add_coords(self.top_turn_pivot, distance_in_direction(261 - i * 18, self.track_width / 2 - self.lane_width * (1 + 2 * j) / 2))
                self.image.blit(self.peghole_image, self.peghole_rect)
                self.peghole_positions[j][self.straightaway_length + 1 + i] = self.peghole_rect.midbottom

            for i in range(self.straightaway_length):
                self.peghole_rect.center = (self.board_width - self.slices[2] - globals.padding - self.lane_width * (1 + 2 * j) / 2, self.slices[1] + self.turn_height + i * self.straightaway_spacing + globals.padding)
                self.image.blit(self.peghole_image, self.peghole_rect)
                self.peghole_positions[j][10 + self.straightaway_length + 1 + i] = self.peghole_rect.midbottom

            for i in range(5):
                self.peghole_rect.center = add_coords(self.bottom_turn_pivot, distance_in_direction(72 - i * 36, (self.lane_width * self.num_lanes + globals.padding / 2 - self.lane_width * (1 + 2 * j) / 2)))
                self.image.blit(self.peghole_image, self.peghole_rect)
                self.peghole_positions[j][10 + self.straightaway_length * 2 + 1 + i] = self.peghole_rect.midbottom

            for i in range(self.straightaway_length):
                self.peghole_rect.center = (self.slices[0] + self.lane_width * self.num_lanes + 2 * globals.padding + self.lane_width * (1 + 2 * j) / 2, self.board_height - (self.slices[3] + self.turn_height + i * self.straightaway_spacing + globals.padding))
                self.image.blit(self.peghole_image, self.peghole_rect)
                self.peghole_positions[j][5 + 10 + self.straightaway_length * 2 + 1 + i] = self.peghole_rect.midbottom

        self.image.set_colorkey((0, 0, 0))
        self.rect.right = globals.WIDTH - globals.padding
        self.rect.bottom = globals.HEIGHT - globals.padding

    def on_window_rebuild(self):
        self.build_pegboard_image()
        for peg_pair in self.peg_pairs:
            peg_pair.on_window_rebuild()

    def pegs_are_moving(self):
        for pegpair in self.peg_pairs:
            if pegpair.is_moving():
                return True
        return False

    def update(self):
        for peg_pair in self.peg_pairs:
            peg_pair.update()

    def draw(self):
        globals.screen.blit(self.image, self.rect)
        for peg_pair in self.peg_pairs:
            peg_pair.draw()