import os
import sys
import pygame
import threading
from level import Level
from config import ConfigFile
from settings import Settings, Text
from client import ClientNetwork, ServerNoFound

"""
WindowsArchitecture :

    ┌──> Menu <─> Settings
    |      │
    | WaitingRoomToGetConn
    |      │
    └─── Level
     
"""


class WaitingRoomToGetConn:
    config_file = ConfigFile()
    error_msg = None
    padding = {"between title and host": 10}

    def __init__(self, screen: pygame.surface.Surface = None):
        pygame.init()
        self.screen = screen if screen else pygame.display.set_mode(self.config_file.get_screen_size())
        pygame.display.set_caption("")

        self.conn = ClientNetwork
        self.host, self.port = ConfigFile().get_host()
        self.key = ConfigFile().get_key()
        self.text_group = {"Title": Text("Searching for the server.", self.config_file.get_title_size(), "white",
                                         (self.screen.get_width() / 2, 280), "midtop", True),
                           "Timer": Text("", self.config_file.get_body_size(), "white", (0, 0), "topleft")
                           }
        self.text_group['Host'] = Text(f"{self.host} : {self.port}", self.config_file.get_body_size(), "white",
                                       (self.screen.get_width() / 2, self.text_group['Title'].rect.bottom +
                                        self.padding["between title and host"]), "midtop", True)

        self.text_group['Title'].pos = self.text_group['Title'].rect.topleft
        self.text_group['Title'].side = 'topleft'

        self.start_time = pygame.time.get_ticks()

    def update_animations(self):
        f = 0.0025
        time = round((pygame.time.get_ticks() - self.start_time) / 1000)
        timer_text = f"{time // 60}min {time % 60}s" if time >= 60 else f"{time % 60}s"
        new_text = {'Title': f'Searching for the server'
                             f'{"." * (round((pygame.time.get_ticks() - self.start_time) / (1/f)) % 4)}',
                    'Timer': timer_text}
        for key, value in new_text.items():
            if self.text_group[key].str != value:
                self.text_group[key].update_text(value)

    def draw(self):
        self.screen.fill('black')
        for value in self.text_group.values():
            value.draw(self.screen)

    def init_objet(self):
        try:
            self.conn(self.host, self.port, self.key)
        except ServerNoFound as e:
            self.error_msg = e.__str__()
            print(self.error_msg)

    def run(self):
        thread = threading.Thread(target=self.init_objet)
        thread.start()
        running = True
        while running:
            if self.conn.connected:
                running = False
            elif self.error_msg is not None:
                running = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.error_msg = "Connection interrupted but not stopped so be careful"
            self.update_animations()
            self.draw()
            pygame.display.update()

        if self.conn.connected:
            return self.conn
        else:
            return self.error_msg


class MainWindow:
    pygame.init()
    background_color = '#DCD7D0'
    config_file = ConfigFile()
    width, height = config_file.get_screen_size()
    FPS = config_file.getint("SCREEN--SETTINGS", "fps")
    pygame.init()

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(self.config_file.get_screen_size())
        self.text = Text("Press <Ctrl> and <Tab> to start the game", 40, 'black',
                         (self.width / 2, self.height / 2.3), side="center", bold=True)
        self.clock = pygame.time.Clock()
        self.refresh_page()

    def refresh_page(self):
        pygame.display.set_caption('MENU - MULTIPLAYER GAME')
        self.config_file.update()
        self.FPS = self.config_file.getint("SCREEN--SETTINGS", "fps")

    def run(self) -> None:
        running = True
        while running:
            self.screen.fill(self.background_color)
            self.clock.tick(self.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_TAB] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        conn = WaitingRoomToGetConn(self.screen).run()
                        if isinstance(conn, ClientNetwork):
                            Level(self.screen, conn).run()
                        else:
                            print(conn)
                        self.refresh_page()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    Settings(self.screen).run()
                    self.refresh_page()

            self.text.draw(self.screen)
            pygame.display.update()
        pygame.quit()
        os._exit(1)


if __name__ == "__main__":
    MainWindow().run()
