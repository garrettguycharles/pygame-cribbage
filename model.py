import copy
import random
from cardsprite import CardSprite
from playingcard import suits, cards
from nineslice import NineSlice
import globals
from utils import *

class Card:
    def __init__(self, card_num, suit, card_collection=None):
        self.suit = suit
        self.number = card_num
        self.name = cards.CARDS[self.number]
        self.sprite = CardSprite(self.name, self.suit, card_collection)

    def __deepcopy__(self, memodict={}):
        cls = self.__class__
        result = cls.__new__(cls)

        memodict[id(self)] = result

        for key, value in self.__dict__.items():
            if key == 'sprite':
                setattr(result, 'sprite', self.sprite)
            else:
                setattr(result, key, copy.deepcopy(value, memodict))


        return result


    def __str__(self):
        toReturn = " ".join([self.name, suits.get_symbol(self.suit)])
        return toReturn

    def __eq__(self, other):
        if (other == None):
            return False
        return (self.suit == other.suit and self.number == other.number)

    def __gt__(self, other):
        num_comp = self.number > other.number
        suit_comp = self.number == other.number and suits.get_number(self.suit) > suits.get_number(other.suit)

        return num_comp or suit_comp

    def __lt__(self, other):
        num_comp = self.number < other.number
        suit_comp = self.number == other.number and suits.get_number(self.suit) < suits.get_number(other.suit)

        return num_comp or suit_comp

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other

    def __hash__(self):
        return 17 * self.number + 1000 * suits.get_number(self.suit)

    def set_sprite(self, new_sprite):
        self.sprite = new_sprite

    def get_sprite(self):
        return self.sprite

    def is_pair(self, other):
        return self.number == other.number

    def is_fifteen(self, other):
        return (self.get_value() + other.get_value() == 15)

    def is_equal_number(self, other):
        return (self.number == other.number)

    def is_one_less_than(self, other):
        return (self.number == other.number - 1)

    def is_one_greater_than(self, other):
        return (self.number == other.number + 1)

    def is_same_suit(self, other):
        return self.get_suit() == other.get_suit()

    def get_suit(self):
        return self.suit

    def get_name(self):
        return self.name

    def get_number(self):
        return self.number

    def get_value(self):
        return cards.get_value(self.get_number())

