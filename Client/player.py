import pygame, os

class Player():
    def __init__(self, x, y, width, height, char):
        self.player = (self.x, self.y, self.width, self.height, self.animation) = (x, y, width, height, list([(24*frame, 0, 24, 32) for frame in range(3)])[1])
        self.char = char
        self.frame = 0
        self.velocity = 2
        self.maxHeight = 960
        self.maxWidth = 1280
        self.increment = 0
        

    def collision(self, player_img):
        if not player_img:
            return False

        cropped = pygame.Surface([24,32], pygame.SRCALPHA, 32)
        cropped.blit(player_img,(0,3*32//4),list([(24*frame, 64+3*32//4, 24, 32//4) for frame in range(3)])[1])
        aux = cropped

        obstacle = pygame.transform.scale(pygame.image.load(os.path.join('..', 'Img', 'obstacle.png')).convert_alpha(),(self.maxWidth//2, self.maxHeight))

        moving_object_mask = pygame.mask.from_surface(aux)
        obstacle_mask = pygame.mask.from_surface(obstacle)

        obstacle_rect = obstacle.get_rect(topleft = (self.maxWidth//4, 0))
        player_rect = player_img.get_rect(topleft = (self.x, self.y))
        offset = (obstacle_rect.x - player_rect.x), (obstacle_rect.y - player_rect.y)

        if moving_object_mask.overlap(obstacle_mask, offset):
            return True
        else:
            return False


    def draw(self, window):

        player_img = pygame.image.load(os.path.join('..', 'Img', 'players', '24x32', '{}.png'.format(self.char))).convert_alpha()

        window.blit(player_img,(self.x,self.y),self.animation)


    def move(self):
        player_img = pygame.image.load(os.path.join('..', 'Img', 'players', '24x32', '{}.png'.format(self.char))).convert_alpha()

        keys = pygame.key.get_pressed()
        if self.frame >= 56:
            self.increment =- 3
        if self.frame <= 0:
            self.increment = 3
        self.frame += self.increment
        if (keys[ord('w')] or keys[pygame.K_UP]) and self.y + self.velocity > 0:
            self.y -= self.velocity
            if not self.collision(player_img):
                self.animation=list([(24*frame,0,24,32) for frame in range(3)])[self.frame//20]
            else:
                self.y += self.velocity

        if (keys[ord('a')] or keys[pygame.K_LEFT]) and self.x + self.velocity > 0:
            self.x -= self.velocity
            if not self.collision(player_img):
                self.animation=list([(24*frame,96,24,32) for frame in range(3)])[self.frame//20]
            else:
                self.x += self.velocity

        if (keys[ord('s')] or keys[pygame.K_DOWN]) and self.y + self.height - self.velocity < self.maxHeight:
            self.y += self.velocity
            if not self.collision(player_img):
                self.animation=list([(24*frame,64,24,32) for frame in range(3)])[self.frame//20]
            else:
                self.y -= self.velocity

        if (keys[ord('d')] or keys[pygame.K_RIGHT]) and self.x + self.width - self.velocity < self.maxWidth:
            self.x += self.velocity
            if not self.collision(player_img):
                self.animation=list([(24*frame,32,24,32) for frame in range(3)])[self.frame//20]
            else:
                self.x -= self.velocity

        #self.update()


    def update(self):
        self.player = (self.x, self.y, self.width, self.height, self.animation)
