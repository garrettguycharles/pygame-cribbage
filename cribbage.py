import time
import pygame
import gc

pygame.init()
pygame.mixer.init()

from nineslice import NineSlice
from utils import *
import random
import copy
import os
import globals
from cardsprite import CardSprite
from playingcard import suits, cards
from model import *
from visual_fx import FloatingMessage, AnimatedIcon
from pegboard import PegBoardSprite
from ui import *


font = pygame.font.SysFont("arial", globals.FONT_SIZE, bold=True)
font_large = pygame.font.SysFont("arial", 50, bold=True)
table_image = load_image("spr_table.png")
table_image = NineSlice.get_nine(table_image, (32, 32, 32, 32), globals.TABLE_RECT.width, globals.TABLE_RECT.height)

def refresh_table_image():
    global font, font_large, table_image
    font = pygame.font.SysFont("arial", int(globals.FONT_SIZE), bold=True)
    font_large = pygame.font.SysFont("arial", int(globals.FONT_SIZE * 2.5), bold=True)
    table_image = load_image("spr_table.png")
    table_image = NineSlice.get_nine(table_image, (32, 32, 32, 32), globals.TABLE_RECT.width, globals.TABLE_RECT.height)


def set_game_scale(num):
    # global globals.GAME_SCALE, WINDOWED_WIDTH, WINDOWED_HEIGHT, globals.WIDTH, globals.HEIGHT, globals.CARD_WIDTH, globals.CARD_HEIGHT
    # global FONT_SIZE, globals.padding, globals.PLAY_WIDTH, TABLE_WIDTH, TABLE_MARGIN, TABLE_RECT, screen

    globals.GAME_SCALE = num

    refresh_globals()

def refresh_globals():

    globals.WINDOWED_WIDTH = int(globals.FULLSCREEN_WIDTH * globals.GAME_SCALE)  # 1778
    globals.WINDOWED_HEIGHT = int(globals.FULLSCREEN_HEIGHT * globals.GAME_SCALE)  # 1000

    globals.WIDTH = globals.WINDOWED_WIDTH
    globals.HEIGHT = globals.WINDOWED_HEIGHT

    globals.CARD_WIDTH = int(globals.GAME_SCALE * 64)  # 48 #96
    globals.CARD_HEIGHT = int(globals.GAME_SCALE * 90)  # 67 #135
    globals.FONT_SIZE = int(globals.GAME_SCALE * 20)
    globals.padding = int(globals.GAME_SCALE * 10)  # 5

    globals.PLAY_WIDTH = globals.WIDTH - ((globals.padding * 3) * 12 + globals.padding * 4)
    globals.TABLE_WIDTH = globals.HEIGHT
    globals.TABLE_MARGIN = (globals.PLAY_WIDTH - globals.TABLE_WIDTH) / 2
    globals.TABLE_RECT = pygame.rect.Rect(globals.TABLE_MARGIN + globals.padding, globals.padding, globals.TABLE_WIDTH - globals.padding * 2, globals.HEIGHT - globals.padding * 2)
    globals.TABLE_RECT.topleft = (globals.TABLE_MARGIN + globals.padding, globals.padding)

    globals.screen = pygame.display.set_mode((globals.WIDTH, globals.HEIGHT), pygame.RESIZABLE)


