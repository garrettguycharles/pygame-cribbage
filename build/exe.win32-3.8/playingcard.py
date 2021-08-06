class suits:
    spade = "spade"
    heart = "heart"
    club = "club"
    diamond = "diamond"

    SUITS = {
        0: spade,
        1: heart,
        2: club,
        3: diamond
    }

    def __init__(self):
        pass

    def get_symbol(suit):
        if suit == suits.spade:
            return '\u2660'
        elif suit == suits.heart:
            return '\u2661'
        elif suit == suits.club:
            return '\u2663'
        elif suit == suits.diamond:
            return '\u2662'
        else:
            raise Exception("requested suit does not exist: " + suit)

    def get_number(suit):
        for key in suits.SUITS:
            if suits.SUITS[key] == suit:
                return key
        raise Exception("Invalid suit: " + suit)

class cards:
    ACE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13

    CARDS = {
        1: "A",
        2: "2",
        3: "3",
        4: "4",
        5: "5",
        6: "6",
        7: "7",
        8: "8",
        9: "9",
        10: "10",
        11: "J",
        12: "Q",
        13: "K"
    }

    @staticmethod
    def sort_cards(cards_list):
        sorted = False

        while not (sorted):
            sorted = True

            for i in range(len(cards_list) - 1):
                if (cards_list[i] > cards_list[i + 1]):
                    cards.swap(cards_list, i, i + 1)
                    sorted = False

    @staticmethod
    def swap(listname, i, j):
        temp = listname[i]
        listname[i] = listname[j]
        listname[j] = temp

    @staticmethod
    def flip_list(in_list):
        toReturn = []
        for i in reversed(range(len(in_list))):
            toReturn.append(in_list[i])
        in_list = toReturn

    @staticmethod
    def sum_card_value(in_cards):
        sum = 0;
        for card in in_cards:
            sum += card.get_value()
        return sum

    @staticmethod
    def are_same_number(to_check):
        if (len(to_check) < 2):
            return False
        toReturn = True
        for card in to_check:
            if not card.is_pair(to_check[0]):
                toReturn = False
                break
        return toReturn

    @staticmethod
    def get_value(card_num):
        if (card_num < 0 or card_num > cards.KING):
            raise Exception("Card number is out of range: " + str(card_num))

        if (card_num >= 10):
            return 10

        return card_num

    def __init__(self):
        pass