import pygame
from ui import Text, Button
from level import Level
from client import ClientNetwork
from config import ConfigFile


class MainWindow:
    pygame.init()
    background_color = '#DCD7D0'
    width, height = ConfigFile().get_screen_size()

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('MENU - MULTIPLAYER GAME')
        self.game = None
        self.text = Text(self.screen, 'Press <Ctrl> and <Tab> to start the game', 50, (self.width / 2, self.height / 2), 'black')
        self.settings_button = Button(self.screen, (75, 75), (self.width - 100, self.height - 100), (0, 0, 0), "rounded rect", [self.stop_menu],
                                      Text(self.screen, "Settings", 15, (0, 0), (255, 255, 255), "center"))

    def draw_background(self):
        self.screen.fill(self.background_color)

    def stop_menu(self):
        self.running = False

    def run(self) -> None:
        self.running = True

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print(self.running)
                    self.stop_menu()
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:

                    if pygame.key.get_pressed()[pygame.K_TAB] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        self.stop_menu()
                        host, port = ConfigFile().get_host()
                        Level(self.screen, ClientNetwork(host=host, port=port)).run()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pass

            self.draw_background()
            self.text.draw()
            self.settings_button.draw()
            pygame.display.update()
            self.screen.fill(self.background_color)



if __name__ == "__main__":
    MainWindow().run()