class Player:
    def __init__(self, is_AI=False):
        self.is_AI = is_AI
        if self.is_AI:
            self.type = "CPU"
        else:
            self.type = "Player"
        self.hand = Hand(should_draw=True, name="hand")
        self.played = Hand(should_draw=True, name="play", label=("play" if not self.is_AI else ""),
                           droppable=False,
                           dimensions=([globals.CARD_WIDTH * 3, globals.CARD_HEIGHT] if not self.is_AI else [globals.CARD_WIDTH, globals.CARD_HEIGHT]))
        self.points = 0
        self.name = "Unnamed"
        self.dealer_token_position = (0, 0)
        self.pegs_icon_position = (0, 0)
        self.cutter_icon_position = (0, 0)
        self.peg_pair = None
        self.pegs_icon = None
        self.play_delay = -1

    def __repr__(self):
        toReturn = self.name + ": "
        toReturn += self.get_type() + "\n"
        toReturn += "Points: " + str(self.get_points()) + "\n"
        toReturn += "Hand: " + str(self.hand) + "\n"
        return toReturn

    def __str__(self):
        toReturn = self.name + ": "
        toReturn += self.get_type() + "\n"
        toReturn += "Points: " + str(self.get_points()) + "\n"
        return toReturn

    def refresh_pegs_icon(self):
        if self.pegs_icon != None:
            self.pegs_icon.end()
        self.pegs_icon = AnimatedIcon(name=self.peg_pair.color + "_pegs", fps=15, loop_repeat=0, pause_duration=1, center=self.pegs_icon_position, height=64)

    def refresh_icon_positions(self):
        normal_angle = get_angle_between_points(self.get_card_collection().get_position(), globals.TABLE_RECT.center)
        self.dealer_token_position = add_coords(distance_in_direction(normal_angle - 90, globals.CARD_WIDTH * 5), self.get_card_collection().get_position())
        self.cutter_icon_position = self.dealer_token_position
        self.pegs_icon_position = add_coords(distance_in_direction(normal_angle - 90, globals.CARD_WIDTH * 4), self.get_card_collection().get_position())

    def get_name(self):
        return self.name

    def get_type(self):
        return self.type

    def set_name(self, new_name):
        self.name = new_name

    def send_cards_to(self, other, cards_list):
        other.get_hand().insert_all_of(cards_list)
        self.get_hand().remove_all_of(cards_list)

    def send_card(self, other, card):
        other.get_card_collection().insert(card)
        self.get_card_collection().remove(card)

    def get_card_collection(self):
        return self.hand.get_card_collection()

    def get_cards(self):
        return self.get_hand().get_cards()

    def return_cards(self, deck):
        dest = deck.get_card_collection()
        self.hand.send_all_to(dest)
        self.played.send_all_to(dest)

    def set_hand(self, cards_list):
        self.hand.get_card_collection().set_cards(cards_list)
        self.played.get_card_collection().set_cards([])

    def get_hand(self):
        return self.hand

    def get_played(self):
        return self.played

    def get_hand_score(self, cut_starter_card=None, is_crib=False):
        return self.hand.get_score(cut_starter_card, is_crib)

    def get_points(self):
        return self.points

    def peg_points(self, num_points, cribbage_game, message="", message_delay = 0):
        self.points += num_points
        # self.peg_pair.set_score(self.points)
        in_motion_message = "+" + str(num_points)
        if (message == ""):
            message = in_motion_message
        FloatingMessage(message, self.played.get_card_collection().get_position(), self.peg_pair.back.get_position(),
                        color=self.peg_pair.color, execute_on_arrival=self.peg_pair.set_score,
                        execute_args=[self.points], in_motion_message=in_motion_message, end_scale=0.5, fade_in_delay=message_delay)
        if self.points >= cribbage_game.get_finish_line():
            cribbage_game.end_game()

    def pick_up_cards(self):
        self.played.send_all_to(self.hand)
        for card in self.hand.get_cards():
            card.get_sprite().set_facing(True)

    def flip_played_cards(self):
        for card in self.played.get_cards():
            card.get_sprite().set_facing(False)

    def cut_deck(self, deck):
        cut_range = len(deck)
        if (self.is_AI):
            return deck.cut(random.randint(2, cut_range - 2))
        else:
            # TODO: let player click deck to cut it :)
            return deck.cut(-1)

    def clear_play_delay(self):
        self.play_delay = -1

    def play_card(self, played_so_far):
        global fast_forward
        return_box = VarsBox()
        return_box.skip_step = False
        return_box.cannot_play = False
        return_box.out_of_cards = False

        play_count = cards.sum_card_value(played_so_far)

        if self.is_AI:
            if globals.fast_forward:
                self.play_delay = 0

            if self.play_delay < 0:
                if len(self.hand) < 1 or self.hand.get_min_card().get_value() + play_count > 31:
                    self.play_delay = int(0.5 * globals.FPS)
                elif len(self.get_cards()) == 1:
                    self.play_delay = int(random.randint(1, 3) * 0.25 * globals.FPS)
                else:
                    self.play_delay = int(random.randint(3, 10) * 0.25 * globals.FPS)
                return_box.skip_step = True
                return return_box
            if self.play_delay > 0:
                self.play_delay -= 1
                return_box.skip_step = True
                return return_box


        if (len(self.hand) < 1):
            if not self.is_AI:
                print("You are out of cards.")
            else:
                print(self.get_name() + " is out of cards.")

            if self is not globals.game.play_vars.last_player_to_play:
                FloatingMessage("out of cards", self.get_played().get_card_collection().get_position(),
                            self.get_played().get_card_collection().get_position(), color=self.peg_pair.color,
                            anim_delay=1, await_animation=False)

            return_box.cannot_play = True
            return_box.out_of_cards = True
            self.clear_play_delay()
            return return_box

        if self.hand.get_min_card().get_value() + play_count > 31:
            if not self.is_AI:
                print("You cannot play any of your cards.")
            else:
                print(self.get_name() + " cannot play any of their cards.")

            if self is not globals.game.play_vars.last_player_to_play:
                FloatingMessage("go", self.get_played().get_card_collection().get_position(),
                            self.get_played().get_card_collection().get_position(), color=self.peg_pair.color,
                            anim_delay=1)
            return_box.cannot_play = True
            self.clear_play_delay()
            return return_box

        card_to_play = None
        if self.is_AI:

            if (play_count < 15):
                for card in self.get_cards():
                    if (card.get_value() + play_count == 15):
                        card_to_play = card
                        break
                if (card_to_play == None):
                    card_to_play = self.hand.get_max_card()

            else:
                for card in self.get_cards():
                    if card.get_value() + play_count == 31:
                        card_to_play = card
                        break
                if (card_to_play == None):
                    for card in self.get_cards():
                        if (card.get_value() + play_count < 31):
                            card_to_play = card

            print("\n" + self.get_name() + " played " + str(card_to_play))

        else:
            card_to_play = None
            for card in self.get_cards():
                if card.get_sprite().has_drop_target():
                    targ_coll = card.get_sprite().get_drop_target()
                    if targ_coll.get_name() == "play":
                        card_to_play = card
                        break
                    card.get_sprite().clear_drop_target()

            if card_to_play == None:
                return_box.skip_step = True
                return return_box

            if card_to_play.get_value() + play_count > 31:
                card_to_play.get_sprite().clear_drop_target()
                return_box.skip_step = True
                return return_box

        self.send_card(self.played, card_to_play)
        card_to_play.get_sprite().set_facing(True)
        played_so_far.append(copy.copy(card_to_play))
        print("Count: " + str(cards.sum_card_value(played_so_far)))
        self.clear_play_delay()
        return return_box

    def make_crib_submission(self, crib):
        if (self.is_AI):
            suggestion = self.hand.get_crib_suggestion()
            sugg_cards = suggestion.get_cards()

            for card in sugg_cards:
                self.hand.send_card(crib.get_card_collection(), card)
            return True
        else:
            if (len(self.hand) <= 4):
                return True

            card_to_send = None
            for card in self.get_cards():
                if card.get_sprite().has_drop_target():
                    targ_coll = card.get_sprite().get_drop_target()
                    if targ_coll.get_name() == "crib":
                        card_to_send = card
                        break
                    card.get_sprite().clear_drop_target()

            if card_to_send == None:
                return False

            card_to_send.get_sprite().set_facing(False)
            self.hand.send_card(crib.get_card_collection(), card_to_send)
            return False


