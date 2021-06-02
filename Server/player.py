#import pygame

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
