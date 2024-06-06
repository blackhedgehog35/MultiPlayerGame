import sys
import pygame
import client
import sprites


class Game:
    FPS = 60

    def __init__(self, connection: client.ClientNetwork):
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
                self.sprites[key] = sprites.Player(key, server_game[key]['pos'])
            else:
                if key != self.conn.KEY:
                    self.sprites[key].set_attribute(server_game[key]['pos'])
        try:
            for sprite in self.sprites.values():
                if sprite.KEY not in server_game.keys():
                    del self.sprites[sprite.KEY]
                sprite.update(dt)
                sprite.draw()
        finally:
            pass

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
    Game(client.ClientNetwork("86.253.205.36", 39783)).run()