class CardCollection:

    def __init__(self, cards_list=[], should_draw = False, name = "", label = "", droppable=False, dimensions=[globals.CARD_WIDTH, globals.CARD_HEIGHT], hide_spot_marker=False):
        self.font = pygame.font.SysFont("arial", globals.FONT_SIZE, bold=True)
        self.clickable = True
        self.base_dimensions = scale_coord_to_int(dimensions, 1 / globals.GAME_SCALE)
        self.dimensions = dimensions
        self.label = label
        self.name = name
        self.hide_spot_marker = hide_spot_marker
        self.should_draw = should_draw
        if (should_draw):
            globals.all_card_collections.append(self)
        self.sprite = None
        self.droppable = False
        if (self.label != ""):
            self.sprite = pygame.sprite.Sprite()
            self.sprite.image = load_image("spr_card_outline.png")
            self.sprite.image = NineSlice.get_nine(self.sprite.image, (8, 8, 8, 8), self.dimensions[0], self.dimensions[1])
            text_render = self.font.render(self.label, True, globals.WHITE)
            text_scale_w = globals.CARD_WIDTH - 2 * globals.padding
            text_scale_h = int(text_scale_w * (text_render.get_height() / text_render.get_width()))
            text_render = pygame.transform.smoothscale(text_render, (text_scale_w, text_scale_h))
            text_rect = text_render.get_rect()
            text_rect.center = self.sprite.image.get_rect().center
            self.sprite.image.set_colorkey((0, 0, 0))
            self.sprite.image.blit(text_render, text_rect)
            self.sprite.rect = self.sprite.image.get_rect()
            self.droppable = droppable

        self.draw_list = []
        self.cards_list = []
        self.set_cards(cards_list)
        self.card_draw_separation = (16, -16)
        self.reverse_draw_order = False
        self.card_angle_separation = 0
        self.x = globals.PLAY_WIDTH / 2
        self.y = globals.HEIGHT / 2
        self.angle = 0

    def __str__(self):
        if (len(self.cards_list) == 0):
            return ""
        if (len(self.cards_list) == 1):
            return str(self.cards_list[0])
        if (len(self.cards_list) > 10):
            return "\n".join([str(card) for card in self.cards_list])
        return "(" + " | ".join([str(card) for card in self.cards_list]) + ")"

    def __len__(self):
        return len(self.cards_list)

    def on_window_rebuild(self):
        for cardspr in self.draw_list:
            cardspr.on_window_rebuild()
        self.reset_card_positions()
        for i in range(len(self.draw_list)):
            self.draw_list[i].set_position(self.draw_list[i].target_position)

        if (self.label != ""):
            self.dimensions = scale_coord_to_int(self.base_dimensions, globals.GAME_SCALE)
            self.font = pygame.font.SysFont("arial", globals.FONT_SIZE, bold=True)
            temp = self.sprite.rect.center
            self.sprite = pygame.sprite.Sprite()
            self.sprite.image = load_image("spr_card_outline.png")
            self.sprite.image = NineSlice.get_nine(self.sprite.image, (8, 8, 8, 8), self.dimensions[0], self.dimensions[1])
            text_render = self.font.render(self.label, True, globals.WHITE)
            text_scale_w = globals.CARD_WIDTH - 2 * globals.padding
            text_scale_h = int(text_scale_w * (text_render.get_height() / text_render.get_width()))
            text_render = pygame.transform.smoothscale(text_render, (text_scale_w, text_scale_h))
            text_rect = text_render.get_rect()
            text_rect.center = self.sprite.image.get_rect().center
            self.sprite.image.set_colorkey((0, 0, 0))
            self.sprite.image.blit(text_render, text_rect)
            self.sprite.rect = self.sprite.image.get_rect()
            self.sprite.rect.center = temp

        self.reset_card_positions()

    def get_rect(self):
        if self.sprite != None:
            return self.sprite.rect

    def set_reverse_draw_order(self, val):
        self.reverse_draw_order = True

    def is_droppable(self):
        return self.droppable

    def set_droppable(self, val):
        self.droppable = val

    def set_angle(self, degs):
        self.angle = degs

    def get_name(self):
        return self.name

    def get_position(self):
        return (self.x, self.y)

    def set_cards(self, cards_list):
        self.cards_list = cards_list.copy()
        self.draw_list = [card.get_sprite() for card in self.cards_list]
        for card in self.cards_list:
            card.get_sprite().set_card_collection(self)

    def set_clickable(self, bool):
        self.clickable = bool

        for cardsprite in self.draw_list:
            cardsprite.set_clickable(self.clickable)

    def get_clickable(self):
        return self.clickable

    def set_position(self, _x, _y):
        self.x = _x
        self.y = _y
        if self.sprite != None:
            self.sprite.rect.center = (self.x, self.y)

    def set_draw_card_separation(self, x_sep, y_sep, angle=0):
        self.card_draw_separation = (x_sep, y_sep)
        self.card_angle_separation = angle
        self.reset_card_positions()

    def get_width(self):
        if (len(self.draw_list) < 1):
            return 0
        return self.draw_list[0].width + self.card_draw_separation[0] * (len(self.draw_list) - 1)

    def get_height(self):
        if (len(self.draw_list) < 1):
            return 0
        return self.draw_list[0].height + abs(self.card_draw_separation[1] * (len(self.draw_list) - 1))

    def get_visual_center(self):
        if len(self.cards_list) > 0:
            return scale_coord_to_int(add_coords(self.cards_list[0].get_sprite().rect.midbottom, self.cards_list[-1].get_sprite().rect.midbottom), 0.5)
        return self.get_position()

    def reset_card_positions(self, clear_drag = False):
        base_x = self.x - self.get_width() / 2
        base_y = self.y - self.get_height() / 2
        base_angle = self.angle + ((self.card_angle_separation * (len(self.get_cards()) - 1)) / 2)

        if self.sprite != None:
            base_x = self.x - self.get_width() / 2
            base_y = self.sprite.rect.top

        if abs(self.card_angle_separation) > 0:
            pos_offset_constant = abs(self.card_angle_separation)  #(45 / len(self.cards_list))
        else:
            pos_offset_constant = 1

        for i in range(len(self.cards_list)):
            card = self.cards_list[i].get_sprite()
            if clear_drag:
                card.clear_drag_anchor()
            angle = base_angle - i * self.card_angle_separation
            card.set_angle(angle)
            card.clear_cut_card()
            targ_x = base_x + i * self.card_draw_separation[0]
            targ_y = base_y + i * self.card_draw_separation[1]
            correction_dist = (math.pow(abs(self.angle - base_angle), 2) / pos_offset_constant)
            targ_x, targ_y = add_coords((targ_x, targ_y), distance_in_direction(self.angle, (math.pow(abs(self.angle - angle), 2) / pos_offset_constant) - correction_dist))
            card.set_move_target(targ_x, targ_y)
        self.draw_list = [card.get_sprite() for card in self.cards_list]

    def draw(self):
        if self.sprite != None and not self.hide_spot_marker:
            globals.screen.blit(self.sprite.image, self.sprite.rect)
        if self.reverse_draw_order:
            for i in reversed(range(len(self.draw_list))):
                self.draw_list[i].draw()
        else:
            for card_sprite in self.draw_list:
                card_sprite.draw()

    def update(self):

        for card in self.draw_list:
            if self.is_droppable():
                if not card.get_facing():
                    card.set_alpha(0.2)
                else:
                    card.set_alpha(0.8)
            else:
                card.set_alpha(1.0)



        for i in reversed(range(len(self.draw_list))):
            card = self.draw_list[i]
            card.update()

    def on_mouse_hold(self, pos, button):
        for i in reversed(range(len(self.draw_list))):
            card = self.draw_list[i]
            if card.on_mouse_hold(pos, button):
                break

    def on_double_click(self, pos, button):
        for i in reversed(range(len(self.draw_list))):
            card = self.draw_list[i]
            if card.on_double_click(pos, button):
                break

    def on_mouse_down(self, pos, button):
        for i in reversed(range(len(self.draw_list))):
            card = self.draw_list[i]
            if card.on_mouse_down(pos, button):
                break

    def on_mouse_up(self, pos, button):
        for i in reversed(range(len(self.draw_list))):
            card = self.draw_list[i]
            card.on_mouse_up(pos, button)


    def get_card_collection(self):
        return self

    def get_cards(self):
        return self.cards_list.copy()

    def insert(self, card):
        if not card in self.cards_list:
            self.cards_list.append(card)
            card.get_sprite().set_clickable(self.get_clickable())
            card.get_sprite().clear_drop_target()
            offset = len(self.draw_list)
            self.draw_list.append(card.get_sprite())
            card.get_sprite().set_card_collection(self)

        self.reset_card_positions()

    def remove(self, card):
        if (card in self.cards_list):
            self.cards_list.remove(card)
            self.draw_list.remove(card.get_sprite())
            self.reset_card_positions()

    def insert_all_of(self, cards_list):
        for card in cards_list:
            self.insert(card)

    def remove_all_of(self, cards_list):
        for i in reversed(range(len(cards_list))):
            self.remove(cards_list[i])

    def send_cards_to(self, other, cards_list):
        other.insert_all_of(cards_list)
        self.remove_all_of(cards_list)
        other.get_card_collection().reset_card_positions()

    def send_card(self, other, card):
        other.insert(card)
        self.remove(card)
        other.get_card_collection().reset_card_positions()

    def send_all_to(self, other):
        self.send_cards_to(other, copy.deepcopy(self.cards_list))

    def shuffle(self):
        shuffled = []
        while (len(self.cards_list) > 0):
            i = random.randint(0, len(self.cards_list) - 1)
            card = self.cards_list[i]
            shuffled.append(card)
            self.cards_list.remove(card)
        self.cards_list = shuffled
        self.draw_list = [card.get_sprite() for card in self.cards_list]
        self.reset_card_positions()

    def sort(self):
        cards.sort_cards(self.cards_list)
        self.draw_list = [card.get_sprite() for card in self.cards_list]
        self.reset_card_positions()

    def send_to_back(self):
        if not self.should_draw:
            raise Exception("Tried to send undrawn card collection to bottom of draw list")

        globals.all_card_collections.remove(self)
        globals.all_card_collections.append(self)

    def bring_to_front(self):
        if not self.should_draw:
            raise Exception("Tried to bring undrawn card collection to front of draw list")

        globals.all_card_collections.remove(self)
        globals.all_card_collections[0:0] = [self]


