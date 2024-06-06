import sys
import pygame
import game.client
from game import sprites


class Game:
    FPS = 144

    def __init__(self, connection: game.client.ClientNetwork):
        self.conn = connection
        pygame.init()
        self.screen = pygame.display.set_mode((1100, 800))
        pygame.display.set_caption('')
        self.clock = pygame.time.Clock()
        self.sprites = {self.conn.KEY: sprites.Player(self.conn.KEY, self.conn.spawn_pos)}

    def draw_bg(self):
        self.screen.fill('#5a5a5a')

    def update(self, dt, server_game):
        self.draw_bg()
        self.sprites[self.conn.KEY].input()
        for key in server_game.keys():
            if key not in self.sprites.keys():
                self.sprites[key] = game.sprites.Player(key, server_game[key]['pos'])
            else:
                if key != self.conn.KEY:
                    self.sprites[key].set_attribute(server_game[key]['pos'])

        for sprite in self.sprites.values():
            if sprite.KEY not in server_game.keys():
                del self.sprites[sprite.KEY]
            sprite.update(dt)
            sprite.draw()

    def run(self):
        run = True
        while run:
            dt = self.clock.tick(self.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.K_UP:
                    if event == pygame.K_ESCAPE:
                        run = False

            server_game = self.conn.send_attribute((self.sprites[self.conn.KEY].rect.x,
                                                    self.sprites[self.conn.KEY].rect.y))
            self.update(dt, server_game)
            pygame.display.flip()

        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    Game(game.client.ClientNetwork("86.253.205.36", 47753)).run()
