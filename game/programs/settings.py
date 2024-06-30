import pygame
import config

pygame.init()


class MainContainerGroup(pygame.sprite.Group):
    scroll_intensity = 20

    def __init__(self, container_rect, margin):
        super().__init__()
        self.main_container_rect = container_rect
        self.margin = margin
        self.screen = pygame.display.get_surface()
        self.current_input_selected = None
        #  camera offset
        self.offset = pygame.math.Vector2()

    def scroll(self, event_y):

        self.offset.y = event_y * self.scroll_intensity
        if self.main_container_rect.top + self.offset.y > self.margin['container']['top']:
            pass
        elif self.main_container_rect.bottom + self.offset.y < self.margin['container']['bottom']:
            pass
        else:
            self.main_container_rect.y += self.offset.y
            for component in self.sprites():
                component.scroll(self.offset.y)

    def get_last_rect_y(self):
        c = self.main_container_rect.top
        for component in self.sprites():
            c = max(c, component.rect.bottom)
        return c

    def custom_draw(self):
        for component in self.sprites():
            component.draw(self.screen)

    def custom_selector(self):

        mouse_x, mouse_y = pygame.mouse.get_pos()
        for component in self.sprites():
            if isinstance(component, InputTest):
                if component.rect.collidepoint(mouse_x, mouse_y):
                    component.is_writing = True
                    self.current_input_selected = component
        for component in self.sprites():
            if isinstance(component, InputTest):
                if component == self.current_input_selected:
                    pass
                else:
                    component.is_writing = False


class Text(pygame.sprite.Sprite):
    config_file = config.ConfigFile()

    def __init__(self, text, size, color, pos, side='topleft', bold=False):
        super().__init__()
        self.str = text

        self.font = pygame.font.SysFont(self.config_file.get('FONT', 'font-family'), int(size), bold=bold)
        self.color = color
        self.pos = pygame.math.Vector2(pos)
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

    def scroll(self, offset_y):
        self.pos.y += offset_y
        setattr(self.rect, self.side, self.pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class InputTest(pygame.sprite.Sprite):
    config_file = config.ConfigFile()
    padding = {"between rect and text": {"x": 4, "y": 3}}
    is_writing = False

    """
    (48, 58) --> 0123456789
    (97, 123) --> abc...xyz
    (65, 91) --> ABCD...XYZ
    46 --> .
    """

    def __init__(self, default_text, text_size, colors: tuple, pos, max_character=8,
                 authorized_char=((48, 58), (97, 123), (65, 91), 46), _id=""):
        #  pos : mid right side : right
        super().__init__()
        self.id = _id
        self.default_text = default_text
        self.text_size = text_size
        self.rect_color, text_color = colors
        self.pos = pos
        self.max_character = max_character
        self.authorized_char, self.min_char_value, self.max_char_value = self.get_authorized_char(authorized_char)

        char_x_size, char_y_size = self.found_size()
        self.rect = pygame.rect.Rect(0, 0,
                                     char_x_size * self.max_character + 2 * self.padding["between rect and text"]["x"],
                                     char_y_size + 2 * self.padding["between rect and text"]["y"])
        self.rect.midright = self.pos
        self.text = Text(self.default_text, text_size, text_color, (
            self.rect.right - self.padding['between rect and text']['x'],
            self.rect.bottom - self.padding['between rect and text']['y']
        ), "bottomright")
        self.write(pygame.K_BACKSPACE)

    @staticmethod
    def get_authorized_char(chr_values):
        min_char_value = None
        max_char_value = None
        authorized_char = ""
        for value in chr_values:
            try:
                start, end = value
                for i in range(start, end):
                    min_char_value = min(min_char_value, i) if min_char_value else i
                    max_char_value = max(max_char_value, i) if max_char_value else i
                    authorized_char += chr(i)
            except TypeError:
                min_char_value = min(min_char_value, value) if min_char_value else value
                max_char_value = max(max_char_value, value) if max_char_value else value

                authorized_char += chr(value)
        return authorized_char, min_char_value, max_char_value

    def found_size(self):
        font = pygame.font.SysFont(self.config_file.get('FONT', 'font-family'), self.text_size)
        c_x, c_y = 0, 0
        for char in self.authorized_char:
            image = font.render(char, True, "white")
            rect = image.get_rect()
            c_x, c_y = max(c_x, rect.width), max(c_y, rect.height)

        return c_x, c_y

    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_x, mouse_y):
            self.is_writing = True
        else:
            self.is_writing = False

    def scroll(self, offset_y):
        self.rect.y += offset_y
        self.text.scroll(offset_y)
        self.text.rect.bottomright = (self.rect.right - self.padding['between rect and text']['x'],
                                      self.rect.bottom - self.padding['between rect and text']['y'])

    def write(self, key_pressed):
        #  replace ; by .
        if self.is_writing:
            key_pressed = pygame.K_PERIOD if key_pressed == pygame.K_SEMICOLON else key_pressed
            value = self.text.str

            if key_pressed == pygame.K_BACKSPACE:
                # we replace the variable with the same variable but without the last letter
                value = value[0:-1]

            elif self.min_char_value <= key_pressed <= self.max_char_value and len(value) < self.max_character:
                if chr(key_pressed) in self.authorized_char:
                    value += chr(key_pressed)

            self.text.update_text(value)

    def draw(self, surface):
        pygame.draw.rect(surface, self.rect_color, self.rect, border_radius=5)
        if self.is_writing:
            pygame.draw.rect(surface, "brown", self.text.rect)
        surface.blit(self.text.image, self.text.rect)