class Deck:
    def __init__(self):
        self.deck = CardCollection(Deck.generate_deck(), should_draw=True, name="deck", label="deck", hide_spot_marker=True)
        self.deck.x = 0
        self.deck.y = 0
        self.deck.set_position(globals.TABLE_MARGIN + globals.TABLE_WIDTH / 2, globals.HEIGHT / 2)
        self.deck.set_draw_card_separation(0, -1)
        self.cut_state = "ready_to_cut"

    def __len__(self):
        return len(self.deck)

    def __str__(self):
        toReturn = "DECK:\n"
        toReturn += str(self.deck)
        return toReturn

    def get_card_collection(self):
        return self.deck

    def shuffle(self):
        self.deck.shuffle()

    def cut(self, i):
        if self.cut_state == "ready_to_cut":
            if i < 0:
                for j in range(len(self.get_card_collection().get_cards())):
                    if self.get_card_collection().get_cards()[j].get_sprite().is_cut_card():
                        i = j
                        break
            if i < 0:
                return False

            _cards = self.deck.get_cards()

            for card in _cards[:i + 1]:
                c_spr = card.get_sprite()
                c_spr.set_move_target(c_spr.rect.x - (globals.CARD_WIDTH + globals.padding), c_spr.rect.y)

            cut_cards = _cards[i + 1:] + _cards[:i + 1]
            self.deck.set_cards(cut_cards)
            self.deck.draw_list[-1].set_facing(True)

            self.cut_state = "wait_for_animation"
            return False

        if self.cut_state == "wait_for_animation":
            self.deck.reset_card_positions()
            self.cut_state = "ready_to_cut"
            return True

    def draw_card(self):
        card = self.deck.get_cards()[-1]
        self.deck.remove(card)
        return card

    def deal_card(self, dest_card_collection):
        card = self.deck.get_cards()[-1]
        self.deck.send_card(dest_card_collection, card)

    def deal(self, num_cards, hands_list):
        for i in range(num_cards):
            for hand in hands_list:
                self.deal_card(hand.get_card_collection())
        self.get_card_collection().reset_card_positions()

    def generate_suit(suit):
        if (suit != suits.spade
                and suit != suits.heart
                and suit != suits.club
                and suit != suits.diamond):
            raise Exception("Error: unknown suit type in generate_suit(): " + str(suit))

        toReturn = []
        for i in range(1, 14):
            toReturn.append(Card(i, suit))

        return toReturn

    @staticmethod
    def generate_deck():
        toReturn = []
        for i in range(4):
            toReturn.extend(Deck.generate_suit(suits.SUITS[i]))
        return toReturn

