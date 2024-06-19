import pygame.sprite

from ui import *


class Settings:

    pygame.init()
    bg_color = "black"

    def __init__(self, screen, mainwindow):
        self.screen = screen
        self.sprites = []
        self.around_text = Shapes(self.screen, [], (200, 60), (0, 20), (50, 50, 50), "rect", None, 5, None, None, "topleft")
        self.settings_text = Text(self.screen, [], "Settings", 30, (75, 25), (255, 255, 255))
        self.exit_button = Button(self.screen, [], (40, 50), (30, 50), (255, 255, 255), "rounded rect", [self.stop_settings, mainwindow.run])

        self.line = Shapes(self.screen, [], (3, self.screen.get_height()), (210, 0), (50, 50, 50), "rect", None, 5, None, None, "topleft")

        self.port_input = Input(self.screen, self.sprites, (150, 25), (750, 150), (200, 200, 200), "rect", "", title="PORT", title_size=20)
        self.adress_input = Input(self.screen, self.sprites, (150, 25), (750, 300), (200, 200, 200), "rect", "", title="ADRESS IP", title_size=20)
        self.keyboard_selector = Selector(self.screen, self.sprites, (750, 450), (200, 200, 200),
                                          [Text(self.screen, self.sprites, "QWERTY", 18, (0, 0), (0, 0, 0)), Text(self.screen, self.sprites, "AZERTY", 18, (0, 0), (0, 0, 0))], "rect", title="KEYBOARD", title_size=20)
        self.luminosity_cursor = Cursor(self.screen, self.sprites, (150, 10), (750, 600), (200, 200, 200), 20, 1/1, "LUMINOSITY", title_size=20)
    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def stop_settings(self):
        self.running = False

    def run(self):
        self.running = True

        while self.running:

            self.draw_bg()

            self.around_text.draw()
            self.settings_text.draw()
            self.exit_button.draw()

            self.line.draw()

            self.adress_input.draw()
            self.luminosity_cursor.draw_all()
            self.port_input.draw()

            self.keyboard_selector.draw()
            self.keyboard_selector.draw_all()

            pygame.display.flip()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_settings()
                    pygame.quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.adress_input.check_clicked(event)
                    self.port_input.check_clicked(event)
                    self.exit_button.check_clicked(event)
                    self.keyboard_selector.check_arrows_clicked(event)
                    self.luminosity_cursor.check_clicked(event)

                elif event.type == pygame.KEYDOWN:
                    self.adress_input.check_key(event)
                    self.port_input.check_key(event)

                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:
                        for sprite in self.sprites:
                            sprite.rect.y += 5
                    else:
                        for sprite in self.sprites:
                            sprite.rect.y -= 5

