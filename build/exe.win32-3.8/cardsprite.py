import pygame
import random
from globals import *
from playingcard import suits, cards
from utils import *
from nineslice import NineSlice

class CardSprite(pygame.sprite.Sprite):
    def __init__(self, name, suit, card_collection):
        pygame.sprite.Sprite.__init__(self)
        self.deck = card_collection
        self.font = pygame.font.SysFont("arial", 20, bold=True)
        self.width = CARD_WIDTH #96
        self.height = CARD_HEIGHT #135
        self.name = name
        self.suit = suit
        self.suit_image = pygame.image.load(os.path.join(img_folder, "spr_" + self.suit + ".png"))
        self.face_image = pygame.image.load(os.path.join(img_folder, "spr_card.png"))
        self.back_image = pygame.image.load(os.path.join(img_folder, "spr_card_back.png"))
        self.image = None
        self.is_face_up = False
        self.update_images()
        #self.rect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.mouse_drag = False
        self.drag_anchor = None
        self.target_position = (random.randint(0, PLAY_WIDTH), random.randint(0, HEIGHT)) # None
        self.move_to_target = True
        self.move_speed = 10
        self.clickable = True
        self.drop_target = None
        self.cut_deck_here = False
        self.angle = 0
        self.target_angle = 0
        self.alpha = 0xff
        self.target_alpha = 0xff

    def __str__(self):
        toReturn = "CardSprite: " + " ".join([self.name, suits.get_symbol(self.suit)])
        return toReturn

    def is_moving(self):
        return self.move_to_target

    def get_card_collection(self):
        return self.deck

    def get_drop_target(self):
        return self.drop_target

    def clear_drop_target(self):
        self.drop_target = None
        self.move_to_target = True

    def set_clickable(self, bool):
        self.clickable = bool

    def set_card_collection(self, card_collection):
        self.deck = card_collection

    def update_images(self):
        self.face = NineSlice.get_nine(self.face_image, (8, 8, 8, 8), self.width, self.height)
        self.face.blit(pygame.transform.smoothscale(self.suit_image, (int(self.height * 0.6), int(self.height * 0.6))), (int(self.width * 0.3), int(self.height * 0.3)))
        self.face.blit(self.font.render(self.name, True, BLACK), (padding, padding))
        self.back = NineSlice.get_nine(self.back_image, (8, 8, 8, 8), self.width, self.height, stretch=True)
        if self.image == None:
            self.image = self.back
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

    def send_to_back(self):
        self.deck.draw_list.remove(self)
        self.deck.draw_list[:0] = self

    def bring_to_front(self):
        self.deck.draw_list.remove(self)
        self.deck.draw_list.append(self)

    def set_image(self, image):
        self.image = image
        self.image.set_colorkey((0, 0, 0))

    def is_cut_card(self):
        return self.cut_deck_here

    def clear_cut_card(self):
        self.cut_deck_here = False

    def get_position(self):
        return self.rect.center

    def set_move_target(self, targ_x, targ_y):
        self.target_position = (targ_x, targ_y)
        self.move_to_target = True

    def set_drag_anchor(self, _x, _y):
        self.drag_anchor = (_x - self.rect.x, _y - self.rect.y)
        self.mouse_drag = True

    def find_drop_target(self):
        for coll in all_card_collections:
            if coll.is_droppable() and self.rect.colliderect(coll.get_rect()):
                self.drop_target = coll
                return
        self.clear_drop_target()

    def has_drop_target(self):
        return self.drop_target != None

    def clear_drag_anchor(self):
        self.drag_anchor = None
        self.mouse_drag = False

        if self.deck.get_name() == "deck":
            self.cut_deck_here = True
            return

        # check for drop targets
        self.find_drop_target()

        # find own index
        self_i = 0
        for i in range(len(self.deck.cards_list)):
            if (self == self.deck.cards_list[i].get_sprite()):
                self_i = i
                break
        changed_position = False
        for i in range(len(self.deck.cards_list)):
            cardsprite = self.deck.cards_list[i].get_sprite()
            if i != self_i:
                if self.rect.collidepoint((cardsprite.rect.midleft)):
                    card_to_move = self.deck.cards_list[self_i]
                    self.deck.cards_list.remove(card_to_move)
                    if i > self_i:
                        i -= 1
                    self.deck.cards_list[i:i] = [card_to_move]
                    changed_position = True
                    break
                elif self.rect.collidepoint((cardsprite.rect.midright)):
                    card_to_move = self.deck.cards_list[self_i]
                    self.deck.cards_list.remove(card_to_move)
                    if i < self_i:
                        i += 1
                    self.deck.cards_list[i:i] = [card_to_move]
                    changed_position = True
                    break
        if (changed_position):
            self.deck.reset_card_positions()
        else:
            self.move_to_target = True

    def __eq__(self, other):
        if other == None:
            return False

        name_comp = self.name == other.name
        suit_comp = self.suit == other.suit
        return name_comp and suit_comp


    def move_by_anchor(self, _anchor, target_x, target_y):
        self.rect.x = target_x - _anchor[0]
        self.rect.y = target_y - _anchor[1]

    def move_towards_target(self):
        move_x = (self.target_position[0] - self.rect.x) * 0.3
        move_y = (self.target_position[1] - self.rect.y) * 0.3
        if (abs(self.rect.x - self.target_position[0]) == 0) and (
                abs(self.rect.y - self.target_position[1]) > 0):
            self.rect.y += get_sign(move_y) * max(abs(move_y), 1)
        elif (abs(self.rect.x - self.target_position[0]) > 0) and (
                abs(self.rect.y - self.target_position[1]) == 0):
            self.rect.x += get_sign(move_x) * max(abs(move_x), 1)
        else:
            self.rect.x += get_sign(move_x) * max(abs(move_x), 1)
            self.rect.y += get_sign(move_y) * max(abs(move_y), 1)
        if (abs(self.rect.x - self.target_position[0]) < 2 and abs(self.rect.y - self.target_position[1]) < 2):
            self.rect.x, self.rect.y = self.target_position
            self.move_to_target = False

    def on_mouse_down(self, pos, button):
        if not self.clickable:
            return False
        if self.rect.collidepoint(pos) and button == 1:
            self.bring_to_front()
            self.set_drag_anchor(pos[0], pos[1])
            return True
        return False

    def on_mouse_up(self, pos, button):
        if not self.clickable:
            return False
        if self.mouse_drag and button == 1:
            self.clear_drag_anchor()
            return True
        return False

    def on_mouse_hold(self, pos, button):
        if not self.clickable:
            return False
        if self.rect.collidepoint(pos) and button == 1:
            #self.mouse_drag = True
            #self.set_drag_anchor(pos[0], pos[1])
            return True
        return False

    def set_facing(self, new_is_face_up):
        self.is_face_up = new_is_face_up
        self.update_facing_image()

    def get_facing(self):
        return self.is_face_up

    def update_facing_image(self):
        if self.is_face_up:
            self.set_image(self.face)
        else:
            self.set_image(self.back)

    def on_double_click(self, pos, button):
        if not self.clickable:
            return False
        if self.rect.collidepoint(pos) and button == 1:
            self.set_facing(not self.get_facing())
            return True
        return False

    def set_angle(self, degs):
        self.target_angle = degs

    def set_alpha(self, floatval):
        self.target_alpha = float_to_alpha(floatval)

    def update(self):
        if self.mouse_drag:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.move_by_anchor(self.drag_anchor, mouse_x, mouse_y)
            self.set_angle(0)
        else:
            if self.move_to_target:
                if self.has_drop_target():
                    self.move_to_target = False
                    return
                self.move_towards_target()

        if self.angle != self.target_angle:
            self.angle += (self.target_angle - self.angle) * 0.3
            if abs(self.target_angle - self.angle) < 3:
                self.angle = self.target_angle

        if self.alpha != self.target_alpha:
            self.alpha += (self.target_alpha - self.alpha) * 0.15
            if abs(self.target_alpha - self.alpha) < 3:
                self.alpha = self.target_alpha

    def draw(self):
        if self.angle != 0:
            to_draw = pygame.transform.rotozoom(self.image, self.angle, 1)
            to_draw.set_colorkey((0, 0, 0))
            to_draw_rect = to_draw.get_rect()
            to_draw_rect.center = self.rect.center
            to_draw.set_alpha(self.alpha)
            screen.blit(to_draw, to_draw_rect)
        else:
            self.image.set_alpha(self.alpha)
            screen.blit(self.image, self.rect)