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
    min_char_value = 0
    max_char_value = 11100
    is_writing = False
    """
    (48, 58) --> 0123456789
    (97, 123) --> abc...xyz
    (65, 91) --> ABCD...XYZ
    46 --> .
    """

    def __init__(self, default_text, text_size, colors: tuple, pos, max_character=8, authorized_char=((48, 58), (97, 123),
                                                                                                          (65, 91), 46),
                 side="topleft", text_side="left"):
        super().__init__()
        self.default_text = default_text
        self.text_size = text_size
        self.rect_color, text_color = colors
        self.pos = pos
        self.max_character = max_character
        self.get_authorized_char(authorized_char)
        self.side = side
        self.text_side = text_side

        self.text = Text(default_text, text_size, text_color, pos, side=f"bottom{self.text_side}")
        char_x_size, char_y_size = self.found_size()
        self.rect = pygame.rect.Rect(0, 0,
                                     char_x_size * self.max_character + 2 * self.padding["between rect and text"]["x"],
                                     char_y_size + 2 * self.padding["between rect and text"]["y"])

        setattr(self.rect, self.side, self.pos)

        d = -1 if text_side == 'right' else 1
        setattr(self.text.rect, f"bottom{text_side}", (getattr(self.rect, text_side) +
                                                       self.padding["between rect and text"]["x"] * d,
                                                       self.rect.bottom + self.padding["between rect and text"]["y"]))
        self.text.update_text(default_text)

    def get_authorized_char(self, chr_values):

        for value in chr_values:
            try:
                start, end = value
                for i in range(start, end):
                    self.min_char_value = min(self.min_char_value, i)
                    self.max_char_value = min(self.max_char_value, i)
                    self.authorized_char += chr(i)
            except TypeError:
                self.min_char_value = min(self.min_char_value, value)
                self.max_char_value = min(self.max_char_value, value)

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

    def write(self, key_pressed):
        if self.is_writing:
            value = self.text.str

            if key_pressed == pygame.K_BACKSPACE:
                # we replace the variable with the same variable but without the last letter
                value = value[0:-1]

            elif self.min_char_value <= key_pressed <= self.max_char_value:
                if chr(key_pressed) in self.authorized_char:
                    value += chr(key_pressed)
                    print('TATA')

            self.text.update_text(value)

    def check_clicked(self, event):
        if self.rect.collidepoint(event.pos):
            self.is_writing = True
        else:
            self.is_writing = False


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

        self.clock = pygame.time.Clock()
        self.get_settings_sections()
        self.component_group = pygame.sprite.Group()
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
        for text in self.component_group.sprites():
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

        self.component_group.add(title_text)

        for variable_name in self.config_file.options(section_name):
            _text = Text(f"{variable_name} :".upper(), self.config_file.getint('FONT', 'body-size'),
                        (255, 255, 255), (self.main_container.left, self.get_last_rect() +
                                          self.margin['between']['variable']), side="topleft")
            try:
                variable_value = self.config_file.getint(section_name, variable_name)
            except ValueError:
                variable_value = self.config_file.get(section_name, variable_name)

            _input = Input(f"{variable_value}".upper(), self.config_file.getint('FONT', 'body-size'),
                           ("white", "black"), (self.main_container.right, _text.rect.centery), side="midright",
                           text_side="right", max_character=len(str(variable_value)) + 1)
            self.component_group.add(_text)
            self.component_group.add(_input)

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
                    else:
                        for component in self.component_group.sprites():
                            if isinstance(component, Input):
                                component.write(event.key)
                                break

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for component in self.component_group.sprites():
                        if isinstance(component, Input):
                            component.check_clicked(event)


            for component in self.component_group.sprites():
                component.draw(self.screen)
            # Update the display
            pygame.display.flip()

        pygame.quit()


if __name__ == '__main__':
    Settings().run()
