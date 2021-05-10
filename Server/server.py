import socket
from _thread import *
import pickle, random
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
idCount = 0

def aiMove(gameId):
    for i in range(len(games[gameId].ai)):
        if games[gameId].ai[i]:
            direction = random.randrange(1,5)

            if direction == 1 and games[gameId].players[i].y + games[gameId].players[i].velocity > 0:
                games[gameId].players[i].y -= games[gameId].players[i].velocity

            if direction == 2 and games[gameId].players[i].x + games[gameId].players[i].velocity > 0:
                games[gameId].players[i].x -= games[gameId].players[i].velocity

            if direction == 3 and games[gameId].players[i].y + games[gameId].players[i].height - games[gameId].players[i].velocity < games[gameId].players[i].maxHeight:
                games[gameId].players[i].y += games[gameId].players[i].velocity

            if direction == 4 and games[gameId].players[i].x + games[gameId].players[i].width - games[gameId].players[i].velocity < games[gameId].players[i].maxWidth:
                games[gameId].players[i].x += games[gameId].players[i].velocity

            games[gameId].players[i].player = (games[gameId].players[i].x, games[gameId].players[i].y, games[gameId].players[i].width, games[gameId].players[i].height)


def clientThread(connection, playerNumber, gameId):
    global idCount

    # Send player object
    connection.send(pickle.dumps(games[gameId].players[playerNumber]))
    reply = []
    while True:
        try:
            # Get player move
            data = pickle.loads(connection.recv(buffer))
            if not data: break

            #else:
            # Reply others move
            games[gameId].players[playerNumber] = data
            aiMove(gameId)
            for i in range(len(games[gameId].players)):
                if i != playerNumber:
                    reply.append(games[gameId].players[i])

                #print("Received: ", data)
                #print("Sending : ", reply)

            connection.sendall(pickle.dumps(reply))
            reply = []

        except: break

    print("Lost connection",address)
    games[gameId].ai[playerNumber] = True
    #print((gameId,games[gameId].ai))

    if False not in games[gameId].ai:
        try:
            del games[gameId]
            print("Closing Game", gameId)
        except:
            pass

    idCount -= 1
    connection.close()


while True:
    connection, address = s.accept()
    print("Connected to:", address)

    playerNumber = idCount % 4
    idCount += 1
    gameId = (idCount - 1) // 4

    if idCount % 4 == 1 and gameId not in games:
        games[gameId] = Game(gameId)
        #print((gameId,games[gameId].ai))
        print("Creating a new game.",gameId)

    else:
        for game in range(gameId):
            for aiControled in range(len(games[game].ai)):
                if games[game].ai[aiControled]:
                    playerNumber = aiControled
                    gameId = game
                    break
        print("Joining game", gameId)

        games[gameId].ai[playerNumber] = False
        #print((gameId,games[gameId].ai))

    #print(playerNumber, gameId)
    start_new_thread(clientThread, (connection, playerNumber, gameId))