class Settings:
    config_file = config.ConfigFile()
    FPS = config_file.getint('SCREEN--SETTINGS', 'FPS')
    screen_size = config_file.get_screen_size()
    #  Container : Top, left, right
    margin = {'container': {"top": 55, "bottom": screen_size[1] - 100, "left": 240, "right": 240},
              "between": {"title": 70, "variable": 40}}

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
        self.main_container_group = MainContainerGroup(self.main_container, self.margin)

        for section in self.get_settings_sections():
            self.add_section(section)
        self.main_container.height = self.main_container_group.get_last_rect_y() - self.margin['container']['top']

    def get_settings_sections(self):
        section_settings = []
        for section in self.config_file.sections():
            if '--SETTINGS' in section:
                section_settings.append(section)
        return section_settings

    def draw_bg(self):
        self.screen.fill("black")

    def add_section(self, section_name):
        section_title = section_name

        if "--SETTINGS" in section_name:
            section_title = section_name.replace("--SETTINGS", "")

        pos = (self.screen_size[0] / 2, self.main_container_group.get_last_rect_y() if
        self.main_container_group.get_last_rect_y() == self.margin['container']['top'] else
        self.main_container_group.get_last_rect_y() + self.margin['between']['title'])
        title_text = Text(section_title, self.config_file.getint('FONT', 'title-size'), (255, 255, 255), pos,
                          side='midtop', bold=True)

        self.main_container_group.add(title_text)

        for variable_name in self.config_file.options(section_name):
            text_size = self.config_file.getint('FONT', 'body-size')
            _text = Text(f"{variable_name} :".upper(), text_size,
                         (255, 255, 255), (self.main_container.left, self.main_container_group.get_last_rect_y() +
                                           self.margin['between']['variable']), side="topleft")
            try:
                variable_value = self.config_file.getint(section_name, variable_name)
                authorized_char = ((48, 57), 57)
            except ValueError:
                variable_value = self.config_file.get(section_name, variable_name)
                authorized_char = ((48, 58), 46)
            _input = InputTest(f"{variable_value}".upper(), text_size, ("white", "black"),
                               (self.main_container.right, _text.rect.centery),
                               max_character=len(str(variable_value)) + 1, authorized_char=authorized_char,
                               _id=f"{section_name}|{variable_name}")
            self.main_container_group.add(_text)
            self.main_container_group.add(_input)

    def save(self):
        for component in self.main_container_group.sprites():
            if isinstance(component, InputTest):
                section, option = component.id.split("|")
                self.config_file.edit_value(section, option, component.text.str)

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
                        for component in self.main_container_group.sprites():
                            if isinstance(component, InputTest):
                                component.write(event.key)
                elif event.type == pygame.MOUSEWHEEL:
                    self.main_container_group.scroll(event.y)

            self.main_container_group.custom_selector()
            self.main_container_group.custom_draw()
            # Update the display
            pygame.display.flip()
        self.save()
        pygame.quit()


if __name__ == '__main__':
    Settings().run()
