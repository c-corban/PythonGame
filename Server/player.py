import pygame

class Player():
    def __init__(self, x, y, width, height, char):
        self.player = (self.x, self.y, self.width, self.height, self.animation) = (x, y, width, height, list([(24*frame,0,24,32) for frame in range(3)])[1])
        self.char = char
        self.frame = 0
        self.velocity = 2
        self.maxHeight = 960
        self.maxWidth = 1280
        self.increment=0


    def draw(self, window):

        window.blit(pygame.image.load('../Img/players/24x32/{}.png'.format(self.char)),(self.x,self.y),self.animation)


    def move(self):

        keys = pygame.key.get_pressed()

        if self.frame>=56:
            self.increment=-3

        if self.frame<=0:
            self.increment=3

        self.frame+=self.increment


        if (keys[ord('w')] or keys[pygame.K_UP]) and self.y + self.velocity > 0:
            self.y -= self.velocity
            self.animation=list([(24*frame,0,24,32) for frame in range(3)])[self.frame//20]

        if (keys[ord('a')] or keys[pygame.K_LEFT]) and self.x + self.velocity > 0:
            self.x -= self.velocity
            self.animation=list([(24*frame,96,24,32) for frame in range(3)])[self.frame//20]

        if (keys[ord('s')] or keys[pygame.K_DOWN]) and self.y + self.height - self.velocity < self.maxHeight:
            self.y += self.velocity
            self.animation=list([(24*frame,64,24,32) for frame in range(3)])[self.frame//20]

        if (keys[ord('d')] or keys[pygame.K_RIGHT]) and self.x + self.width - self.velocity < self.maxWidth:
            self.x += self.velocity
            self.animation=list([(24*frame,32,24,32) for frame in range(3)])[self.frame//20]

        self.update()


    def update(self):
        self.player = (self.x, self.y, self.width, self.height, self.animation)