class Cribbage:
    def __init__(self, num_players=4, play_to=121):

        self.num_players = num_players
        self.players = [Player()]
        for i in range(num_players - 1):
            self.players.append(Player(True))
        #self.players = [Player(True) for i in range(num_players)]
        self.deck = Deck()
        self.crib = Hand(should_draw=True, name="crib", label="crib", droppable=True)
        self.cut_card = CardCollection(should_draw=True, name="cut", label="cut")
        self.current_cut_card = None
        self.dealer = 0
        self.game_over = False
        self.finish_line = play_to
        self.dealer_token = AnimatedIcon(name="dealer", pause_duration=10, height=64)
        self.cutter_icon = AnimatedIcon(name="scissors", loop_repeat=2, pause_duration=10, height=64, angle=135)

        self.pegboard = PegBoardSprite(num_lanes=self.num_players)

        self.set_up_hands_UI()

        for i in range(len(self.players)):
            self.players[i].peg_pair = self.pegboard.peg_pairs[i]
            self.players[i].refresh_icon_positions()
            self.players[i].refresh_pegs_icon()

        self.round_state = "deal"
        self.play_state = "begin_the_play"
        self.show_state = "begin_the_show"
        self.deal_state = "shuffle"
        self.anim_show_state = "start_show_animation"

        self.round_vars = VarsBox()
        self.play_vars = VarsBox()
        self.show_vars = VarsBox()
        self.deal_vars = VarsBox()
        self.anim_show_vars = VarsBox()

        self.round_vars.crib_submission_turn = 0

    def rebuild_game_window(self):
        refresh_table_image()
        self.pegboard.on_window_rebuild()
        self.fast_forward_button.end()
        self.sort_button.end()
        self.exit_button.end()

        self.set_up_hands_UI()

        for card_coll in globals.all_card_collections:
            card_coll.on_window_rebuild()

        for player in self.players:
            player.refresh_pegs_icon()
            player.refresh_icon_positions()

        if self.dealer_token != None:
            self.dealer_token.end()
        if self.cutter_icon != None:
            self.cutter_icon.end()

        self.dealer_token = AnimatedIcon(name="dealer", pause_duration=10, height=64)
        self.cutter_icon = AnimatedIcon(name="scissors", loop_repeat=2, pause_duration=10, height=64, angle=135)

        self.dealer_token.set_position(self.players[self.dealer].dealer_token_position)
        self.cutter_icon.set_position(self.players[self.get_cutter_index()].cutter_icon_position)

        gc.collect()

    def set_fast_forward(self, bool):
        globals.fast_forward = bool

    def close_game(self):
        globals.running = False

    def sort_player_hand(self):
        self.players[0].get_hand().sort()

    def set_up_hands_UI(self):

        self.fast_forward_button = Button(text=">>", on_click = self.set_fast_forward, is_toggle=True)
        self.fast_forward_button.rect.bottomleft = add_coords(globals.TABLE_RECT.bottomright, (globals.padding * 2, -globals.padding))

        self.sort_button = Button(text="sort", on_click=self.sort_player_hand)
        self.sort_button.rect.bottomleft = add_coords(self.fast_forward_button.rect.topleft, (0, -globals.padding))

        self.exit_button = Button(image="spr_button_exit.png", pressed_image="spr_button_exit_pressed.png", on_click=self.close_game, dimensions = (32, 32))
        self.exit_button.rect.topleft = (globals.padding, globals.padding)

        self.deck.deck.set_position(*globals.TABLE_RECT.center)

        # self.cut_card.set_position(self.deck.deck.x - (globals.padding + globals.CARD_WIDTH), self.deck.deck.y)
        self.cut_card.set_position(
            *get_absolute_coords((globals.padding + globals.CARD_WIDTH / 2, globals.padding + globals.CARD_HEIGHT / 2), globals.TABLE_RECT))

        self.crib.get_card_collection().set_position(self.deck.deck.x + globals.padding + globals.CARD_WIDTH, self.deck.deck.y)
        self.crib.get_card_collection().set_draw_card_separation(-globals.padding / 4, globals.padding)
        self.crib.get_card_collection().set_clickable(False)

        players_list = [player for player in self.players]

        # bottom player (user controlled)
        players_list[0].get_hand().get_card_collection().set_position(globals.PLAY_WIDTH / 2,
                                                                      globals.HEIGHT - (globals.padding * 2 + globals.CARD_HEIGHT / 2))
        players_list[0].get_hand().get_card_collection().set_draw_card_separation(globals.CARD_WIDTH + globals.padding, 0, angle=5)
        players_list[0].get_played().get_card_collection().set_position(globals.PLAY_WIDTH / 2,
                                                                        globals.HEIGHT - (globals.CARD_HEIGHT + globals.padding) * 2)
        players_list[0].get_played().get_card_collection().set_draw_card_separation(globals.CARD_WIDTH * 4 / 5, 0)


        if self.num_players == 4:
            # left player (CPU)
            players_list[1].get_hand().get_card_collection().set_position(globals.TABLE_MARGIN + globals.padding * 2 + globals.CARD_HEIGHT / 2,
                                                                          globals.HEIGHT / 2)
            players_list[1].get_hand().get_card_collection().set_draw_card_separation(0, globals.CARD_WIDTH * 0.5 + globals.padding,
                                                                                      angle=7)
            players_list[1].get_played().get_card_collection().set_position(globals.TABLE_MARGIN + (globals.padding + globals.CARD_HEIGHT * 2),
                                                                            globals.HEIGHT / 2)
            players_list[1].get_played().get_card_collection().set_draw_card_separation(0, globals.CARD_HEIGHT / 2)
            players_list[1].draw_score_position = (globals.padding, int(globals.HEIGHT * (4 / 5)))
            players_list[1].get_hand().get_card_collection().set_angle(-90)

            # top player (CPU)
            players_list[2].get_hand().get_card_collection().set_position(globals.PLAY_WIDTH / 2, globals.padding * 2 + globals.CARD_HEIGHT / 2)
            players_list[2].get_hand().get_card_collection().set_draw_card_separation(globals.CARD_WIDTH * 0.5 + globals.padding, 0,
                                                                                      angle=-7)
            players_list[2].get_played().get_card_collection().set_position(globals.PLAY_WIDTH / 2, (globals.CARD_HEIGHT + globals.padding) * 2)
            players_list[2].get_played().get_card_collection().set_draw_card_separation(globals.CARD_WIDTH * 4 / 5, 0)
            players_list[2].draw_score_position = (globals.PLAY_WIDTH * (1 / 5), globals.padding)
            players_list[2].get_hand().get_card_collection().set_angle(180)
            players_list[2].get_hand().get_card_collection().set_reverse_draw_order(True)

            # right player (CPU)
            players_list[3].get_hand().get_card_collection().set_position(
                globals.PLAY_WIDTH - (globals.TABLE_MARGIN + globals.padding * 2 + globals.CARD_HEIGHT / 2),
                globals.HEIGHT / 2)
            players_list[3].get_hand().get_card_collection().set_draw_card_separation(0, globals.CARD_WIDTH * 0.5 + globals.padding,
                                                                                      angle=-7)
            players_list[3].get_played().get_card_collection().set_position(
                globals.PLAY_WIDTH - globals.TABLE_MARGIN - (globals.padding + globals.CARD_HEIGHT) * 2,
                globals.HEIGHT / 2)
            players_list[3].get_played().get_card_collection().set_draw_card_separation(0, globals.CARD_HEIGHT / 2)
            players_list[3].draw_score_position = (globals.PLAY_WIDTH - (globals.padding + 100), globals.HEIGHT * (1 / 5))
            players_list[3].get_hand().get_card_collection().set_angle(90)
            players_list[3].get_hand().get_card_collection().set_reverse_draw_order(True)

        elif self.num_players == 3:

            # left player (CPU)
            players_list[1].get_hand().get_card_collection().set_position(globals.TABLE_MARGIN + globals.padding * 2 + globals.CARD_HEIGHT / 2,
                                                                          globals.HEIGHT / 2)
            players_list[1].get_hand().get_card_collection().set_draw_card_separation(0, globals.CARD_WIDTH * 0.5 + globals.padding,
                                                                                      angle=7)
            players_list[1].get_played().get_card_collection().set_position(globals.TABLE_MARGIN + (globals.padding + globals.CARD_HEIGHT * 2),
                                                                            globals.HEIGHT / 2)
            players_list[1].get_played().get_card_collection().set_draw_card_separation(0, globals.CARD_HEIGHT / 2)
            players_list[1].draw_score_position = (globals.padding, int(globals.HEIGHT * (4 / 5)))
            players_list[1].get_hand().get_card_collection().set_angle(-90)

            # right player (CPU)
            players_list[2].get_hand().get_card_collection().set_position(
                globals.PLAY_WIDTH - (globals.TABLE_MARGIN + globals.padding * 2 + globals.CARD_HEIGHT / 2),
                globals.HEIGHT / 2)
            players_list[2].get_hand().get_card_collection().set_draw_card_separation(0, globals.CARD_WIDTH * 0.5 + globals.padding,
                                                                                      angle=-7)
            players_list[2].get_played().get_card_collection().set_position(
                globals.PLAY_WIDTH - globals.TABLE_MARGIN - (globals.padding + globals.CARD_HEIGHT) * 2,
                globals.HEIGHT / 2)
            players_list[2].get_played().get_card_collection().set_draw_card_separation(0, globals.CARD_HEIGHT / 2)
            players_list[2].draw_score_position = (globals.PLAY_WIDTH - (globals.padding + 100), globals.HEIGHT * (1 / 5))
            players_list[2].get_hand().get_card_collection().set_angle(90)
            players_list[2].get_hand().get_card_collection().set_reverse_draw_order(True)

        else:  # self.num_players == 2

            # top player (CPU)
            players_list[1].get_hand().get_card_collection().set_position(globals.PLAY_WIDTH / 2, globals.padding * 2 + globals.CARD_HEIGHT / 2)
            players_list[1].get_hand().get_card_collection().set_draw_card_separation(globals.CARD_WIDTH * 0.5 + globals.padding, 0,
                                                                                      angle=-7)
            players_list[1].get_played().get_card_collection().set_position(globals.PLAY_WIDTH / 2, (globals.CARD_HEIGHT + globals.padding) * 2)
            players_list[1].get_played().get_card_collection().set_draw_card_separation(globals.CARD_WIDTH * 4 / 5, 0)
            players_list[1].draw_score_position = (globals.PLAY_WIDTH * (1 / 5), globals.padding)
            players_list[1].get_hand().get_card_collection().set_angle(180)
            players_list[1].get_hand().get_card_collection().set_reverse_draw_order(True)

        self.deck.get_card_collection().set_clickable(False)

        players_list[0].get_played().get_card_collection().set_clickable(False)

        for i in range(self.num_players):
            players_list[i].refresh_icon_positions()

        for i in range(1, self.num_players):
            players_list[i].get_hand().get_card_collection().set_clickable(False)
            players_list[i].get_played().get_card_collection().set_clickable(False)

    def get_finish_line(self):
        return self.finish_line

    def end_game(self):
        winner = None
        for player in self.players:
            if (player.get_points() >= self.finish_line):
                winner = player
        if winner == None:
            print("Someone tried to declare themselves the winner!  Liar!")
        else:
            print("\n\nGame Over!  Here is your winner:")
            print(winner)
            self.game_over = True

    def flip_played_cards(self):
        for player in self.players:
            player.flip_played_cards()

    def get_players(self):
        return self.players

    def get_cutter_index(self):
        return (self.dealer + 1) % len(self.players)

    def deal(self):
        if self.deal_state == "shuffle":
            for i in range(3):
                self.deck.shuffle()

            self.crib.get_card_collection().send_to_back()

            for card in self.deck.deck.get_cards():
                dist = random.randint(0, globals.CARD_HEIGHT * 3)
                dest = move_step(dist, card.get_sprite().get_position(),
                                 (random.randint(0, globals.WIDTH), random.randint(0, globals.HEIGHT)))
                card.get_sprite().set_move_target(dest[0], dest[1])
                card.get_sprite().set_angle(random.randint(0, 360))

            self.deal_state = "give_to_dealer"
            return False

        if self.deal_state == "give_to_dealer":
            self.players[self.dealer].pegs_icon.set_loop_repeat(1)
            deck_pos = self.players[self.dealer].get_played().get_card_collection().get_position()
            deck_pos = add_coords(deck_pos,
                                  distance_in_direction(self.players[self.dealer].get_card_collection().angle - 180,
                                                        globals.CARD_HEIGHT / 2))
            self.deal_vars.deck_home_position = self.deck.deck.get_position()
            self.deck.deck.set_position(*deck_pos)
            self.deal_vars.deck_home_angle = self.deck.deck.angle
            self.deck.deck.set_angle(self.players[self.dealer].get_hand().get_card_collection().angle)
            self.deck.deck.send_to_back()
            self.players[self.dealer].get_played().get_card_collection().send_to_back()
            self.deal_vars.hands_list = [player.get_hand() for player in self.players]
            self.deal_vars.num_cards = 0
            self.deal_vars.num_to_crib = 0
            if len(self.deal_vars.hands_list) == 2:
                self.deal_vars.num_cards = 6
            if len(self.deal_vars.hands_list) == 3:
                self.deal_vars.num_cards = 5
                self.deal_vars.num_to_crib = 1
            if len(self.deal_vars.hands_list) == 4:
                self.deal_vars.num_cards = 5

            self.deal_vars.round = 1
            self.deal_vars.turn = (self.dealer + 1) % len(self.players)
            self.deal_state = "deal"
            self.dealer_token.set_target_position(self.players[self.dealer].dealer_token_position)
            self.cutter_icon.set_target_position(self.players[self.get_cutter_index()].cutter_icon_position)
            return False

        if self.deal_state == "deal":
            # if self.deck.deal(self.deal_vars.num_cards, self.deal_vars.hands_list):
            self.deck.deal_card(self.players[self.deal_vars.turn].get_hand())

            if self.deal_vars.turn == self.dealer:
                self.deal_vars.round += 1

                if self.deal_vars.round > self.deal_vars.num_cards:
                    self.deal_state = "end_deal"
                    return False

            self.deal_vars.turn = (self.deal_vars.turn + 1) % len(self.players)
            return False

        if self.deal_state == "end_deal":
            self.players[self.dealer].pegs_icon.set_loop_repeat(0)
            self.deck.deck.set_angle(self.deal_vars.deck_home_angle)
            self.deck.deck.set_position(self.deal_vars.deck_home_position[0], self.deal_vars.deck_home_position[1])
            self.deck.deck.reset_card_positions()
            for card in self.players[0].get_card_collection().get_cards():
                card.get_sprite().set_facing(True)

            for i in range(self.deal_vars.num_to_crib):
                self.deck.deal_card(self.crib.get_card_collection())
            self.deal_state = "shuffle"
            return True

    def collect_cards(self):
        global screen_message
        self.cut_card.send_all_to(self.deck.get_card_collection())
        for player in self.players:
            player.return_cards(self.deck)
        self.crib.send_all_to(self.deck.get_card_collection())
        for card in self.deck.get_card_collection().get_cards():
            card.get_sprite().set_facing(False)
        self.deck.get_card_collection().reset_card_positions()
        screen_message = "Deck Length: " + str(len(self.deck))

    def step_the_play(self):
        if self.game_over:
            self.play_state = "begin_the_play"
            return True

        if self.play_state == "begin_the_play":
            self.play_vars.played_this_round = []
            self.play_vars.last_player_to_play = None
            self.play_vars.should_continue = True
            self.play_vars.turn = (self.dealer + 1) % len(self.players)
            self.play_vars.current_player = self.players[self.play_vars.turn]
            self.play_vars.num_out_of_cards = 0
            self.play_vars.num_cannot_play = 0
            self.play_state = "start_play_loop"
            return False

        if self.play_state == "start_play_loop":
            if not self.play_vars.should_continue:
                self.play_state = "begin_the_play"
                return True
            self.play_vars.current_player = self.players[self.play_vars.turn]
            self.play_vars.current_player.pegs_icon.set_loop_repeat(1)
            self.play_state = "let_player_play_card"
            return False

        if self.play_state == "let_player_play_card":
            if not self.play_vars.current_player.is_AI:
                self.play_vars.current_player.get_played().get_card_collection().set_droppable(True)

            self.play_vars.play_result = self.play_vars.current_player.play_card(self.play_vars.played_this_round)
            if self.play_vars.play_result.skip_step:
                return False
            if self.play_vars.play_result.cannot_play:
                self.play_state = "end_play_turn"
                self.play_vars.num_cannot_play += 1
                if self.play_vars.num_cannot_play == len(self.players):
                    if self.play_vars.last_player_to_play != None:
                        print(self.play_vars.last_player_to_play.get_name() + ": 1 Point for last card")
                        self.play_vars.last_player_to_play.peg_points(1, self, "last card")
                        self.play_vars.last_player_to_play = None
                    self.play_vars.played_this_round = []
                    self.play_vars.num_out_of_cards = 0
                    self.play_vars.num_cannot_play = 0
                    self.flip_played_cards()
                if self.play_vars.play_result.out_of_cards:
                    self.play_vars.num_out_of_cards += 1
                    if self.play_vars.num_out_of_cards == len(self.players):
                        self.play_vars.should_continue = False
                    else:
                        self.play_vars.num_out_of_cards = 0
            else:
                self.play_vars.num_cannot_play = 0
                self.play_vars.last_player_to_play = self.play_vars.current_player

                self.play_vars.should_continue = False

                for player in self.players:
                    if len(player.get_cards()) > 0:
                        self.play_vars.should_continue = True
                        break

                if not self.play_vars.should_continue:
                    if cards.sum_card_value(self.play_vars.played_this_round) != 31:
                        print(self.play_vars.last_player_to_play.get_name() + ": 1 point for last card")
                        self.play_vars.last_player_to_play.peg_points(1, self, "last card")

                self.play_state = "count_points"
            if not self.play_vars.current_player.is_AI:
                self.play_vars.current_player.get_played().get_card_collection().set_droppable(False)
            return False

        if self.play_state == "count_points":
            # TODO: break this up so that it animates the counting :) maybe.  Not as important

            messages_sent = 0
            delay_multiplier = 0.75

            # check for run in played cards
            for i in range(len(self.play_vars.played_this_round)):
                to_check = copy.deepcopy(self.play_vars.played_this_round[i:])
                if HandScorer.is_run(to_check):
                    print(self.play_vars.current_player.get_name() + ": " + str(len(to_check)) + " points for a run! ",
                          end="")
                    print(CardCollection(to_check))
                    self.play_vars.current_player.peg_points(len(to_check), self, "run of " + str(len(to_check)), message_delay = messages_sent * delay_multiplier)
                    messages_sent += 1
                    break

            # check for pairs in played cards
            for i in range(len(self.play_vars.played_this_round)):
                to_check = copy.deepcopy(self.play_vars.played_this_round[i:])
                if cards.are_same_number(to_check):
                    pairs_list = HandScorer.get_pairs(to_check)
                    print(self.play_vars.current_player.get_name() + ": " + str(
                        len(pairs_list) * 2) + " points for pair(s)! ", end="")
                    points_to_peg = 0
                    for pair in pairs_list:
                        print(CardCollection(pair))
                        points_to_peg += 2
                    self.play_vars.current_player.peg_points(points_to_peg, self,
                                                             ("pair" if len(pairs_list) < 2 else "pairs"), message_delay = messages_sent * delay_multiplier)
                    messages_sent += 1
                    break

            # check for fifteens
            if cards.sum_card_value(self.play_vars.played_this_round) == 15:
                print(self.play_vars.current_player.get_name() + ": 2 Points for Fifteen!")
                self.play_vars.current_player.peg_points(2, self, "fifteen", message_delay = messages_sent * delay_multiplier)
                messages_sent += 1

            # check for 31
            if cards.sum_card_value(self.play_vars.played_this_round) == 31:
                print(self.play_vars.current_player.get_name() + ": 2 Points for 31")
                self.play_vars.current_player.peg_points(2, self, "thirty-one", message_delay = messages_sent * delay_multiplier)
                messages_sent += 1
                self.play_vars.played_this_round = []
                self.play_vars.num_out_of_cards = 0
                self.play_vars.num_cannot_play = 0
                self.flip_played_cards()

            self.play_state = "end_play_turn"
            return False

        if self.play_state == "end_play_turn":
            if not self.play_vars.current_player.is_AI:
                self.play_vars.current_player.get_played().get_card_collection().set_droppable(False)

            for i in range(len(self.players)):
                self.players[i].pegs_icon.set_loop_repeat(0)

            self.play_vars.turn = (self.play_vars.turn + 1) % len(self.players)
            self.play_state = "start_play_loop"
            return False

    def animate_the_show(self):
        if globals.fast_forward:
            self.anim_show_vars.linger_delay = -1

        if self.anim_show_state == "start_show_animation":
            self.cut_card.send_all_to(self.show_vars.current_player.get_hand().get_card_collection())
            self.show_vars.current_player.get_hand().get_card_collection().sort()
            self.show_vars.current_player.get_hand().get_card_collection().reset_card_positions()
            self.anim_show_vars.i = 0
            self.anim_show_vars.hand = self.show_vars.current_player.get_hand().get_card_collection()
            self.anim_show_vars.played = self.show_vars.current_player.get_played().get_card_collection()
            self.anim_show_state = "show_fifteen"
            return False

        if self.anim_show_state == "show_fifteen":
            if self.anim_show_vars.i < len(self.show_vars.breakdown.fifteens):
                point_cards = self.show_vars.breakdown.fifteens[self.anim_show_vars.i].get_cards()
                for card in point_cards:
                    self.anim_show_vars.hand.send_card(self.anim_show_vars.played, card)
                self.anim_show_vars.played.sort()
                self.anim_show_vars.played.reset_card_positions(clear_drag = True)
                dist = globals.CARD_HEIGHT * 3
                start = self.anim_show_vars.played.get_position()
                dest = move_step(dist, start,
                                 (random.randint(0, globals.WIDTH), random.randint(0, globals.HEIGHT)))
                FloatingMessage("fifteen", start, dest, transition_duration=1.0, anim_delay=0.1, await_animation=False,
                                font_size=globals.FONT_SIZE, fade_in=False, color=self.show_vars.current_player.peg_pair.color)
            else:
                self.anim_show_vars.i = 0
                self.anim_show_state = "show_pair"
                return False
            self.anim_show_state = "retrieve_fifteen"
            self.anim_show_vars.linger_delay = globals.FPS
            return False

        if self.anim_show_state == "retrieve_fifteen":

            if self.anim_show_vars.linger_delay > 0:
                self.anim_show_vars.linger_delay -= 1
                return False

            self.anim_show_vars.played.send_all_to(self.anim_show_vars.hand)
            self.anim_show_vars.i += 1
            self.anim_show_state = "show_fifteen"
            return False

        if self.anim_show_state == "show_pair":
            if self.anim_show_vars.i < len(self.show_vars.breakdown.pairs):
                point_cards = self.show_vars.breakdown.pairs[self.anim_show_vars.i].get_cards()
                for card in point_cards:
                    self.anim_show_vars.hand.send_card(self.anim_show_vars.played, card)
                self.anim_show_vars.played.sort()
                self.anim_show_vars.played.reset_card_positions(clear_drag = True)
                dist = globals.CARD_HEIGHT * 3
                start = self.anim_show_vars.played.get_position()
                dest = move_step(dist, start,
                                 (random.randint(0, globals.WIDTH), random.randint(0, globals.HEIGHT)))
                FloatingMessage("pair", start, dest, transition_duration=1.0, anim_delay=0.1, await_animation=False,
                                font_size=globals.FONT_SIZE, fade_in=False, color=self.show_vars.current_player.peg_pair.color)
            else:
                self.anim_show_vars.i = 0
                self.anim_show_state = "show_run"
                return False
            self.anim_show_state = "retrieve_pair"
            self.anim_show_vars.linger_delay = globals.FPS
            return False

        if self.anim_show_state == "retrieve_pair":
            if self.anim_show_vars.linger_delay > 0:
                self.anim_show_vars.linger_delay -= 1
                return False

            self.anim_show_vars.played.send_all_to(self.anim_show_vars.hand)
            self.anim_show_vars.i += 1
            self.anim_show_state = "show_pair"
            return False

        if self.anim_show_state == "show_run":
            if self.anim_show_vars.i < len(self.show_vars.breakdown.runs):
                point_cards = self.show_vars.breakdown.runs[self.anim_show_vars.i].get_cards()
                for card in point_cards:
                    self.anim_show_vars.hand.send_card(self.anim_show_vars.played, card)
                self.anim_show_vars.played.sort()
                self.anim_show_vars.played.reset_card_positions(clear_drag = True)
                dist = globals.CARD_HEIGHT * 3
                start = self.anim_show_vars.played.get_position()
                dest = move_step(dist, start,
                                 (random.randint(0, globals.WIDTH), random.randint(0, globals.HEIGHT)))
                FloatingMessage("run", start, dest, transition_duration=1.0, anim_delay=0.1, await_animation=False,
                                font_size=globals.FONT_SIZE, fade_in=False, color=self.show_vars.current_player.peg_pair.color)
            else:
                self.anim_show_vars.i = 0
                self.anim_show_state = "show_flush"
                return False
            self.anim_show_state = "retrieve_run"
            self.anim_show_vars.linger_delay = globals.FPS
            return False

        if self.anim_show_state == "retrieve_run":
            if self.anim_show_vars.linger_delay > 0:
                self.anim_show_vars.linger_delay -= 1
                return False

            self.anim_show_vars.played.send_all_to(self.anim_show_vars.hand)
            self.anim_show_vars.i += 1
            self.anim_show_state = "show_run"
            return False

        if self.anim_show_state == "show_flush":
            if len(self.show_vars.breakdown.flush[0]) > 0:
                point_cards = self.show_vars.breakdown.flush[0].get_cards()
                for card in point_cards:
                    self.anim_show_vars.hand.send_card(self.anim_show_vars.played, card)
                self.anim_show_vars.played.sort()
                self.anim_show_vars.played.reset_card_positions(clear_drag = True)
                dist = globals.CARD_HEIGHT * 3
                start = self.anim_show_vars.played.get_position()
                dest = move_step(dist, start,
                                 (random.randint(0, globals.WIDTH), random.randint(0, globals.HEIGHT)))
                FloatingMessage("flush", start, dest, transition_duration=1.0, anim_delay=0.1, await_animation=False,
                                font_size=globals.FONT_SIZE, fade_in=False, color=self.show_vars.current_player.peg_pair.color)
                self.anim_show_vars.i = 0
                self.anim_show_state = "retrieve_flush"
                self.anim_show_vars.linger_delay = globals.FPS
            else:
                self.anim_show_state = "show_his_nob"
            return False

        if self.anim_show_state == "retrieve_flush":
            if self.anim_show_vars.linger_delay > 0:
                self.anim_show_vars.linger_delay -= 1
                return False

            self.anim_show_vars.played.send_all_to(self.anim_show_vars.hand)
            self.anim_show_vars.i += 1
            self.anim_show_state = "show_his_nob"
            return False

        if self.anim_show_state == "show_his_nob":
            if len(self.show_vars.breakdown.his_nob[0]) > 0:
                point_cards = self.show_vars.breakdown.his_nob[0].get_cards()
                for card in point_cards:
                    self.anim_show_vars.hand.send_card(self.anim_show_vars.played, card)
                self.anim_show_vars.played.sort()
                self.anim_show_vars.played.reset_card_positions(clear_drag = True)
                dist = globals.CARD_HEIGHT * 3
                start = self.anim_show_vars.played.get_position()
                dest = move_step(dist, start,
                                 (random.randint(0, globals.WIDTH), random.randint(0, globals.HEIGHT)))
                FloatingMessage("his nob", start, dest, transition_duration=1.0, anim_delay=0.1, await_animation=False,
                                font_size=globals.FONT_SIZE, fade_in=False,
                                color=self.show_vars.current_player.peg_pair.color)
            else:
                self.anim_show_vars.i = 0
                self.anim_show_state = "end_show_anim"
                return False
            self.anim_show_state = "retrieve_his_nob"
            self.anim_show_vars.linger_delay = globals.FPS
            return False

        if self.anim_show_state == "retrieve_his_nob":
            if self.anim_show_vars.linger_delay > 0:
                self.anim_show_vars.linger_delay -= 1
                return False

            self.anim_show_vars.played.send_all_to(self.anim_show_vars.hand)
            self.anim_show_vars.i += 1
            self.anim_show_state = "end_show_anim"
            return False

        if self.anim_show_state == "end_show_anim":
            self.anim_show_state = "start_show_animation"
            self.anim_show_vars = VarsBox()
            self.show_vars.current_player.get_hand().get_card_collection().send_card(self.cut_card,
                                                                                     self.current_cut_card)
            for card in self.show_vars.current_player.get_hand().get_cards():
                card.get_sprite().set_facing(False)
            self.show_vars.current_player.get_hand().get_card_collection().send_all_to(self.deck.get_card_collection())
            return True

    def step_the_show(self):

        if self.game_over:
            return True

        if self.show_state == "begin_the_show":
            self.show_vars.turn = (self.dealer + 1) % len(self.players)
            self.show_vars.should_continue = True

            self.show_state = "start_show_loop"
            return False

        if self.show_state == "start_show_loop":

            if not self.show_vars.should_continue:
                self.show_state = "begin_the_show"
                self.show_vars = VarsBox()
                return True

            self.show_vars.current_player = self.players[self.show_vars.turn]
            self.show_vars.breakdown = self.show_vars.current_player.get_hand().get_breakdown(self.get_cut_card())
            self.show_vars.hand_score = self.show_vars.breakdown.get_score()
            self.show_vars.current_player.pegs_icon.set_loop_repeat(1)

            print("\n\n" + self.show_vars.current_player.get_name() + "'s Hand: ", end="")

            print(self.show_vars.current_player.get_hand(), end=" ")
            print(str(self.get_cut_card()))
            print(self.show_vars.breakdown)

            self.show_state = "animate_the_show"
            return False

        if self.show_state == "animate_the_show":
            if self.animate_the_show():

                self.show_vars.current_player.peg_points(self.show_vars.hand_score, self)

                if self.show_vars.turn == self.dealer:
                    self.show_state = "move_cards_from_crib"
                else:
                    self.show_state = "increment_turn"
            return False

        if self.show_state == "move_cards_from_crib":
            self.show_vars.hand_score = 0
            self.show_vars.should_continue = False
            self.show_vars.current_player.return_cards(self.deck)
            for card in self.crib.get_cards():
                card.get_sprite().set_facing(True)
            self.crib.send_all_to(self.show_vars.current_player.get_hand())
            self.show_state = "count_crib"
            return False

        if self.show_state == "count_crib":
            print("\n" + self.show_vars.current_player.get_name() + " has the crib!")

            self.show_vars.breakdown = self.show_vars.current_player.get_hand().get_breakdown(self.get_cut_card(), True)
            self.show_vars.hand_score = self.show_vars.breakdown.get_score()
            print("Crib: ", end="")
            print(self.show_vars.current_player.get_hand(), end=" ")
            print(str(self.get_cut_card()))
            print(self.show_vars.breakdown)
            self.deck.deck.send_card(self.show_vars.current_player.get_hand().get_card_collection(),
                                     self.get_cut_card())
            self.show_state = "animate_crib_show"
            return False

        if self.show_state == "animate_crib_show":
            if self.animate_the_show():
                self.show_vars.current_player.peg_points(self.show_vars.hand_score, self)
                self.show_state = "increment_turn"
            return False

        if self.show_state == "increment_turn":
            for i in range(len(self.players)):
                self.players[i].pegs_icon.set_loop_repeat(0)
            self.show_vars.turn = (self.show_vars.turn + 1) % len(self.players)
            self.show_state = "start_show_loop"
            return False

    # def the_play(self): went here

    def get_cut_card(self):
        if len(self.cut_card) > 0:
            return self.cut_card.get_cards()[0]
        else:
            return None

    def set_cut_card(self, card):
        self.deck.deck.send_card(self.cut_card, card)
        self.current_cut_card = card

    def step(self):
        global screen_message
        if self.game_over:
            return

        if self.round_state == "begin_round":
            self.round_state = "deal"
            return

        if self.round_state == "deal":
            screen_message = "dealing..."
            if self.deal():
                self.round_state = "crib_submission"
            return

        if self.round_state == "crib_submission":
            if self.round_vars.crib_submission_turn < len(self.get_players()):
                self.players[self.round_vars.crib_submission_turn].pegs_icon.set_loop_repeat(1)
                if not self.players[self.round_vars.crib_submission_turn].is_AI:
                    screen_message = "Drag a card to the crib!"
                    self.crib.get_card_collection().set_droppable(True)
                else:
                    screen_message = "Waiting for everyone's crib submissions..."
                    self.crib.get_card_collection().set_droppable(False)

                if (self.players[self.round_vars.crib_submission_turn].make_crib_submission(self.crib)):
                    self.players[self.round_vars.crib_submission_turn].pegs_icon.set_loop_repeat(0)
                    self.round_vars.crib_submission_turn += 1
            else:
                self.round_vars.crib_submission_turn = 0
                self.crib.get_card_collection().set_droppable(False)
                self.round_state = "pre_cut"
            return

        if self.round_state == "pre_cut":
            self.deck.deck.set_draw_card_separation(0, -5)
            self.deck.deck.reset_card_positions()
            self.crib.get_card_collection().reset_card_positions(clear_drag = True)
            self.deck.deck.set_clickable(True)
            self.round_vars.cut_icon = AnimatedIcon(name="scissors",
                                                    osc_radius=(globals.CARD_WIDTH / 5, self.deck.deck.get_height() / 4),
                                                    center=add_coords((-globals.CARD_WIDTH, -globals.CARD_HEIGHT * 2/3),
                                                                      self.deck.deck.get_visual_center()), height=84,
                                                    angle=-90)
            self.round_state = "cut"
            return

        if self.round_state == "cut":
            # TODO
            # self.round_vars.cut_icon.point_towards = self.deck.deck.get_visual_center()
            self.round_vars.cut_icon.set_target_position(add_coords(self.deck.deck.get_visual_center(), (-globals.CARD_WIDTH, 0)))
            cutter = self.get_cutter_index()
            self.players[cutter].pegs_icon.set_loop_repeat(1)
            self.cutter_icon.set_pause_duration(0)

            if not self.players[cutter].is_AI:
                self.round_vars.cut_icon.message = "tap to cut deck"

            if self.players[cutter].cut_deck(self.deck):
                self.players[cutter].pegs_icon.set_loop_repeat(0)
                self.cutter_icon.set_pause_duration(10)

                self.round_vars.cut_icon.end()
                self.round_vars.cut_icon = None

                self.deck.deck.set_clickable(False)
                self.deck.deck.set_draw_card_separation(0, -1)
                self.deck.deck.reset_card_positions()
                cut_card = self.deck.deck.get_cards()[-1]
                self.set_cut_card(cut_card)
                print("\nCut card: " + str(self.get_cut_card()))

                if (self.get_cut_card().get_number() == 11):
                    print(self.players[self.dealer].get_name() + ": Two for his heels")
                    self.players[self.dealer].peg_points(2, self, "his heels")
                # TODO END

                self.round_state = "the_play"
            return

        if self.round_state == "the_play":
            screen_message = "round and round we go..."
            # TODO
            # input("Press enter to continue...")
            if self.step_the_play():
                self.round_state = "pick_up_cards"
            return

        if self.round_state == "pick_up_cards":
            for player in self.players:
                player.pick_up_cards()
            self.round_state = "the_show"
            return

        if self.round_state == "the_show":
            screen_message = "Count 'em up!"
            # TODO
            if self.step_the_show():
                self.round_state = "collect_cards"
            return

        if self.round_state == "collect_cards":
            self.collect_cards()
            self.round_state = "go_to_next_round"
            return

        if self.round_state == "go_to_next_round":
            self.dealer = (self.dealer + 1) % len(self.players)
            self.round_state = "begin_round"
            return

    '''
    def play_round(self):
        if self.game_over:
            return
        self.deal()

        for player in self.players:
            player.make_crib_submission(self.crib)

        cutter = (self.dealer + 1) % len(self.players)

        self.players[cutter].cut_deck(self.deck)
        self.cut_card = self.deck.draw_card()
        print("\nCut card: " + str(self.cut_card))

        if (self.cut_card.get_number() == 11):
            print(self.players[cutter].get_name() + ": Two for his heels")
            self.players[cutter].peg_points(2, self)

        time.sleep(random.randint(1, 3) * 0.5)

        if self.game_over:
            return

        print("\n\nBegin the Play:\n")

        self.the_play()

        if self.game_over:
            return

        print("\n\nBegin the Show:\n")

        for player in self.players:
            player.pick_up_cards()

        self.the_show()

        if self.game_over:
            return

        print("\n\nScores:\n")

        for player in self.players:
            print(player)

        self.collect_cards()
        self.dealer = (self.dealer + 1) % len(self.players)

    def play(self):
        for player in self.players:
            new_name = input("Please set name for " + (player.get_type()) + ": ")
            player.set_name(new_name)

        while not self.game_over:
            self.play_round()
    '''


