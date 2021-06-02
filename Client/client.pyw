import pygame, socket, pickle, os

buffer = 2048

class Network:
    def __init__(self):
        self.server = (self.ip, self.port) = ("localhost", 2911)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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


size = (width, height) = (1280, 960)

window = pygame.display.set_mode(size)
pygame.display.set_caption("Better Together")

ship = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'ocean_e_new_ship_small.png')).convert(), (width//2, height)) #(825, 750)
water1 = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'water.png')).convert(), (width//4, height))
water2 = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'water.png')).convert(), (width//4, height))

def refresh(window, playerMe, playerOthers):
    window.blit(water1, (0, 0), (0, 0, width, height))
    window.blit(water2, (width-width//4, 0), (0, 0, width, height))
    window.blit(ship, (width//4, 0),(0, 0, width, height))

    for p in playerOthers:
        p.draw(window)

    playerMe.draw(window)

    #pygame.display.update()


if __name__ =="__main__":
    game = True
    server = Network()
    playerMe = server.getPlayer()
    framerate = pygame.time.Clock()
    infoCount = 0
    while game:
        framerate.tick(60)
        playerOthers = server.send(playerMe)
        playerMe.move()
        refresh(window, playerMe, playerOthers)

        # move info
        if infoCount < 60*5: # 5 seconds
            infoCount += 1
            font = pygame.font.SysFont(None, 64)
            window.blit(font.render("Use WASD or Arrow Keys to MOVE", True, (255,255,255)), (width//4-50, height-height//12))

        # use cannon info
        """
        if (playerMe.x,playerMe.y) in [(,)]:
            font = pygame.font.SysFont(None, 64)
            window.blit(font.render("Hold SPACE to use Cannon", True, (255,255,255)), (width//4-50, height-height//12))
        """

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game = False
                pygame.quit()
