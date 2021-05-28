from player import Player
import random

class Game:
    def __init__(self, id):
        self.id = id
        self.ai = [True, True, True, True]

        characters=['captain-m-001-light', 'pirate-m-001-light', 'pirate-m-003-light-alt', 'pirate-m-004-light']
        random.shuffle(characters)
        self.players = [Player(480, 800, 48, 64, characters[0]), Player(576, 800, 48, 64, characters[1]), Player(722, 800, 48, 64, characters[2]), Player(818, 800, 48, 64, characters[3])]


    def get_player(self, playerNumber):
        if self.ai[playerNumber] == True:
            self.ai[playerNumber] = False
            return self.players[playerNumber]
        return None


    def play(self, playerNumber, move):
        self.players[playerNumber] = move
