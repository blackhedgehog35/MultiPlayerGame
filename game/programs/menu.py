import os
import sys
import threading

import pygame
from level import Level
from settings import Settings, Text
from client import ClientNetwork, ServerNoFound, ServerClosed
from config import ConfigFile

"""Ce que je dois corriger :
Objet ConfigFile à revoir : ce serai plus simple que les attributs, on les ai en variable ex : config_file.key
et qu'à chaque fois qu'on veut être sur que ça ai pris les dernières modifications, on met un methode update()
pour être sûr que toute les variabes ont bien les bonnes valeurs. J'ai comme l'impression que ça commence à être
un meli-melo mdr.
Ajouter les touches dans settings.py
- Faire un truc qui vérifie que les valeurs dans les inputs sont bien, sinon pour le moment, ne pas modifier les settings,
puis mettre un message pour dire à l'utilisateur que les valeurs sont incorrect.


*  Il faudrai faire une page d'attente pour attendre que le server réponde, qu'on pourrai à tout moment arreter si ça 
prend trop de temps. Je pense que c'est possible avec les threads
Ce qu'il faut ajouter à WaitingRommToGetConn
- un texte interractif qui genre met connection en cours ... avec les trois points qui qui font une animation
- ça affiche l'host et le port         
      
    ┌──> Menu <─> Settings
    |      │
    | WaitingRoom
    |      │
    └─── Level
    
ATTENTION !!! GROS BUG ! Dans le thread de Waiting Room, lorqu'on sort de la fenetre WaitingRoom, ne s'arrete pas tout de suite
donc potentiellement on pourrai faire plein de requête en attente et je ne sais pas ce que ça pourrai faire de voiloir tenter de 
créer plein d'instance de ClientNetwork donc à surveiller. 
Suggestion : On fait un variable connection dans Menu pour pas qu'on puisse en créer plusieur, donc si jamais on quitte sans 
que le clientNetwork soit terminé et qu'on relance, on reprend cet objet parce que je ne sais pas ce qui peux se passer à 
long terme si on créer bcp d'objet ClientNetwork: En gros on garde le même jusqu'à qu'il se termine tout seul et si et seulement si
il se termine alors on en créer un autre
"""


class WaitingRoomToGetConn:
    config_file = ConfigFile()
    error_msg = None
    padding = {"between title and host": 10}

    def __init__(self, screen=None):
        self.screen = screen if screen else pygame.display.set_mode(self.config_file.get_screen_size())
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
        new_text = {'Title': f'Searching for the server{"." * (round((pygame.time.get_ticks() - self.start_time) / (1/f)) % 4)}',
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
        self.config_file.update()
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
            self.host_text.draw(self.screen)
            pygame.display.update()
        pygame.quit()
        os._exit(1)


if __name__ == "__main__":
    MainWindow().run()
