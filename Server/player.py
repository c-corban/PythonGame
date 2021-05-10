import pygame

class Player():
    def __init__(self, x, y, width, height, char):
        self.player = (self.x, self.y, self.width, self.height, self.animation) = (x, y, width, height, list([(48*frame,0,48,64) for frame in range(3)])[1])
        self.char = char
        self.frame = 0
        self.velocity = 3
        self.maxHeight = 700
        self.maxWidth = 900
        #self.animation=list([(48*frame,0,48,64) for frame in range(3)])[1]

    def draw(self, window):
        #pygame.draw.rect(window, self.char, self.player)

        #self.animation=list([(48*frame,128,48,64) for frame in range(3)])
        #window.blit(pygame.image.load('../Img/players/48x64_scale/captain-m-001-light.png'),(self.x,self.y),(0,128,48,64))

        #for i in range(60):
        window.blit(pygame.image.load('../Img/players/48x64_scale/{}.png'.format(self.char)),(self.x,self.y),self.animation)
        #captain-m-001-light.png
    def move(self):
        keys = pygame.key.get_pressed()
        if self.frame>=59:
            self.frame=0
        self.frame+=1
        if (keys[ord('w')] or keys[pygame.K_UP]) and self.y + self.velocity > 0:
            self.y -= self.velocity
            self.animation=list([(48*frame,0,48,64) for frame in range(3)])[self.frame//20]

        if (keys[ord('a')] or keys[pygame.K_LEFT]) and self.x + self.velocity > 0:
            self.x -= self.velocity
            self.animation=list([(48*frame,192,48,64) for frame in range(3)])[self.frame//20]

        if (keys[ord('s')] or keys[pygame.K_DOWN]) and self.y + self.height - self.velocity < self.maxHeight:
            self.y += self.velocity
            self.animation=list([(48*frame,128,48,64) for frame in range(3)])[self.frame//20]

        if (keys[ord('d')] or keys[pygame.K_RIGHT]) and self.x + self.width - self.velocity < self.maxWidth:
            self.x += self.velocity
            self.animation=list([(48*frame,64,48,64) for frame in range(3)])[self.frame//20]
        self.update()

    def update(self):
        self.player = (self.x, self.y, self.width, self.height, self.animation)
