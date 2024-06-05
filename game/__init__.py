import pygame


class Game:
    WIDTH = 1100
    HEIGHT = 750
    FPS = 15

    def __init__(self):
        pygame.display.set_caption('')
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        while running:
            _dt = self.clock.tick(self.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.K_UP:
                    if event == pygame.K_ESCAPE:
                        running = False

            self.screen.fill((190, 240, 40))
            pygame.display.update()


if __name__ == '__main__':
    Game().run()
