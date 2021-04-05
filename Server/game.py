from player import Player

class Game:
    def __init__(self, id):
        self.id = id
        self.ai = [False,True,True,True]
        self.players = [Player(300,400,48,64,(255,0,0)), Player(358,400, 48,64, (0,0,255)), Player(416,400, 48,64, (0,255,0)), Player(474,400, 48,64, (255,255,0))]
        #self.players = [1,2,3,4]

    def get_player(self, playerNumber):
        if self.ai[playerNumber] == True:
            self.ai[playerNumber] = False
            return self.players[playerNumber]
        return None


    def play(self, playerNumber, move):
        self.players[playerNumber] = move
