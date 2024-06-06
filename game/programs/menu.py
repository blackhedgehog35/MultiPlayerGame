import pygame
from ui import Text
from game import Game
from client import ClientNetwork


class MainWindow:
    pygame.init()
    background_color = '#DCD7D0'
    width = 1100
    height = 800

    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('MENU - MULTIPLAYER GAME')
        self.text = Text('Press <Ctrl> and <Tab> to start the game', 50, (550, 400), 'black', 'center')
        self.game = None

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
                        Game(self.screen, ClientNetwork("86.253.205.36", 39783)).run()

            self.draw_background()
            self.text.draw(self.screen)
            pygame.display.update()
            self.screen.fill(self.background_color)

        pygame.quit()


if __name__ == "__main__":
    MainWindow().run()
