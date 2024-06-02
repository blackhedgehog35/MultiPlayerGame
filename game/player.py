import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self, screen, key):

        super.__init__()

        self.screen = screen
        self.color = f"#{key}"
        self.image = self.draw()
        self.rect = (0, 0)

    def input(self):
        pass

    def move(self):
        pass

    def draw(self):
        return pygame.draw.rect(self.screen, self.color, self.rect, width=50)