class HandBreakdown:
    def __init__(self, fifteens, pairs, runs, flush, his_nob):
        self.scores = {"hand": 0, "fifteens": 0, "pairs": 0, "runs": 0, "flush": 0, "his_nob": 0}

        self.fifteens = []
        for fifteen in fifteens:
            self.scores["fifteens"] += 2
            self.fifteens.append(CardCollection(fifteen))

        self.scores["hand"] += self.scores["fifteens"]

        self.pairs = []
        for pair in pairs:
            self.scores["pairs"] += 2
            self.pairs.append(CardCollection(pair))

        self.scores["hand"] += self.scores["pairs"]

        self.runs = []
        for run in runs:
            self.runs.append(CardCollection(run))

        for run in self.runs:
            self.scores["runs"] += len(run)

        self.scores["hand"] += self.scores["runs"]

        self.flush = []
        self.flush.append(CardCollection(flush))

        for f in self.flush:
            self.scores["flush"] += len(f)

        self.scores["hand"] += self.scores["flush"]

        self.his_nob = []
        self.his_nob.append(CardCollection(his_nob))

        for n in self.his_nob:
            self.scores["his_nob"] += len(n)

        self.scores["hand"] += self.scores["his_nob"]

    def __str__(self):
        toReturn = "\nBreakdown: (" + str(self.scores["hand"]) + " points)\n"
        if (self.scores["fifteens"] > 0):
            toReturn += "\nFifteens: (" + str(self.scores["fifteens"]) + " points)\n"
            toReturn += "\n".join([str(fifteen) for fifteen in self.fifteens])
        if (self.scores["pairs"] > 0):
            toReturn += "\nPairs: (" + str(self.scores["pairs"]) + " points)\n"
            toReturn += "\n".join([str(pair) for pair in self.pairs])
        if (self.scores["runs"] > 0):
            toReturn += "\nRuns: (" + str(self.scores["runs"]) + " points)\n"
            toReturn += "\n".join([str(run) for run in self.runs])
        if (self.scores["flush"] > 0):
            toReturn += "\nFlush: (" + str(self.scores["flush"]) + " points)\n"
            toReturn += "\n".join([str(f) for f in self.flush])
        if (self.scores["his_nob"] > 0):
            toReturn += "\nHis nob: (" + str(self.scores["his_nob"]) + " point)\n"
            toReturn += "\n".join([str(nob) for nob in self.his_nob])
        return toReturn

    def get_score(self):
        return self.scores["hand"]

