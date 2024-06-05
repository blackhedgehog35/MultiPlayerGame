import sys

import pygame
from game import player


class Game:
    FPS = 20

    def __init__(self):
        self.screen = pygame.display.set_mode((1100, 620))
        self.clock = pygame.time.Clock()
        self.sprite = player.Player(self.screen, 'ffffff')
        pygame.init()

    def run(self):
        run = True
        while run:
            dt = self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            self.screen.fill('green')
            self.sprite.move()
            self.sprite.update()
            self.sprite.draw()

            pygame.display.flip()
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()


