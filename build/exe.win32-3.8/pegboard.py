import pygame
from globals import *
from utils import *
from nineslice import NineSlice

class PegSprite(pygame.sprite.Sprite):
    font = pygame.font.SysFont("arial", FONT_SIZE * 4, bold=True)
    def __init__(self, pegboard, color="red"):
        pygame.sprite.Sprite.__init__(self)

        self.color = color
        if self.color == "red":
            self.track_x = 20
        if self.color == "green":
            self.track_x = 39
        if self.color == "blue":
            self.track_x = 57
        if self.color == "tan":
            self.track_x = 76

        self.pegboard = pegboard

        self.track_height = pegboard.track_height
        self.score = 0

        self.full_peg_image = load_image("spr_peg_" + color + ".png")
        self.half_peg_image = load_image("spr_peg_" + color + "_pegged.png")
        self.full_peg_image.set_colorkey((0, 0, 0))
        self.half_peg_image.set_colorkey((0, 0, 0))

        self.score_draw_timer = -1

        self.image = self.full_peg_image
        self.rect = self.image.get_rect()
        self.move_to_target = False
        self.target_position = (0, 0)
        self.hover = False
        self.is_front = False

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
            self.set_move_target(self.pegboard.rect.x + self.pegboard.finish_hole_position[0], self.pegboard.rect.y + self.pegboard.finish_hole_position[1])
        else:
            self.set_move_target(self.pegboard.rect.x + self.track_x, (self.pegboard.rect.bottom + (self.pegboard.peghole_height / 2)) - (self.pegboard.slices[3] + padding + ((self.pegboard.track_height - padding) * ((self.score - 1) / 120))))

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
            self.score_draw_timer = FPS * 2

        if self.is_front:
            if self.hover:
                self.score_draw_timer = int(FPS / 4) + 1
        else:
            self.score_draw_timer = -1

        if self.score_draw_timer >= 0:
            # TODO turn this into an fx message bubble
            self.score_draw_timer -= 1
            score_render = PegSprite.font.render(str(max(0, self.score)), True, WHITE)
            score_render.set_colorkey((0, 0, 0))
            circle_diam = max(score_render.get_height() + padding, score_render.get_width() + padding)
            to_draw = pygame.surface.Surface((circle_diam, circle_diam))
            pygame.draw.circle(to_draw, get_color_from_name(self.color), to_draw.get_rect().center, min(to_draw.get_width(), to_draw.get_height()) / 2.0, 0)
            to_draw.set_colorkey((0, 0, 0))
            score_rect = score_render.get_rect()
            score_rect.center = (to_draw.get_width() / 2, to_draw.get_height() / 2)
            to_draw.blit(score_render, score_rect)
            dest_rect = to_draw.get_rect()
            dest_rect.midright = self.rect.midtop
            to_draw.set_alpha(int(0xff * self.score_draw_timer * 4 / FPS))
            screen.blit(to_draw, get_rect_kept_on_screen(dest_rect))
        screen.blit(self.image, self.rect)

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
    def __init__(self, pegboard, color="red"):
        self.color = color
        self.pegboard = pegboard
        self.back = PegSprite(pegboard, color)
        self.front = PegSprite(pegboard, color)
        self.back.set_score(-2)
        self.front.set_score(-1)
        self.front.set_is_front(True)

        self.back.set_position(self.back.target_position)
        self.front.set_position(self.front.target_position)

    def draw(self):
        self.front.draw()
        self.back.draw()

    def update(self):
        self.front.update()
        self.back.update()

    def set_score(self, score):
        self.back.set_score(score)
        temp = self.front
        self.front = self.back
        self.back = temp

        self.front.set_is_front(True)
        self.back.set_is_front(False)

    def is_moving(self):
        return self.back.is_moving() or self.front.is_moving()



class PegBoardSprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(img_folder, "spr_peg_board.png"))
        self.peghole_image = pygame.image.load(os.path.join(img_folder, "spr_peg_hole.png"))
        self.slices = (12, 20, 12, 28)
        self.image = NineSlice.get_nine(self.image, self.slices, self.image.get_width(), HEIGHT - 3 * padding, stretch=True)
        self.track_height = self.image.get_height() - (self.slices[1] + self.slices[3])
        self.track_width = self.image.get_width() - (self.slices[0] + self.slices[2])
        self.peghole_height = int((self.track_height - (120 + padding)) / 120)
        self.peghole_image = pygame.transform.smoothscale(self.peghole_image, (self.peghole_image.get_width(), self.peghole_height))
        self.rect = self.image.get_rect()
        self.peghole_rect = self.peghole_image.get_rect()
        self.finish_hole_position = (48, 10)
        for i in range(120):
            self.peghole_rect.center = (20, self.rect.height - (self.slices[3] + padding + ((self.track_height - padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        for i in range(120):
            self.peghole_rect.center = (39, self.rect.height - (self.slices[3] + padding + ((self.track_height - padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        for i in range(120):
            self.peghole_rect.center = (57, self.rect.height - (self.slices[3] + padding + ((self.track_height - padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        for i in range(120):
            self.peghole_rect.center = (76, self.rect.height - (self.slices[3] + padding + ((self.track_height - padding) * (i / 120))))
            self.image.blit(self.peghole_image, self.peghole_rect)
        self.image.set_colorkey((0, 0, 0))
        self.rect.right = WIDTH - padding
        self.rect.bottom = HEIGHT - padding

        self.peg_pairs = [PegPair(self, "red"), PegPair(self, "green"), PegPair(self, "blue"), PegPair(self, "tan")]

    def pegs_are_moving(self):
        for pegpair in self.peg_pairs:
            if pegpair.is_moving():
                return True
        return False

    def update(self):
        for peg_pair in self.peg_pairs:
            peg_pair.update()

    def draw(self):
        screen.blit(self.image, self.rect)
        for peg_pair in self.peg_pairs:
            peg_pair.draw()