class HandScorer:
    def __init__(self):
        pass

    def is_run(in_cards):
        if len(in_cards) < 3:
            return False
        cards_list = copy.deepcopy(in_cards)
        cards.sort_cards(cards_list)

        toReturn = True
        for i in range(len(cards_list) - 1):
            if (cards_list[i].get_number() + 1 != cards_list[i + 1].get_number()):
                toReturn = False
                break
        return toReturn

    def get_points_in_run(in_cards):
        cards_list = copy.deepcopy(in_cards)

        cards.sort_cards(cards_list)

        if (HandScorer.is_run(cards_list)):
            return len(cards_list)
        else:
            return 0

    def get_combinations_for_fifteens(in_cards, in_cards_so_far):
        _cards = copy.deepcopy(in_cards)
        cards_so_far = copy.deepcopy(in_cards_so_far)
        my_value = cards.sum_card_value(cards_so_far)

        toReturn = []

        for i in range(len(_cards)):
            to_append = copy.deepcopy(cards_so_far)
            if (my_value + _cards[i].get_value() == 15):
                to_append.append(_cards[i])
                toReturn.append(to_append)
            elif (my_value + _cards[i].get_value() < 15):
                to_append.append(_cards[i])
                to_extend = HandScorer.get_combinations_for_fifteens(in_cards[i + 1:], to_append)
                toReturn.extend(to_extend)

        return toReturn

    def get_his_nob(in_hand, cut_starter_card):
        if (cut_starter_card == None):
            return []
        toReturn = []

        for card in in_hand:
            if card.get_number() == 11 and card.is_same_suit(cut_starter_card):
                toReturn.append(card)
                break
        return toReturn

    def get_flush(in_hand, cut_starter_card, is_crib=False):
        hand = copy.deepcopy(in_hand)
        is_flush = True
        flush_suit = hand[0].get_suit()

        for i in range(1, len(hand)):
            if hand[i].get_suit() != flush_suit:
                is_flush = False
                break

        if is_flush:
            if (cut_starter_card == None):
                return hand

            include_starter = cut_starter_card.get_suit() == flush_suit
            if is_crib and include_starter:
                hand.append(cut_starter_card)
                return hand
            else:
                if include_starter:
                    hand.append(cut_starter_card)
                return hand
        return []

    def get_fifteens(in_cards):
        _cards = copy.deepcopy(in_cards)
        cards.sort_cards(_cards)
        cards.flip_list(_cards)

        toReturn = []
        for i in range(len(_cards)):
            toReturn.extend(HandScorer.get_combinations_for_fifteens(_cards[i + 1:], [_cards[i]]))
        return toReturn

    def get_pairs(in_cards):
        _cards = copy.deepcopy(in_cards)
        cards.sort_cards(_cards)
        toReturn = []

        for i in range(len(_cards) - 1):
            for j in range(i + 1, len(_cards)):
                if (_cards[i].is_pair(_cards[j])):
                    toReturn.append([_cards[i], _cards[j]])
                else:  # we can skip the rest because our list of cards is sorted
                    break
        return toReturn

    def get_multiples(in_cards):
        _cards = copy.deepcopy(in_cards)
        multiples_list = []

        curr_multiple = []
        for i in range(len(_cards)):
            if (len(curr_multiple) < 1):
                curr_multiple.append(_cards[i])
            else:
                if _cards[i].is_equal_number(curr_multiple[-1]):
                    curr_multiple.append(_cards[i])
                else:
                    if (len(curr_multiple) > 1):
                        multiples_list.append(curr_multiple)
                    curr_multiple = [_cards[i]]

        if (len(curr_multiple) > 1):
            multiples_list.append(curr_multiple)

        return multiples_list

    def remove_multiples(in_cards):
        _cards = copy.deepcopy(in_cards)

        for i in reversed(range(len(_cards) - 1)):
            if _cards[i].is_equal_number(_cards[i + 1]):
                _cards.remove(_cards[i])
        return _cards

    def remove_duplicates_in_list(in_list):
        for i in reversed(range(len(in_list) - 1)):
            if (in_list[i] == in_list[i + 1]):
                in_list.remove(in_list[i])

    def get_combinations_from_multiples(in_cards, in_multiples_list):
        my_multiple = in_multiples_list[0]
        _cards = copy.deepcopy(in_cards)
        cards.sort_cards(_cards)
        multiples_list = copy.deepcopy(in_multiples_list)
        multiples_list.remove(my_multiple)

        toReturn = []

        for card in range(len(_cards)):
            for multiple in range(len(my_multiple)):
                if _cards[card].is_equal_number(my_multiple[multiple]):
                    _cards[card] = copy.deepcopy(my_multiple[multiple])
                    if (len(multiples_list) < 1):
                        toReturn.append(copy.deepcopy(_cards))
                    else:
                        to_extend = HandScorer.get_combinations_from_multiples(_cards, multiples_list)
                        toReturn.extend(copy.deepcopy(to_extend))

        HandScorer.remove_duplicates_in_list(toReturn)
        return toReturn

    def split_parallel_runs(in_cards):
        _cards = copy.deepcopy(in_cards)
        cards.sort_cards(_cards)

        if len(HandScorer.get_pairs(_cards)) < 1:
            return [_cards]

        multiples_list = HandScorer.get_multiples(_cards)

        _cards = HandScorer.remove_multiples(_cards)

        return HandScorer.get_combinations_from_multiples(_cards, multiples_list)

    def get_runs(in_cards):
        _cards = copy.deepcopy(in_cards)
        if (len(_cards) < 3):
            return []

        toReturn = []
        cards.sort_cards(_cards)

        working_array = []
        for i in range(len(_cards)):

            if (len(working_array) < 1):
                working_array.append(_cards[i])
            else:
                if _cards[i].is_one_greater_than(working_array[-1]) or _cards[i].is_equal_number(working_array[-1]):

                    working_array.append(_cards[i])
                else:
                    if (len(HandScorer.remove_multiples(working_array)) > 2):
                        toReturn.extend(HandScorer.split_parallel_runs(working_array))
                    working_array = [_cards[i]]
        if (len(HandScorer.remove_multiples(working_array)) > 2):
            toReturn.extend(HandScorer.split_parallel_runs(working_array))

        return toReturn

    def get_hand_breakdown(bare_hand, cut_starter_card=None, is_crib=False):
        hand_with_starter = copy.deepcopy(bare_hand)
        if (cut_starter_card != None):
            hand_with_starter.append(cut_starter_card)

        fifteens = HandScorer.get_fifteens(hand_with_starter)
        pairs = HandScorer.get_pairs(hand_with_starter)
        runs = HandScorer.get_runs(hand_with_starter)
        flush = HandScorer.get_flush(bare_hand, cut_starter_card, is_crib)
        his_nob = HandScorer.get_his_nob(bare_hand, cut_starter_card)

        return HandBreakdown(fifteens, pairs, runs, flush, his_nob)

