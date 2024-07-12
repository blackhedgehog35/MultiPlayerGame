import sys
import pygame
from client import ClientNetwork
from sprites import Sprite, CustomSpriteGroup
from config import ConfigFile
from ui import show_info


class Level:
    config_file = ConfigFile()
    FPS = config_file.getint('SCREEN--SETTINGS', 'FPS')
    address, port = config_file.get_host()
    key = config_file.get_key()

    def __init__(self, screen=None, connection: ClientNetwork = None):
        pygame.init()
        self.screen = screen if screen else pygame.display.set_mode(self.config_file.get_screen_size())
        self.conn = connection if connection else ClientNetwork(self.address, self.port, key=self.key)
        pygame.display.set_caption('')

        self.clock = pygame.time.Clock()
        self.all_sprites = CustomSpriteGroup()
        self.all_sprites.add(Sprite(self.conn.KEY, self.conn.spawn_pos, self.all_sprites))

    def draw_bg(self):
        self.screen.fill('#5a5a5a')

    def update(self, dt, server_game):
        self.draw_bg()
        show_info(f'POS : {self.all_sprites.find(self.conn.KEY).pos}', (0, self.screen.get_height()), 'bottomleft')
        #  Update the local game with the server
        for key in server_game.keys():
            if key not in [sprite.KEY for sprite in self.all_sprites.sprites()]:
                self.all_sprites.add(Sprite(key, server_game[key]['pos'], self.all_sprites))
            else:
                if key != self.conn.KEY:
                    self.all_sprites.find(key).set_attribute(server_game[key]['pos'])
        #  Update and Draw the sprites
        for sprite in self.all_sprites.sprites():
            if sprite.KEY == self.conn.KEY:
                sprite.input()
            #  We check also if it's an instance of Player because the elements of the decor will be also in the sprite
            #  group and doesn't have a key
            elif sprite.KEY not in server_game.keys() and isinstance(sprite, Sprite):
                self.all_sprites.remove(sprite)
        self.all_sprites.update(dt)
        self.all_sprites.custom_draw(self.all_sprites.find(self.conn.KEY))

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(self.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            server_game = self.conn.send_attribute((self.all_sprites.find(self.conn.KEY).rect.x,
                                                    self.all_sprites.find(self.conn.KEY).rect.y))
            self.update(dt, server_game)
            pygame.display.flip()
        self.config_file.save_key(self.conn.KEY)


if __name__ == '__main__':
    Level().run()