double_click = {"button": None, "timer": 0}
click_hold = {"pos": None, "button": None, "timer": -1}

#table_image = pygame.transform.smoothscale(table_image, (TABLE_RECT.width, TABLE_RECT.height))

def update():
    global screen_message
    global fast_forward

    cards_settled = True

    for coll in globals.all_card_collections:
        for card in coll.get_cards():
            if card.get_sprite().is_moving():
                cards_settled = False
                break
        if not cards_settled:
            break

    fx_settled = True
    for fx in globals.all_visual_fx:
        if fx.is_moving():
            fx_settled = False
            break

    pegboard_settled = not globals.game.pegboard.pegs_are_moving()

    if globals.fast_forward or (cards_settled and fx_settled and pegboard_settled):
        globals.game.step()

    for i in range(len(globals.all_card_collections)):
        globals.all_card_collections[i].update()

    for i in range(len(globals.all_visual_fx)):
        if (i >= len(globals.all_visual_fx)):
            break
        globals.all_visual_fx[i].update()

    for i in range(len(globals.all_ui_elements)):
        globals.all_ui_elements[i].update()

    globals.game.pegboard.update()


def draw():
    globals.screen.fill(globals.BLACK)

    table_surface = pygame.surface.Surface((globals.TABLE_RECT.width, globals.TABLE_RECT.height))
    table_surface.set_colorkey((0, 0, 0))

    table_surface.blit(table_image, (0, 0, table_surface.get_width(), table_surface.get_height()))
    #pygame.draw.rect(table_surface, GREEN, (0, 0, TABLE_RECT.width, TABLE_RECT.height), 0, globals.padding * 2)

    if globals.game.round_state == "the_play" and globals.game.play_state != "begin_the_play":
        count = font_large.render(str(cards.sum_card_value(globals.game.play_vars.played_this_round)), True, globals.WHITE)
        count = pygame.transform.smoothscale(count, (count.get_width() * 2, count.get_height() * 2))
        count_rect = count.get_rect()
        count_rect.center = (globals.game.deck.deck.x - (globals.padding + globals.CARD_WIDTH + count.get_width() / 2), globals.game.deck.deck.y)
        count_rect.topleft = get_relative_coords(count_rect.topleft, globals.TABLE_RECT)
        table_surface.blit(count, count_rect)
        turn_pos = globals.game.play_vars.current_player.get_hand().get_card_collection().get_position()
        turn_pos = add_coords(turn_pos, scale_coord(globals.TABLE_RECT.topleft, -1))
        pygame.draw.circle(table_surface, globals.TURN_COLOR, turn_pos, globals.HEIGHT / 4, 0)

    globals.screen.blit(table_surface, globals.TABLE_RECT)

    if globals.game.round_state == "crib_submission":
        pygame.draw.circle(globals.screen, globals.TURN_COLOR, (globals.PLAY_WIDTH / 2, globals.HEIGHT / 2), get_distance((globals.PLAY_WIDTH / 2, globals.HEIGHT / 2),
                                                                                          globals.game.players[
                                                                                              0].get_played().get_card_collection().get_position()) * 0.5,
                           0)

    text = font.render(globals.screen_message, True, globals.WHITE)

    globals.screen.blit(text, (globals.padding, globals.HEIGHT - (globals.padding + text.get_height())))

    for i in reversed(range(len(globals.all_card_collections))):
        globals.all_card_collections[i].draw()

    globals.game.pegboard.draw()

    for i in range(len(globals.all_visual_fx)):
        globals.all_visual_fx[i].draw()

    for i in range(len(globals.all_ui_elements)):
        globals.all_ui_elements[i].draw()


