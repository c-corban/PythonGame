from player import Player
import random, os

class Game:
    def __init__(self, id):
        self.id = id
        self.ai = [True, True, True, True]
        self.pirateShips = []
        #(self.playerWidth,self.playerHeight) = 24, 32
        (self.playerWidth,self.playerHeight) = 36, 48
        #(self.playerWidth,self.playerHeight) = 48, 64

        characters = ['captain-m-001-light', 'pirate-m-001-light', 'pirate-m-003-light-alt', 'pirate-m-004-light']
        for i in range(len(characters)):
            characters[i] = os.path.join('Images', 'players', '{}x{}'.format(self.playerWidth,self.playerHeight), '{}.png'.format(characters[i]))

        random.shuffle(characters)
        self.players = [Player(480, 780, self.playerWidth, self.playerHeight, characters[0]), Player(576, 780, self.playerWidth, self.playerHeight, characters[1]), Player(722, 780, self.playerWidth, self.playerHeight, characters[2]), Player(818, 780, self.playerWidth, self.playerHeight, characters[3])]

        self.pirateShips.append(Player(-300,-300,549,549,os.path.join('Images', 'Black Sail', 'pirate_ship_00000.png')))
        self.pirateShips.append(Player(1050,750,549,549,os.path.join('Images', 'Black Sail', 'pirate_ship_00000.png')))

        for ship in self.pirateShips:
            ship.maxWidth = 1050
            ship.maxHeight = 750
            ship.animation = None
            self.players.append(ship)


    def get_player(self, playerNumber):
        if self.ai[playerNumber] == True:
            self.ai[playerNumber] = False
            return self.players[playerNumber]
        return None


    def play(self, playerNumber, move):
        self.players[playerNumber] = move
