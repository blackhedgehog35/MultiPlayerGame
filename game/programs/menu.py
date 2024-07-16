import pygame
import threading
from level import Level
from config import ConfigFile, close
from settings import Settings, Text, PopUp
from client import ClientNetwork, ServerNoFound

"""
WindowsArchitecture :

    ┌──> Menu <─> Settings
    |      │
    └── WaitingRoomToGetConn
           │
         Level
     
"""


class WaitingRoomToGetConn:
    config_file = ConfigFile()
    error_msg = None
    padding = {"between title and host": 10}
    #  Switch to True if you don't want to receive a popup
    popped = False

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
        self.popup = PopUp()

    def update_animations(self):
        f = 25
        time = round((pygame.time.get_ticks() - self.start_time) / 1000)
        timer_text = f"{time // 60}min "*int(time // 60 > 0) + f"{time % 60}s"*int(time % 60 > 0)
        new_text = {'Title': f'Searching for the server'
                             f'{"." * (round((pygame.time.get_ticks() - self.start_time) * f / 10 ** 4) % 4)}',
                    'Timer': timer_text}
        for key, value in new_text.items():
            if self.text_group[key].str != value:
                self.text_group[key].update_text(value)

    def update(self):
        time = round((pygame.time.get_ticks() - self.start_time) / 1000)
        if not self.popped and time >= 30:
            self.popup.notify(icon_type="info", body=f"Are you sure the host address is {self.host}:{self.port} ?")

            self.popped = True

    def draw(self):
        self.update()
        self.screen.fill('black')
        for value in self.text_group.values():
            value.draw(self.screen)
        self.popup.draw()

    def init_objet(self):
        try:
            self.conn = self.conn(self.host, self.port, self.key)
        except ServerNoFound as e:
            self.error_msg = {'type': 'error', 'content': e.__str__()}

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
                    close()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.error_msg = {'type': 'info',
                                          'content': "Connection interrupted but not stopped so be careful"}
            self.update_animations()
            self.draw()
            pygame.display.update()

        if self.conn.connected:
            return self.conn
        else:
            return self.error_msg


class MainWindow:
    pygame.init()
    background_color = 'black'
    config_file = ConfigFile()
    width, height = config_file.get_screen_size()
    FPS = config_file.getint("SCREEN--SETTINGS", "fps")
    pygame.init()

    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode(self.config_file.get_screen_size())
        self.text2 = Text("Click to Play!", 70, "white", (self.width / 2, self.height / 2.3), side="midbottom",
                          bold=True)
        self.text1 = Text("press any key to open settings", 40, 'white', self.text2.rect.midbottom, side="midtop")
        self.pop_up = PopUp()
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
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        Settings(self.screen).run()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    conn = WaitingRoomToGetConn(self.screen).run()
                    if isinstance(conn, ClientNetwork):
                        Level(self.screen, conn).run()
                    else:
                        self.pop_up.notify(icon_type=conn['type'], body=conn['content'])
                    self.refresh_page()
            self.pop_up.draw()
            self.text1.draw(self.screen)
            self.text2.draw(self.screen)
            pygame.display.update()
        close()


if __name__ == "__main__":
    MainWindow().run()