class Hand:
    def __init__(self, cards_list=[], should_draw=False, name = "", label = "", droppable=False, dimensions=[globals.CARD_WIDTH, globals.CARD_HEIGHT]):
        self.hand = CardCollection(cards_list, should_draw=should_draw, name=name, label=label, droppable=droppable, dimensions=dimensions)
        self.hand.x = random.randint(50, globals.PLAY_WIDTH)
        self.hand.y = random.randint(50, globals.HEIGHT)
        self.hand.reset_card_positions()

    def __str__(self):
        return str(self.hand)

    def __len__(self):
        return len(self.hand)

    def set_position(self, _x, _y):
        self.hand.set_position(_x, _y)
    def send_cards_to(self, other, cards_list):
        other.get_card_collection().insert_all_of(cards_list)
        self.get_card_collection().remove_all_of(cards_list)

    def send_card(self, other, card):
        self.get_card_collection().remove(card)
        other.get_card_collection().insert(card)

    def send_all_to(self, other):
        self.get_card_collection().send_cards_to(other.get_card_collection(), self.get_card_collection().get_cards())

    def get_card_collection(self):
        return self.hand

    def get_cards(self):
        return self.get_card_collection().get_cards()

    def insert(self, card):
        self.hand.insert(card)

    def remove(self, card):
        self.hand.remove(card)

    def sort(self):
        self.hand.sort()

    def get_breakdown(self, cut_starter_card=None, is_crib=False):
        self.breakdown = HandScorer.get_hand_breakdown(self.hand.get_cards(), cut_starter_card, is_crib)
        return self.breakdown

    def get_score(self, cut_starter_card=None, is_crib=False):
        self.get_breakdown(cut_starter_card, is_crib)
        return self.breakdown.get_score()

    def get_crib_suggestion(self):
        hand = copy.deepcopy(self.hand.get_cards())

        highest_potential = -1
        crib_suggestion = None
        if (len(hand) == 5):

            for i in range(len(hand)):
                curr_card = hand[i]
                test_hand = copy.deepcopy(hand)
                test_hand.remove(curr_card)

                test_counter = Hand(test_hand)
                # print(test_counter)
                score = test_counter.get_score()
                if score > highest_potential:
                    highest_potential = score
                    crib_suggestion = curr_card

            return CardCollection([crib_suggestion])
        elif (len(hand) == 6):

            for i in range(len(hand) - 1):
                for j in range(i + 1, len(hand)):
                    card_1 = hand[i]
                    card_2 = hand[j]
                    test_hand = copy.deepcopy(hand)
                    test_hand.remove(card_1)
                    test_hand.remove(card_2)

                    test_counter = Hand(test_hand)
                    # print(test_counter)
                    score = test_counter.get_score()
                    if score > highest_potential:
                        highest_potential = score
                        crib_suggestion = [card_1, card_2]

            return CardCollection(crib_suggestion)

    def get_min_card(self):
        _cards = copy.deepcopy(self.hand.get_cards())
        cards.sort_cards(_cards)
        return _cards[0]

    def get_max_card(self):
        _cards = copy.deepcopy(self.hand.get_cards())
        cards.sort_cards(_cards)
        return _cards[-1]