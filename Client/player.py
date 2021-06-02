import pygame, os
pygame.init()

class Player():
    def __init__(self, x, y, width, height, char):
        self.player = (self.x, self.y, self.width, self.height, self.animation) = (x, y, width, height, list([(24*frame, 64, 24, 32) for frame in range(3)])[1])
        self.char = char
        self.frame = 0
        self.velocity = 2
        self.maxHeight = 960
        self.maxWidth = 1280
        self.increment = 0
        self.inventoryWood = 9
        self.inventoryCannon = 9


    def collision(self, playerImg):
        if not playerImg:
            return False

        cropped = pygame.Surface([24,32], pygame.SRCALPHA, 32)
        cropped.blit(playerImg, (0,3*32//4), list([(24*frame, 64+3*32//4, 24, 32//4) for frame in range(3)])[1])

        obstacle = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'obstacle.png')).convert_alpha(), (self.maxWidth//2, self.maxHeight))

        movingObjectMask = pygame.mask.from_surface(cropped)
        obstacleMask = pygame.mask.from_surface(obstacle)

        obstacleRectangle = obstacle.get_rect(topleft = (self.maxWidth//4, 0))
        playerRectangle = playerImg.get_rect(topleft = (self.x, self.y))
        offset = (obstacleRectangle.x - playerRectangle.x), (obstacleRectangle.y - playerRectangle.y)

        if movingObjectMask.overlap(obstacleMask, offset):
            return True
        else:
            return False


    def draw(self, window):

        playerImg = pygame.image.load(self.char).convert_alpha()

        window.blit(playerImg,(self.x,self.y),self.animation)

        font = pygame.font.SysFont(None, 64)

        woodSurface = pygame.Surface([40,40], pygame.SRCALPHA, 32)
        cannonSurface = pygame.Surface([40,40], pygame.SRCALPHA, 32)


        woodSurface.blit(pygame.image.load(os.path.join('Images', 'wood plank.png')).convert_alpha(), (0, 0))
        cannonSurface.blit(pygame.image.load(os.path.join('Images', 'cannonball.png')).convert_alpha(), (0, 0))


        window.blit(woodSurface, (10,20))
        window.blit(cannonSurface, (10,70))

        window.blit(font.render("{}".format(self.inventoryWood), True, (0,0,0)), (60, 20))
        window.blit(font.render("{}".format(self.inventoryCannon), True, (0,0,0)), (60, 70))

    def move(self):
        playerImg = pygame.image.load(self.char).convert_alpha()

        keys = pygame.key.get_pressed()
        if self.frame >= 56:
            self.increment =- 3
        if self.frame <= 0:
            self.increment = 3
        self.frame += self.increment

        standing = True

        if (keys[ord('w')] or keys[pygame.K_UP]) and self.y + self.velocity > 0:
            standing = False
            self.y -= self.velocity
            self.animation = list([(24*frame, 0, 24, 32) for frame in range(3)])[self.frame//20]
            if self.collision(playerImg):
                self.y += self.velocity

        if (keys[ord('a')] or keys[pygame.K_LEFT]) and self.x + self.velocity > 0:
            standing = False
            self.x -= self.velocity
            self.animation = list([(24*frame, 96, 24, 32) for frame in range(3)])[self.frame//20]
            if self.collision(playerImg):
                self.x += self.velocity

        if (keys[ord('s')] or keys[pygame.K_DOWN]) and self.y + self.height - self.velocity < self.maxHeight:
            standing = False
            self.y += self.velocity
            self.animation = list([(24*frame, 64, 24, 32) for frame in range(3)])[self.frame//20]
            if self.collision(playerImg):
                self.y -= self.velocity

        if (keys[ord('d')] or keys[pygame.K_RIGHT]) and self.x + self.width - self.velocity < self.maxWidth:
            standing = False
            self.x += self.velocity
            self.animation = list([(24*frame, 32, 24, 32) for frame in range(3)])[self.frame//20]
            if self.collision(playerImg):
                self.x -= self.velocity

        if standing:
            if self.animation[1] == 0:
                self.animation = list([(24*frame, 0, 24, 32) for frame in range(3)])[1]

            if self.animation[1] == 96:
                self.animation = list([(24*frame, 96, 24, 32) for frame in range(3)])[1]

            if self.animation[1] == 64:
                self.animation = list([(24*frame, 64, 24, 32) for frame in range(3)])[1]

            if self.animation[1] == 32:
                self.animation = list([(24*frame, 32, 24, 32) for frame in range(3)])[1]

        #self.update()


    def update(self):
        self.player = (self.x, self.y, self.width, self.height, self.animation)
