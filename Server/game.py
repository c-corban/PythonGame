from player import Player
import random, os

class Game:
    def __init__(self, id):
        self.id = id
        self.ai = [True, True, True, True]
        self.pirateShips = []

        characters = ['captain-m-001-light', 'pirate-m-001-light', 'pirate-m-003-light-alt', 'pirate-m-004-light']
        for i in range(len(characters)):
            characters[i] = os.path.join('Images', 'players', '24x32', '{}.png'.format(characters[i]))

        random.shuffle(characters)
        self.players = [Player(480, 800, 48, 64, characters[0]), Player(576, 800, 48, 64, characters[1]), Player(722, 800, 48, 64, characters[2]), Player(818, 800, 48, 64, characters[3])]

        # TO DO: Pirate ship AI

        self.pirateShips.append(Player(0,0,549,549,os.path.join('Images', 'Black Sail', 'pirate_ship_00000.png')))

        for ship in self.pirateShips:
            ship.animation = None
            self.players.append(ship)


    def get_player(self, playerNumber):
        if self.ai[playerNumber] == True:
            self.ai[playerNumber] = False
            return self.players[playerNumber]
        return None


    def play(self, playerNumber, move):
        self.players[playerNumber] = move
