import pygame
from pygame.locals import *
import ui
import config

pygame.init()


class Text(pygame.sprite.Sprite):
    config_file = config.ConfigFile()

    def __init__(self, text, size, color, pos, side='topleft', bold=False):
        super().__init__()
        self.text = text

        self.font = pygame.font.SysFont(self.config_file.get('FONT', 'font-family'), int(size), bold=bold)
        self.color = color
        self.pos = pos
        self.side = side

        self.image = self.font.render(self.text, 1, self.color)
        self.rect = self.image.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update_text(self, text):
        self.text = text
        self.image = self.font.render(self.text, 1, self.color)
        self.rect = self.image.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update(self):
        # This method is called by the group update method.
        # Currently, it doesn't need to do anything, but you could add logic here if needed.
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Settings:
    config_file = config.ConfigFile()
    FPS = config_file.getint('SCREEN--SETTINGS', 'FPS')
    screen_size = config_file.get_screen_size()
    #  Container : Top, left, right
    padding = {'container': {"top": 55, "left": 240, "right": 240}, "between": {"title": 70, "variable": 40}}

    def __init__(self, screen: pygame.surface.Surface = None):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.screen = screen if screen else pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Settings")

        self.main_container = pygame.rect.Rect(self.padding["container"]["left"], self.padding["container"]["top"],
                                               self.screen_size[0] - self.padding["container"]["left"] -
                                               self.padding["container"]["right"],
                                               self.screen_size[1] - self.padding["container"]["top"])

        self.clock = pygame.time.Clock()
        self.get_settings_sections()
        self.text_group = pygame.sprite.Group()
        for section in self.get_settings_sections():
            self.add_section(section)

    def get_settings_sections(self):
        section_settings = []
        for section in self.config_file.sections():
            if '--SETTINGS' in section:
                section_settings.append(section)
        return section_settings

    def draw_bg(self):
        self.screen.fill("black")

    def get_last_rect(self):
        c = self.padding['container']['top']
        for text in self.text_group.sprites():
            c = max(c, text.rect.bottom)
        return c

    def add_section(self, section_name):
        section_title = section_name
        if "--SETTINGS" in section_name:
            section_title = section_name.replace("--SETTINGS", "")

        pos = (self.screen_size[0] / 2, self.get_last_rect() if self.get_last_rect() == self.padding['container']['top']
               else self.get_last_rect() + self.padding['between']['title'])
        title_text = Text(section_title, self.config_file.getint('FONT', 'title-size'), (255, 255, 255), pos,
                          side='midtop', bold=True)

        self.text_group.add(title_text)

        for variable_name in self.config_file.options(section_name):
            text = Text(f"{variable_name} :".upper(), self.config_file.getint('FONT', 'body-size'),
                        (255, 255, 255), (self.padding['container']['left'], self.get_last_rect() +
                                          self.padding['between']['variable']), side="topleft")

            self.text_group.add(text)

    def run(self):
        running = True
        while running:
            self.draw_bg()

            _dt = self.clock.tick(self.FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

            for text in self.text_group.sprites():
                text.draw(self.screen)

            # Update the display
            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    print(pygame.font.get_fonts())
    Settings().run()
