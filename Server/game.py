from player import Player

class Game:
    def __init__(self, id):
        self.id = id
        self.ai = [False,True,True,True]
        self.players = [Player(300,400,48,64,'captain-m-001-light'), Player(358,400, 48,64, 'pirate-m-001-light'), Player(416,400, 48,64, 'pirate-m-003-light-alt'), Player(474,400, 48,64, 'pirate-m-004-light')]
        #self.players = [1,2,3,4]

    def get_player(self, playerNumber):
        if self.ai[playerNumber] == True:
            self.ai[playerNumber] = False
            return self.players[playerNumber]
        return None


    def play(self, playerNumber, move):
        self.players[playerNumber] = move