def on_mouse_hold(pos, button):
    print("Button " + str(button) + " held at ", pos)

    for i in range(len(globals.all_card_collections)):
        globals.all_card_collections[i].on_mouse_hold(pos, button)


def on_double_click(pos, button):
    print("Button " + str(button) + " double clicked at ", pos)

    for i in range(len(globals.all_card_collections)):
        globals.all_card_collections[i].on_double_click(pos, button)


def on_mouse_down(pos, button):
    global click_hold
    click_hold["timer"] = globals.CLICK_DELAY
    click_hold["pos"] = pos
    click_hold["button"] = button

    print("Button " + str(button) + " clicked at ", pos)

    for i in range(len(globals.all_card_collections)):
        globals.all_card_collections[i].on_mouse_down(pos, button)

    for i in range(len(globals.all_ui_elements)):
        globals.all_ui_elements[i].on_mouse_down(pos, button)


def on_mouse_up(pos, button):
    global double_click
    global click_hold
    click_hold["timer"] = -1

    if (double_click["timer"] > 1 and button == double_click["button"]):
        on_double_click(pos, button)
        double_click["timer"] = 0
        double_click["button"] = None
    else:
        double_click["button"] = button
        double_click["timer"] = globals.CLICK_DELAY

    print("Button " + str(button) + " released at ", pos)

    for i in range(len(globals.all_card_collections)):
        globals.all_card_collections[i].on_mouse_up(pos, button)

    for i in range(len(globals.all_ui_elements)):
        globals.all_ui_elements[i].on_mouse_up(pos, button)

