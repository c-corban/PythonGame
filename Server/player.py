import pygame

class Player():
    def __init__(self, x, y, width, height, color):
        self.player = (self.x, self.y, self.width, self.height) = (x, y, width, height)
        self.color = color
        self.velocity = 4
        self.maxHeight = 700
        self.maxWidth = 900

    def draw(self, window):
        pygame.draw.rect(window, self.color, self.player)

    def move(self):
        keys = pygame.key.get_pressed()

        if (keys[ord('w')] or keys[pygame.K_UP]) and self.y + self.velocity > 0:
            self.y -= self.velocity

        if (keys[ord('a')] or keys[pygame.K_LEFT]) and self.x + self.velocity > 0:
            self.x -= self.velocity

        if (keys[ord('s')] or keys[pygame.K_DOWN]) and self.y + self.height - self.velocity < self.maxHeight:
            self.y += self.velocity

        if (keys[ord('d')] or keys[pygame.K_RIGHT]) and self.x + self.width - self.velocity < self.maxWidth:
            self.x += self.velocity

        self.update()

    def update(self):
        self.player = (self.x, self.y, self.width, self.height)
