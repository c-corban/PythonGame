import socket, pickle, random, os
from _thread import *
from game import Game

server = (ip, port) = ("localhost", 2911)

buffer = 2048

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind(server)
except socket.error as errMsg:
    str(errMsg)

s.listen(1)
print("Waiting for connections")

games = {}


def aiMove(gameId):
    for i in range(len(games[gameId].ai)):
        if games[gameId].ai[i]:
            games[gameId].players[i].move()


def shipAi(gameId):
    for i in range(len(games[gameId].pirateShips)):
        for j in range(4):
            #if games[gameId].players[j].targetX in  range(games[gameId].pirateShips[i].x, games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].width) and games[gameId].players[j].targetY in  range(games[gameId].pirateShips[i].y, games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].height):

            if games[gameId].players[j].cannonBallAnimationX in  range(games[gameId].pirateShips[i].x, games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].width) and games[gameId].players[j].cannonBallAnimationY in  range(games[gameId].pirateShips[i].y, games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].height):
                (games[gameId].pirateShips[i].x,games[gameId].pirateShips[i].y)=(1280//2,-600)
                
        if not random.randrange(60) % 20:
            games[gameId].pirateShips[i].increment = random.randrange(-1,2)
        elif random.randrange(60) % 20:
            games[gameId].pirateShips[i].increment = 0

        if games[gameId].pirateShips[i].frame == 0 and games[gameId].pirateShips[i].increment == -1:
            games[gameId].pirateShips[i].frame = 15
        elif games[gameId].pirateShips[i].frame == 15 and games[gameId].pirateShips[i].increment == 1:
            games[gameId].pirateShips[i].frame = 0
        else:
            games[gameId].pirateShips[i].frame += games[gameId].pirateShips[i].increment

        games[gameId].pirateShips[i].char = os.path.join('Images', 'Black Sail', 'pirate_ship_{}0000.png'.format(games[gameId].pirateShips[i].frame))
        #games[gameId].pirateShips[i].char = os.path.join('Images', 'Black Sail before compress', 'pirate_ship_{}0000.png'.format(games[gameId].pirateShips[i].frame))

        if not random.randrange(60) % 12:
            break

        shipMinWidth = -50 #-100 #100
        shipMaxWidth = 900 #+100 #700
        shipMinHeight = -300 #-100 #-300
        shipMaxHeight = 900 #+100 #900

        # down
        if games[gameId].pirateShips[i].frame == 0:

            if games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity < games[gameId].pirateShips[i].maxHeight and ((games[gameId].pirateShips[i].x < shipMinWidth or games[gameId].pirateShips[i].x > shipMaxWidth) or (games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity < shipMinHeight or games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity > shipMaxHeight)):
                games[gameId].pirateShips[i].y += games[gameId].pirateShips[i].velocity

        # down right
        if games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity < games[gameId].pirateShips[i].maxHeight and games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity < games[gameId].pirateShips[i].maxWidth and ((games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity < shipMinWidth or games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity > shipMaxWidth) or (games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity < shipMinHeight or games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity > shipMaxHeight)):
            if games[gameId].pirateShips[i].frame == 1:
                games[gameId].pirateShips[i].x += games[gameId].pirateShips[i].velocity//2
                games[gameId].pirateShips[i].y += games[gameId].pirateShips[i].velocity

            if games[gameId].pirateShips[i].frame == 2:
                games[gameId].pirateShips[i].x += games[gameId].pirateShips[i].velocity
                games[gameId].pirateShips[i].y += games[gameId].pirateShips[i].velocity

            if games[gameId].pirateShips[i].frame == 3:
                games[gameId].pirateShips[i].x += games[gameId].pirateShips[i].velocity
                games[gameId].pirateShips[i].y += games[gameId].pirateShips[i].velocity//2
        """else: # if it hits wall, turn around
            if games[gameId].pirateShips[i].frame == 1:
                games[gameId].pirateShips[i].frame = 9
            if games[gameId].pirateShips[i].frame == 2:
                games[gameId].pirateShips[i].frame = 10
            if games[gameId].pirateShips[i].frame == 3:
                games[gameId].pirateShips[i].frame = 11"""

        # right
        if games[gameId].pirateShips[i].frame == 4:
            if games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity < games[gameId].pirateShips[i].maxWidth and ((games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity < shipMinWidth or games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity > shipMaxWidth) or (games[gameId].pirateShips[i].y < shipMinHeight or games[gameId].pirateShips[i].y > shipMaxHeight)):
                games[gameId].pirateShips[i].x += games[gameId].pirateShips[i].velocity

        # right up
        if games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity < games[gameId].pirateShips[i].maxWidth and games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity > shipMinHeight and ((games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity < shipMinWidth or games[gameId].pirateShips[i].x + games[gameId].pirateShips[i].velocity > shipMaxWidth) or (games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity < shipMinHeight or games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity > shipMaxHeight)):
            if games[gameId].pirateShips[i].frame == 5:
                games[gameId].pirateShips[i].x += games[gameId].pirateShips[i].velocity
                games[gameId].pirateShips[i].y -= games[gameId].pirateShips[i].velocity//2

            if games[gameId].pirateShips[i].frame == 6:
                games[gameId].pirateShips[i].x += games[gameId].pirateShips[i].velocity
                games[gameId].pirateShips[i].y -= games[gameId].pirateShips[i].velocity

            if games[gameId].pirateShips[i].frame == 7:
                games[gameId].pirateShips[i].x += games[gameId].pirateShips[i].velocity//2
                games[gameId].pirateShips[i].y -= games[gameId].pirateShips[i].velocity
        """else: # if it hits wall, turn around
            if games[gameId].pirateShips[i].frame == 5:
                games[gameId].pirateShips[i].frame = 13
            if games[gameId].pirateShips[i].frame == 6:
                games[gameId].pirateShips[i].frame = 14
            if games[gameId].pirateShips[i].frame == 7:
                games[gameId].pirateShips[i].frame = 15"""

        # up
        if games[gameId].pirateShips[i].frame == 8:
            if games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity > shipMinHeight and ((games[gameId].pirateShips[i].x < shipMinWidth or games[gameId].pirateShips[i].x > shipMaxWidth) or (games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity < shipMinHeight or games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity > shipMaxHeight)):
                games[gameId].pirateShips[i].y -= games[gameId].pirateShips[i].velocity

        # up left
        if games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity > shipMinHeight and games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity > shipMinHeight and ((games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity < shipMinWidth or games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity > shipMaxWidth) or (games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity < shipMinHeight or games[gameId].pirateShips[i].y - games[gameId].pirateShips[i].velocity > shipMaxHeight)):
            if games[gameId].pirateShips[i].frame == 9:
                games[gameId].pirateShips[i].x -= games[gameId].pirateShips[i].velocity//2
                games[gameId].pirateShips[i].y -= games[gameId].pirateShips[i].velocity

            if games[gameId].pirateShips[i].frame == 10:
                games[gameId].pirateShips[i].x -= games[gameId].pirateShips[i].velocity
                games[gameId].pirateShips[i].y -= games[gameId].pirateShips[i].velocity

            if games[gameId].pirateShips[i].frame == 11:
                games[gameId].pirateShips[i].x -= games[gameId].pirateShips[i].velocity
                games[gameId].pirateShips[i].y -= games[gameId].pirateShips[i].velocity//2
        """else: # if it hits wall, turn around
            if games[gameId].pirateShips[i].frame == 9:
                games[gameId].pirateShips[i].frame = 1
            if games[gameId].pirateShips[i].frame == 10:
                games[gameId].pirateShips[i].frame = 2
            if games[gameId].pirateShips[i].frame == 11:
                games[gameId].pirateShips[i].frame = 3"""

        # left
        if games[gameId].pirateShips[i].frame == 12:
            if games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity > shipMinHeight and ((games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity < shipMinWidth or games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity > shipMaxWidth) or (games[gameId].pirateShips[i].y < shipMinHeight or games[gameId].pirateShips[i].y > shipMaxHeight)):
                games[gameId].pirateShips[i].x -= games[gameId].pirateShips[i].velocity


        # left down
        if games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity > shipMinHeight and games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity < games[gameId].pirateShips[i].maxHeight and ((games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity < shipMinWidth or games[gameId].pirateShips[i].x - games[gameId].pirateShips[i].velocity > shipMaxWidth) or ( games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity < shipMinHeight or games[gameId].pirateShips[i].y + games[gameId].pirateShips[i].velocity > shipMaxHeight)):
            if games[gameId].pirateShips[i].frame == 13:
                    games[gameId].pirateShips[i].x -= games[gameId].pirateShips[i].velocity
                    games[gameId].pirateShips[i].y += games[gameId].pirateShips[i].velocity//2
            if games[gameId].pirateShips[i].frame == 14:
                    games[gameId].pirateShips[i].x -= games[gameId].pirateShips[i].velocity
                    games[gameId].pirateShips[i].y += games[gameId].pirateShips[i].velocity
            if games[gameId].pirateShips[i].frame == 15:
                    games[gameId].pirateShips[i].x -= games[gameId].pirateShips[i].velocity//2
                    games[gameId].pirateShips[i].y += games[gameId].pirateShips[i].velocity
        """else: # if it hits wall, turn around
            if games[gameId].pirateShips[i].frame == 13:
                games[gameId].pirateShips[i].frame = 5
            if games[gameId].pirateShips[i].frame == 14:
                games[gameId].pirateShips[i].frame = 6
            if games[gameId].pirateShips[i].frame == 15:
                games[gameId].pirateShips[i].frame = 7"""

def clientThread(connection, playerNumber, gameId):

    # Send player object
    connection.send(pickle.dumps(games[gameId].players[playerNumber]))
    reply = []
    while True:
        try:
            # Get player move
            data = pickle.loads(connection.recv(buffer))
            if not data: break

            # Reply others move
            games[gameId].players[playerNumber] = data
            aiMove(gameId) # work in progress
            shipAi(gameId)
            for i in range(len(games[gameId].players)):
                if i != playerNumber:
                    reply.append(games[gameId].players[i])

                #print("Received: ", data)
                #print("Sending : ", reply)

            connection.sendall(pickle.dumps(reply))
            reply = []

        except: break

    print("Lost connection", address)
    games[gameId].ai[playerNumber] = True

    if False not in games[gameId].ai:
        try:
            del games[gameId]
            print("Closing Game", gameId)

        except:
            pass

    connection.close()


while True:
    connection, address = s.accept()
    print("Connected to:", address)

    found = False

    # Search for a game to join
    for game in games:
        if not found:
            for aiControlled in range(len(games[game].ai)):
                if games[game].ai[aiControlled]:
                    found = True
                    playerNumber = aiControlled
                    gameId = game

                    print("Joining game", gameId)

                    games[gameId].ai[playerNumber] = False
                    break

    # Reopen a game
    if not found:
        if games:
            recentlyClosed = None
            maxGameId = max(games.keys())
            gameFound = False
            for recentlyClosed in range(1, maxGameId+1):
                if recentlyClosed-1 not in games:
                    gameFound = True
                    gameId = recentlyClosed-1
                    break

            # Create a new game
            if not gameFound:
                gameId = maxGameId + 1
        else:
            gameId = 0

        print("Creating a new game.", gameId)

        games[gameId] = Game(gameId)
        playerNumber = 0
        games[gameId].ai[0] = False

    start_new_thread(clientThread, (connection, playerNumber, gameId))
