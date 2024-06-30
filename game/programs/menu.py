import sys
import pygame
from level import Level
from settings import Settings, Text
from client import ClientNetwork
from config import ConfigFile
"""Ce que je dois corriger :
Objet ConfigFile à revoir : ce serai plus simple que les attributs, on les ai en variable ex : config_file.key
et qu'à chaque fois qu'on veut être sur que ça ai pris les dernières modifications, on met un methode update()
pour être sûr que toute les variabes ont bien les bonnes valeurs. J'ai comme l'impression que ça commence à être
un meli-melo mdr. 

"""


class MainWindow:
    pygame.init()
    background_color = '#DCD7D0'
    config_file = ConfigFile()
    width, height = config_file.get_screen_size()
    FPS = config_file.getint("SCREEN--SETTINGS", "fps")
    pygame.init()

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.text = Text("Press <Ctrl> and <Tab> to start the game", 40, 'black',
                         (self.width / 2, self.height / 2.3), side="center", bold=True)
        address, port = self.config_file.get_host()
        self.host_text = Text(f"{address}:{port}", 18, "black", (0, self.height),
                              side="bottomleft", bold=True)
        self.clock = pygame.time.Clock()
        self.refresh_page()

    def refresh_page(self):
        pygame.display.set_caption('MENU - MULTIPLAYER GAME')
        self.config_file = ConfigFile()
        address, port = self.config_file.get_host()
        self.FPS = self.config_file.getint("SCREEN--SETTINGS", "fps")
        self.host_text.update_text(f"{address}:{port}")

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
                        host, port = ConfigFile().get_host()
                        Level(self.screen, ClientNetwork(host=host, port=port)).run()
                        self.refresh_page()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    Settings(self.screen).run()
                    self.refresh_page()

            self.text.draw(self.screen)
            self.host_text.draw(self.screen)
            pygame.display.update()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    MainWindow().run()
