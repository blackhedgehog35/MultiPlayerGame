import  pygame
from  ui import *

class Settings:

    pygame.init()
    bg_color = "black"

    def __init__(self, screen):
        self.screen = screen
        self.keyboard_selector = Selector(self.screen, (750, 450), (0, 0, 255),
                                          [Text(self.screen, "bvc", 50, (0, 0), (255, 255, 255)), Text(self.screen, "bvc", 50, (0, 0), (255, 255, 255))], "rect")
        self.port_input = Input(self.screen, (150, 25), (750, 150), (0, 0, 255), "rect", "", title="PORT")
        self.adress_input = Input(self.screen, (150, 25), (750, 300), (0, 0, 255), "rect", "", title="ADRESS IP")

    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def stop_settings(self):
        self.running = False

    def run(self):
        self.running = True

        while self.running:


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_settings()
                    pygame.quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.adress_input.check_clicked(event)
                    self.port_input.check_clicked(event)
                    self.keyboard_selector.check_arrows_clicked(event)

                elif event.type == pygame.KEYDOWN:
                    self.adress_input.check_key(event)
                    self.port_input.check_key(event)

                self.draw_bg()
                self.adress_input.draw()
                self.port_input.draw()
                self.keyboard_selector.draw()
                self.keyboard_selector.draw_all()

                pygame.display.flip()


screen = pygame.display.set_mode((1080, 750))

settings = Settings(screen)
settings.run()
