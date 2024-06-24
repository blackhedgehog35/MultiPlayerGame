import pygame
import ui
import config
pygame.init()


class Settings:
    config_file = config.ConfigFile()
    FPS = config_file.getint('SCREEN--SETTINGS', 'FPS')
    screen_size = config_file.get_screen_size()
    #  Container : Top, left, right
    padding = {'container': {"top": 80, "left": 200, "right": 200}, "between": {"title": 10, "variable": 5}}

    def __init__(self, screen: pygame.surface.Surface = None):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.screen = screen if screen else pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Settings")

        self.main_container = pygame.rect.Rect(self.padding["container"][1], self.padding["container"]["top"],
                                               self.screen_size[0] - self.padding["container"]["left"] -
                                               self.padding["container"]["right"],
                                               self.screen_size[1] - self.padding["container"]["top"])

        self.clock = pygame.time.Clock()
        self.get_settings_sections()
        self.text_group = pygame.sprite.Group()

    def get_settings_sections(self):
        for section in self.config_file.sections():
            if '--SETTINGS' in section:
                print(section)
                for variable_name in self.config_file.options(section):
                    print(variable_name)

    def draw_container(self):
        self.screen.fill("black", self.main_container)

    def draw_bg(self):
        self.screen.fill((255, 255, 255))

    def add_section(self, section_name):
        for variable in self.config_file.options(section_name):
            ui.Text(self.screen,
                    group=self.text_group,
                    text=section_name,
                    size=self.config_file.getint("FONT", "title-size"),
                    pos=(),
                    color=(255, 255, 255),
                    side="topleft")

    def run(self):
        running = True
        while running:
            self.draw_bg()

            _dt = self.clock.tick(self.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.draw_container()

            # Update the display
            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    Settings().run()
