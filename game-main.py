import sys
import pygame
from game import player


class Game:
    FPS = 20

    def __init__(self):
        pygame.init()  # Initialize pygame here
        self.screen = pygame.display.set_mode((1100, 620))
        pygame.display.set_caption('')
        self.clock = pygame.time.Clock()
        self.sprites = [player.Player(self.screen, 'ffffff', (0, 0))]

    def run(self):
        run = True
        while run:
            dt = self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            self.screen.fill('green')
            self.sprites[0].input()
            for sprite in self.sprites:
                sprite.update(dt)
                sprite.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game().run()
