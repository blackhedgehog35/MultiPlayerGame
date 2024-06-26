import pygame
import config

pygame.init()


class Text(pygame.sprite.Sprite):
    config_file = config.ConfigFile()

    def __init__(self, text, size, color, pos, side='topleft', bold=False):
        super().__init__()
        self.str = text

        self.font = pygame.font.SysFont(self.config_file.get('FONT', 'font-family'), int(size), bold=bold)
        self.color = color
        self.pos = pos
        self.side = side
        self.image = self.font.render(self.str, 1, self.color)
        self.rect = self.image.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update_text(self, text):
        self.str = text
        self.image = self.font.render(self.str, 1, self.color)
        self.rect = self.image.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update(self):
        # This method is called by the group update method.
        # Currently, it doesn't need to do anything, but you could add logic here if needed.
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Input(pygame.sprite.Sprite):
    config_file = config.ConfigFile()
    padding = {"between rect and text": {"x": 4, "y": 3}}
    authorized_char = ""
    """
    (48, 58) --> 0123456789
    (97, 123) --> abc...xyz
    (65, 91) --> ABCD...XYZ
    46 --> .
    """

    def __init__(self, default_text, text_size, color: tuple, pos, max_character=8, authorized_char=((48, 58), (97, 123),
                                                                                                     (65, 91), 46),
                 side="topleft", text_side="left"):
        super().__init__()
        self.max_character = max_character
        self.text_size = text_size
        self.rect_color, color = color
        self.text = Text(default_text, text_size, color, pos)
        self.get_authorized_char(authorized_char)
        char_x_size, char_y_size = self.found_size()
        print(self.authorized_char)
        print(self.found_size())
        self.rect = pygame.rect.Rect(0, 0, char_x_size * self.max_character + 2 *
                                     self.padding["between rect and text"]["x"], char_y_size + 2 *
                                     self.padding["between rect and text"]["y"])
        setattr(self.rect, side, pos)

        setattr(self.text.rect, f"bottom{text_side}", (getattr(self.rect, text_side) +
                                                       self.padding["between rect and text"]["x"],
                                                       self.rect.bottom + self.padding["between rect and text"]["y"]))

    def get_authorized_char(self, chr_value):
        for value in chr_value:
            try:
                start, end = value
                for i in range(start, end):
                    self.authorized_char += chr(i)
            except TypeError:
                self.authorized_char += chr(value)

    def found_size(self):
        c_x, c_y = 0, 0
        for char in self.authorized_char:
            image = self.text.font.render(char, True, "white")
            rect = image.get_rect()
            c_x, c_y = max(c_x, rect.width), max(c_y, rect.height)
        return c_x, c_y

    def draw(self, surface):
        pygame.draw.rect(surface, self.rect_color, self.rect, border_radius=5)
        surface.blit(self.text.image, self.text.rect)


class Settings:
    config_file = config.ConfigFile()
    FPS = config_file.getint('SCREEN--SETTINGS', 'FPS')
    screen_size = config_file.get_screen_size()
    #  Container : Top, left, right
    margin = {'container': {"top": 55, "left": 240, "right": 240}, "between": {"title": 70, "variable": 40}}

    def __init__(self, screen: pygame.surface.Surface = None):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.screen = screen if screen else pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Settings")

        self.main_container = pygame.rect.Rect(self.margin["container"]["left"], self.margin["container"]["top"],
                                               self.screen_size[0] - self.margin["container"]["left"] -
                                               self.margin["container"]["right"],
                                               self.screen_size[1] - self.margin["container"]["top"])
        self.input = Input("test", 40, ("white", 'black'), (self.main_container.right, 200), max_character=4,
                           side="topright", text_side="right")
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
        c = self.margin['container']['top']
        for text in self.text_group.sprites():
            c = max(c, text.rect.bottom)
        return c

    def add_section(self, section_name):
        section_title = section_name
        if "--SETTINGS" in section_name:
            section_title = section_name.replace("--SETTINGS", "")

        pos = (self.screen_size[0] / 2, self.get_last_rect() if self.get_last_rect() == self.margin['container']['top']
               else self.get_last_rect() + self.margin['between']['title'])
        title_text = Text(section_title, self.config_file.getint('FONT', 'title-size'), (255, 255, 255), pos,
                          side='midtop', bold=True)

        self.text_group.add(title_text)

        for variable_name in self.config_file.options(section_name):
            text = Text(f"{variable_name} :".upper(), self.config_file.getint('FONT', 'body-size'),
                        (255, 255, 255), (self.margin['container']['left'], self.get_last_rect() +
                                          self.margin['between']['variable']), side="topleft")

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
            self.input.draw(self.screen)
            # Update the display
            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    Settings().run()