previous_resize_event = None
resize_event_repeats = 0
while (globals.running):

    if globals.game is None:
        globals.game = Cribbage(4)

    globals.clock.tick(globals.FPS)
    if (click_hold["timer"] == 0):
        on_mouse_hold(click_hold["pos"], click_hold["button"])
        click_hold["timer"] = -1

    if (click_hold["timer"] > 0):
        click_hold["timer"] -= 1
    if (double_click["timer"] > -1):
        double_click["timer"] -= 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            globals.running = False
        if event.type == pygame.WINDOWRESIZED:
            if event != previous_resize_event:
                resize_event_repeats = 0
                previous_resize_event = event
                wid = pygame.display.get_window_size()[0]
                frac = wid / globals.FULLSCREEN_WIDTH
                set_game_scale(frac)
                globals.game.rebuild_game_window()
            else:
                if event.x >= globals.FULLSCREEN_WIDTH:
                    globals.FULLSCREEN_WIDTH = event.x
                    globals.FULLSCREEN_HEIGHT = event.y
                    refresh_globals()
                    globals.game.rebuild_game_window()

        # if event.type == pygame.WINDOWRESTORED:
        #     set_game_scale(0.75)
        #     game.rebuild_game_window()
        if event.type == pygame.MOUSEBUTTONDOWN:
            on_mouse_down(event.pos, event.button)
        if event.type == pygame.MOUSEBUTTONUP:
            on_mouse_up(event.pos, event.button)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                globals.running = False
            if event.key == pygame.K_SPACE:
                globals.game.get_players()[0].get_hand().get_card_collection().sort()
            if event.key == pygame.K_h:
                globals.game.get_players()[0].get_hand().get_card_collection().shuffle()
            # if event.key == pygame.K_c:
            #     game.deck.cut(int(len(game.deck) / 2))
            # if event.key == pygame.K_f:
            #     for player in game.get_players():
            #         player.flip_played_cards()
            # if event.key == pygame.K_p:
            #     for player in game.get_players():
            #         player.pick_up_cards()

    # keys_list = pygame.key.get_pressed()
    # if keys_list[pygame.K_SPACE]:
    #     fast_forward = True
    # else:
    #     fast_forward = False

    update()

    draw()

    pygame.display.flip()
    # pygame.display.update()

pygame.quit()
