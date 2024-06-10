import pygame
from ui import Text, Input, Button
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
        self.text = Text('Press <Ctrl> and <Tab> to start the game', 50, (550, 400), 'black', 'center')
        self.game = None
        self.input = Input(self.screen, (300, 100), (390, 500), (255, 255, 255), "rounded rect", 50)
        self.button = Button(self.screen, (100, 100), (600, 300), (0, 0, 0), "rounded rect", [pygame.quit])

    def draw_background(self):
        self.screen.fill(self.background_color)

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:

                    if pygame.key.get_pressed()[pygame.K_TAB] and pygame.key.get_pressed()[pygame.K_LCTRL]:
                        running = False
                        print(running)
                        host, port = ConfigFile().get_host()
                        Level(self.screen, ClientNetwork(host=host, port=port)).run()

                    elif self.input.is_writing:
                        self.input.write(event.key)

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if self.input.rect.collidepoint(event.pos):
                        self.input.is_writing = True

                    else:
                        self.input.is_writing = False

                    self.button.check_clicked(event)

            self.draw_background()
            self.text.draw(self.screen)
            self.input.draw()
            self.button.draw()
            self.input.display_data()
            pygame.display.update()
            self.screen.fill(self.background_color)

        pygame.quit()


if __name__ == "__main__":
    MainWindow().run()
