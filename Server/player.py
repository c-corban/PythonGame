import pygame, random
pygame.init()

class Player():
    def __init__(self, x, y, width, height, char):
        self.player = (self.x, self.y, self.width, self.height, self.animation) = (x, y, width, height, list([(width*frame, 2*height, width, height) for frame in range(3)])[1])
        self.char = char
        self.frame = 0
        self.velocity = 2
        self.increment = 0
        (self.maxHeight, self.maxWidth) = (960, 1280)
        (self.inventoryWood, self.inventoryCannon) = (9, 9)
        (self.cannonBallAnimationX, self.cannonBallAnimationY) = (-1000, -1000)
        (self.targetX, self.targetY) = (-1000, -1000)
    """
    def collision(self, playerImg):
        if not playerImg:
            return False

        cropped = pygame.Surface([self.width,self.height], pygame.SRCALPHA, 32)
        cropped.blit(playerImg, (0,3*self.height//4), list([(self.width*frame, 2*self.height+3*self.height//4, self.width, self.height//4) for frame in range(3)])[1])

        #obstacle = pygame.transform.scale(pygame.image.load(os.path.join('Images', 'obstacle.png')).convert_alpha(), (self.maxWidth//2, self.maxHeight))

        movingObjectMask = pygame.mask.from_surface(cropped)
        obstacleMask = pygame.mask.from_surface(obstacle)

        obstacleRectangle = obstacle.get_rect(topleft = (self.maxWidth//4, 0))
        playerRectangle = playerImg.get_rect(topleft = (self.x, self.y))
        offset = (obstacleRectangle.x - playerRectangle.x), (obstacleRectangle.y - playerRectangle.y)

        if movingObjectMask.overlap(obstacleMask, offset):
            return True
        else:
            return False
    """
    def collision(self, obstacle):
        playerImg = pygame.image.load(self.char).convert_alpha()

        cropped = pygame.Surface([self.width,self.height], pygame.SRCALPHA, 32)
        cropped.blit(playerImg, (0,3*self.height//4), list([(self.width*frame, 2*self.height+3*self.height//4, self.width, self.height//4) for frame in range(3)])[1])

        movingObjectMask = pygame.mask.from_surface(cropped)
        obstacleMask = pygame.mask.from_surface(obstacle)

        obstacleRectangle = obstacle.get_rect(topleft = (self.maxWidth//4, 0))
        playerRectangle = playerImg.get_rect(topleft = (self.x, self.y))
        offset = (obstacleRectangle.x - playerRectangle.x), (obstacleRectangle.y - playerRectangle.y)

        return movingObjectMask.overlap(obstacleMask, offset)

    def move(self, obstacle):

        if self.frame >= 56:
            self.increment =- 3
        if self.frame <= 0:
            self.increment = 3
            self.direction = random.randrange(5)
        self.frame += self.increment

        standing = True

        if self.direction == 1 and self.y + self.velocity > 0:
            standing = False
            self.y -= self.velocity
            self.animation = list([(self.width*frame, 0, self.width, self.height) for frame in range(3)])[self.frame//20]
            if self.collision(obstacle):
            #if self.collision(playerImg, obstacle):
                self.y += self.velocity

        if  self.direction == 2 and self.x + self.velocity > 0:
            standing = False
            self.x -= self.velocity
            self.animation = list([(self.width*frame, 3*self.height, self.width, self.height) for frame in range(3)])[self.frame//20]
            if self.collision(obstacle):
            #if self.collision(playerImg):
                self.x += self.velocity

        if  self.direction == 3 and self.y + self.height - self.velocity < self.maxHeight:
            standing = False
            self.y += self.velocity
            self.animation = list([(self.width*frame, 2*self.height, self.width, self.height) for frame in range(3)])[self.frame//20]
            if self.collision(obstacle):
            #if self.collision(playerImg):
                self.y -= self.velocity

        if  self.direction == 4 and self.x + self.width - self.velocity < self.maxWidth:
            standing = False
            self.x += self.velocity
            self.animation = list([(self.width*frame, self.height, self.width, self.height) for frame in range(3)])[self.frame//20]
            if self.collision(obstacle):
            #if self.collision(playerImg):
                self.x -= self.velocity

        if standing:
            if self.animation[1] == 0:
                self.animation = list([(self.width*frame, 0, self.width, self.height) for frame in range(3)])[1]

            if self.animation[1] == 3*self.height:
                self.animation = list([(self.width*frame, 3*self.height, self.width, self.height) for frame in range(3)])[1]

            if self.animation[1] == 2*self.height:
                self.animation = list([(self.width*frame, 2*self.height, self.width, self.height) for frame in range(3)])[1]

            if self.animation[1] == self.height:
                self.animation = list([(self.width*frame, self.height, self.width, self.height) for frame in range(3)])[1]
