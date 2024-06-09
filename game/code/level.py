import sys
import pygame
from client import ClientNetwork
from sprites import Player
from config import ConfigFile


class Level:
    FPS = ConfigFile().get('DEFAULT', 'FPS')

    def __init__(self, screen, connection: ClientNetwork):
        self.conn = connection
        pygame.init()
        self.screen = screen
        pygame.display.set_caption('')
        self.clock = pygame.time.Clock()
        self.sprites = {self.conn.KEY: Player(self.conn.KEY, self.conn.spawn_pos)}

    def draw_bg(self):
        self.screen.fill('#5a5a5a')

    def update(self, dt, server_game):
        self.draw_bg()
        self.sprites[self.conn.KEY].input()
        for key in server_game.keys():
            if key not in self.sprites.keys():
                self.sprites[key] = Player(key, server_game[key]['pos'])
            else:
                if key != self.conn.KEY:
                    self.sprites[key].set_attribute(server_game[key]['pos'])
        for sprite in list(self.sprites.values()):
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
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_a]:
                        run = False

            server_game = self.conn.send_attribute((self.sprites[self.conn.KEY].rect.x,
                                                    self.sprites[self.conn.KEY].rect.y))
            self.update(dt, server_game)
            pygame.display.flip()


if __name__ == '__main__':
    host, port = ConfigFile().get_host()
    Level(pygame.display.set_mode(ConfigFile().get_screen_size()), ClientNetwork(host, port)).run()
