import sys
import pygame
from game import player


class Game:
    FPS = 20

    def __init__(self):
        pygame.init()  # Initialize pygame here
        self.screen = pygame.display.set_mode((1100, 620))
        self.clock = pygame.time.Clock()
        self.sprite = player.Player(self.screen, 'ffffff', (0, 0))

    def run(self):
        run = True
        while run:
            dt = self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False  # Set run to False to exit the loop

            if not run:
                break  # Break the loop to prevent further drawing after quitting

            self.screen.fill('green')
            self.sprite.update(dt)
            self.sprite.draw()
            pygame.display.flip()

        pygame.quit()  # Ensure pygame quits after the loop has exited
        sys.exit()


if __name__ == '__main__':
    Game().run()
