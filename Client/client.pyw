import pygame
import socket
import pickle

buffer = 2048

class Network:
    def __init__(self):
        self.server = (self.ip, self.port) = ("localhost", 2911)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.client.settimeout(60)

        self.player = self.connect()

    def getPlayer(self):
        return self.player

    def connect(self):
        try:
            self.client.connect(self.server)
            return pickle.loads(self.client.recv(buffer))
        except: pass

    def send(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(buffer))
        except socket.error as errMsg:
            print(errMsg)
        #except: pass

size = (width,height) = (900,700)
background = (0,0,0)

window = pygame.display.set_mode(size)
pygame.display.set_caption("Better Together")


def refresh(window, playerMe, playerOthers):
    window.fill(background)
    for p in playerOthers:
        p.draw(window)
        #pygame.draw.rect(window, p.color, p.rect)
    playerMe.draw(window)
    #pygame.draw.rect(window, playerMe.color, playerMe.rect)

    pygame.display.update()


if __name__ =="__main__":
    game = True
    server = Network()
    playerMe = server.getPlayer()
    framerate = pygame.time.Clock()

    while game:
        framerate.tick(60)
        playerOthers = server.send(playerMe)
        playerMe.move()
        refresh(window, playerMe, playerOthers)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
                pygame.quit()
