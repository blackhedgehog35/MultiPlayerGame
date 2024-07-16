import pygame
from config import ConfigFile, close
from animations import load_animation


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

    def inputs(self) -> list:
        input_list = []
        for sprite in self.sprites():
            if isinstance(sprite, Input):
                input_list.append(sprite)
        return input_list

    def input_key(self) -> list:
        component_list = []
        for component in self.sprites():
            if isinstance(component, OneKeyInput):
                component_list.append(component)
        return component_list

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
            component.update()
            component.draw(self.screen)

    def custom_selector(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        for component in self.sprites():
            if isinstance(component, Input):
                if component.rect.collidepoint(mouse_x, mouse_y):
                    component.is_writing = True
                    self.current_input_selected = component
        for component in self.sprites():
            if isinstance(component, Input):
                if component == self.current_input_selected:
                    pass
                else:
                    component.is_writing = False

    def get_clicked_input_key(self) -> list:
        list_component = []
        for component in self.sprites():
            if isinstance(component, OneKeyInput):
                if component.clicked:
                    list_component.append(component)
                    #  break because in theory, there is just one component that is activated
                    break
        return list_component


class TextGroup(pygame.sprite.Group):
    def __init__(self, rect: pygame.Rect):
        super().__init__()
        self.screen = pygame.display.get_surface()
        #  self.rect = pygame.Rect(icon_rect.right, icon_rect.top, main_rect.width-icon_rect.width-10, icon_rect.height)
        self.rect = rect

    def get_bottom_pos_last_text(self) -> int:
        height = self.rect.top
        for sprite in self.sprites():
            height = max(height, sprite.rect.bottom)
        return height

    def set_text(self, *, title: str = None, content: str = None, center=False, text_color="black"):

        if title:
            total_sentence = []
            text = None
            for word in title.split(' '):
                total_sentence.append(word)
                text_pos = (self.rect.left, self.get_bottom_pos_last_text())
                text = Text(" ".join(total_sentence), 20, text_color, text_pos, bold=True)

                if text.rect.right > self.rect.right:
                    total_sentence.remove(word)
                    text = Text(" ".join(total_sentence), 20, text_color, text_pos, bold=True)
                    total_sentence = [word]
                    self.add(text)
            self.add(text)

        if content:
            total_sentence = []
            for index, word in enumerate(content.split(' ')):
                total_sentence.append(word)
                text_pos = (self.rect.left, self.get_bottom_pos_last_text())
                text = Text(" ".join(total_sentence), 20, text_color, text_pos)

                if text.rect.right > self.rect.right and len(total_sentence) != 1:
                    total_sentence.remove(word)
                    text = Text(" ".join(total_sentence), 20, text_color, text_pos)
                    self.add(text)
                    total_sentence = [word]
            if len(total_sentence) != 0:
                self.add(Text(" ".join(total_sentence), 20, text_color, (self.rect.left,
                                                                         self.get_bottom_pos_last_text())))

        if center:
            self.recenter_text()

    def set_transparency(self, transparency):
        for sprite in self.sprites():
            sprite.image.set_alpha(transparency)

    def recenter_text(self):
        top = None
        bottom = None
        for sprite in self.sprites():
            top = min(top, sprite.rect.top) if top else sprite.rect.top
            bottom = max(bottom, sprite.rect.bottom) if bottom else sprite.rect.bottom

        for sprite in self.sprites():
            sprite.rect.y += (self.rect.height - (bottom - top)) / 2 - (top - self.rect.top)

    def draw_hitbox(self):
        pygame.draw.rect(self.screen, "purple", self.rect)
        for text in self.sprites():
            pygame.draw.rect(self.screen, "pink", text.rect)
            text.draw(self.screen)

    def draw_text(self):
        for text in self.sprites():
            text.draw(self.screen)


class Text(pygame.sprite.Sprite):
    config_file = ConfigFile()

    def __init__(self, text, size, color, pos=(0, 0), side='topleft', bold=False):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.str = text

        self.font = pygame.font.SysFont(self.config_file.get_font_name(), int(size), bold=bold)
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

    def draw(self, surface=None):
        if surface:
            surface.blit(self.image, self.rect)
        else:
            self.screen.blit(self.image, self.rect)


class Input(pygame.sprite.Sprite):
    config_file = ConfigFile()
    padding = {"between rect and text": {"x": 4, "y": 3}}
    is_writing = False
    border_radius = 5

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
        self.hover_border_radius = 0 if self.border_radius == 0 else (
                self.border_radius - min(self.padding['between rect and text']['x'],
                                         self.padding['between rect and text']['y']))

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
        font = pygame.font.SysFont(self.config_file.get_font_name(), self.text_size)
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
        pygame.draw.rect(surface, self.rect_color, self.rect, border_radius=self.border_radius)
        if self.is_writing:
            pygame.draw.rect(surface, "brown", self.text.rect, border_radius=self.hover_border_radius)
        surface.blit(self.text.image, self.text.rect)


class OneKeyInput(pygame.sprite.Sprite):
    config_file = ConfigFile()
    special_values = {pygame.K_RIGHT: 'right arrow', pygame.K_LEFT: 'left arrow',
                      pygame.K_DOWN: 'down arrow', pygame.K_UP: 'up arrow', pygame.K_SPACE: 'space'}

    padding = {"between rect and text": {"x": 4, "y": 3}}
    border_radius = 5
    hover_border_radius = border_radius - min(padding["between rect and text"]['x'],
                                              padding["between rect and text"]['y'])
    hover = False
    clicked = False

    def __init__(self, default_value: int or None, colors: tuple, pos, _id=""):
        super().__init__()
        self.value = default_value
        self.id = _id
        self.color, text_color = colors
        self.pos = pygame.math.Vector2(pos)

        rect_x, rect_y = self.get_rect_size()
        self.rect = pygame.rect.Rect(0, 0, rect_x + 2 * self.padding['between rect and text']['x'],
                                     rect_y + 2 * self.padding['between rect and text']['y'])
        self.rect.midright = (self.pos.x, self.pos.y)

        self.text = Text(f" ", self.config_file.get_body_size(), text_color, self.rect.center, side="center")

    def transform_value_into_str(self, value) -> str:
        return self.special_values[value] if value in self.special_values.keys() else chr(value)

    def convert_int_to_str(self, key):
        if key in self.special_values.keys():
            return f"{self.special_values[key]}"
        else:
            return f"key <{chr(key).upper()}>"

    def set_value(self, key):
        self.value = key

    def update(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.hover = True
        else:
            self.hover = False

        if self.hover:
            if pygame.mouse.get_pressed()[0] and not self.clicked:
                self.clicked = True
                self.text.update_text(f"Press a key")
        elif pygame.mouse.get_pressed()[0] and self.clicked:
            self.clicked = False

        if self.clicked or self.value is None:
            self.text.update_text(f"Press a Key")
        else:
            self.text.update_text(self.convert_int_to_str(self.value))

    def get_rect_size(self):
        font = pygame.font.SysFont(self.config_file.get_font_name(), self.config_file.get_body_size(), False)
        biggest_word = "Press a Key"
        for text_group in self.special_values.values():
            if max(len(biggest_word), len(text_group)) == text_group:
                biggest_word = text_group
        return font.render(biggest_word, True, "black").get_rect().size

    def change_input_value(self, key):
        pass

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=self.border_radius)
        if self.hover or self.clicked:
            pygame.draw.rect(surface, "brown", self.text.rect, border_radius=self.hover_border_radius)
        self.text.draw(surface)

    def scroll(self, offset_y):
        self.rect.y += offset_y
        self.text.scroll(offset_y)
        self.text.rect.bottomright = (self.rect.right - self.padding['between rect and text']['x'],
                                      self.rect.bottom - self.padding['between rect and text']['y'])


class Icon(pygame.sprite.Sprite):
    def __init__(self, size, *path):
        super().__init__()
        self.screen = pygame.display.get_surface()
        self.size = size
        self.image = load_animation(*path).convert_alpha()
        self.image = pygame.transform.scale(self.image, self.size)

        self.rect = self.image.get_rect()

    def set_transparency(self, transparency):
        self.image.set_alpha(transparency)

    def draw(self):
        self.screen.blit(self.image, self.rect)


class PopUp(pygame.sprite.Sprite):
    duration = 7.5*10**3
    width_total = 610

    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()
        middle_screen = self.screen.get_width() / 2
        self.icon_rect = pygame.Rect(0, 0, 80, 80)
        self.content_rect = pygame.Rect(0, 0, self.width_total - 110, 80)

        self.main_rect = pygame.Rect(0, 0, self.width_total, 100)
        self.main_rect.midtop = (middle_screen, 30)

        self.icon_rect.midleft = (self.main_rect.x + 10, self.main_rect.centery)
        self.content_rect.midleft = (self.icon_rect.right + 10, self.icon_rect.centery)

        self.icon: Icon = None
        self.text_group: TextGroup = None

        self.surface = pygame.Surface(self.main_rect.size, pygame.SRCALPHA)
        self.active = False
        self.start_time = None

    def notify(self, *, icon_type="error", title=None, body=None, text_center=True, text_color="black"):
        self.icon = Icon((self.icon_rect.width - 20, self.icon_rect.height - 20), "icons", f"{icon_type}.png")
        self.icon.rect.center = self.icon_rect.center

        self.text_group = TextGroup(self.content_rect)
        self.text_group.set_text(title=title, content=body, center=text_center, text_color=text_color)
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def __set_transparency(self, transparency):
        """Set the transparency of the notification.

        Args:
            transparency (int): The transparency level from 0 to 255.
        """
        self.surface.set_alpha(transparency)
        self.text_group.set_transparency(transparency)
        self.icon.set_transparency(transparency)

    def __draw_bg(self):
        pygame.draw.rect(self.surface, "white", self.surface.get_rect(), border_radius=15)
        self.screen.blit(self.surface, self.main_rect.topleft)

    def __update(self):
        current_time = pygame.time.get_ticks()
        if self.active:
            if (current_time - self.start_time >= self.duration and
                    not self.main_rect.collidepoint(pygame.mouse.get_pos())):
                self.active = False

    def draw(self):
        self.__update()
        if self.active:
            self.__draw_bg()
        if self.text_group and self.active:
            self.text_group.draw_text()
        if self.icon and self.active:
            self.icon.draw()


class Settings:
    config_file = ConfigFile()
    FPS = config_file.getint('SCREEN--SETTINGS', 'FPS')
    screen_size = config_file.get_screen_size()
    #  Container : Top, left, right
    margin = {'container': {"top": 55, "bottom": screen_size[1] - 100, "left": 240, "right": 240},
              "between": {"title": 70, "variable": 40}}

    def __init__(self, screen: pygame.surface.Surface = None):
        pygame.init()
        self.screen = screen if screen else pygame.display.set_mode(self.config_file.get_screen_size())

        pygame.display.set_caption("Settings")

        self.main_container = pygame.rect.Rect(self.margin["container"]["left"], self.margin["container"]["top"],
                                               self.screen_size[0] - self.margin["container"]["left"] -
                                               self.margin["container"]["right"],
                                               self.screen_size[1] - self.margin["container"]["top"])

        self.clock = pygame.time.Clock()
        self.get_settings_sections()
        self.main_container_group = MainContainerGroup(self.main_container, self.margin)
        self.pop_up = PopUp()
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
        title_text = Text(section_title, self.config_file.get_title_size(), (255, 255, 255), pos,
                          side='midtop', bold=True)

        self.main_container_group.add(title_text)

        for variable_name in self.config_file.options(section_name):
            _text = Text(f"{variable_name} :".upper(), self.config_file.get_body_size(),
                         (255, 255, 255), (self.main_container.left, self.main_container_group.get_last_rect_y() +
                                           self.margin['between']['variable']), side="topleft")
            try:
                variable_value = self.config_file.getint(section_name, variable_name)
                authorized_char = ((48, 57), 57)
            except ValueError:
                variable_value = self.config_file.get(section_name, variable_name)
                authorized_char = ((48, 58), 46)
            if variable_name == "fps":
                max_character = 3
            elif variable_name == 'port':
                max_character = 5
            elif variable_name == 'address':
                max_character = 15
            else:
                max_character = len(str(variable_value)) + 1

            if section_title in ["DIRECTION", "ACTIONS"]:
                _input = OneKeyInput(variable_value, ("white", "black"),
                                     (self.main_container.right, _text.rect.centery), f"{section_name}|{variable_name}")
            else:
                _input = Input(f"{variable_value}".upper(), self.config_file.get_body_size(), ("white", "black"),
                               (self.main_container.right, _text.rect.centery),
                               max_character=max_character, authorized_char=authorized_char,
                               _id=f"{section_name}|{variable_name}")
            self.main_container_group.add(_text)
            self.main_container_group.add(_input)

    def save(self):
        for input_component in self.main_container_group.inputs():
            section, option = input_component.id.split("|")
            self.config_file.edit_value(section, option, input_component.text.str)
        for input_key in self.main_container_group.input_key():
            section, option = input_key.id.split("|")
            self.config_file.edit_value(section, option, str(input_key.value))

    def verify_input_values(self) -> bool:
        #  I'm going to check a little by hand if each value of the inputs is respected, so for that I'm going to do
        #  lots of if else and as soon as a value is not correct, then result = False. If at the end of the loop result
        #  is still=True then all the checks have passed.
        result = True
        for input_component in self.main_container_group.inputs():
            section, option = input_component.id.split("|")
            if option == "fps":
                try:
                    if not 20 <= int(input_component.text.str) <= 144:
                        result = False
                #  If there is a ValueError exception, it is because of int() and then it means that the field contains
                #  text
                except ValueError:
                    result = False
            elif option == "address":
                #  For the address, we just check if it doesn't start or end with a period. We also check if the values
                #  of the IP addresses are between 0 and 255 inclusive. We check of course that they are int and not str
                value_split = input_component.text.str.split(".")
                if input_component.text.str[0] == "." or input_component.text.str[-1] == ".":
                    result = False
                #  An IP address is made up of 4 numbers from 0 to 255 separated by a dot, so the shortest is 0.0.0.0
                #  and the longest is 255.255.255.255
                elif not 7 <= len(input_component.text.str) <= 15:
                    result = False
                elif "." not in input_component.text.str:
                    result = False
                count = 0
                for value in value_split:
                    count += 1
                    try:
                        if not 0 <= int(value) <= 255:
                            result = False
                            break
                    except ValueError:
                        result = False
                        break
                if not 3 <= count <= 5:
                    result = False
            elif option == "port":
                try:
                    if not 10 ** 2 <= int(input_component.text.str) <= 10 ** 5:
                        result = False
                #  If there is a ValueError exception, it is because of int() and then it means that the field contains
                #  text
                except ValueError:
                    result = False

        return result

    def run(self) -> None:
        running = True
        while running:
            self.draw_bg()

            _dt = self.clock.tick(self.FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    close()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.verify_input_values():
                            running = False
                        else:
                            if not self.pop_up.active:
                                self.pop_up.notify(icon_type='error', title="Warning",
                                                   body="One or more values are not correct, please correct them.")
                            else:
                                running = False
                    else:
                        for component in self.main_container_group.sprites():
                            if isinstance(component, Input):
                                component.write(event.key)
                        for component in self.main_container_group.get_clicked_input_key():
                            if 45 <= event.key <= 200 or event.key in component.special_values.keys():
                                component.set_value(event.key)
                                component.clicked = False

                elif event.type == pygame.MOUSEWHEEL:
                    self.main_container_group.scroll(event.y)

            self.main_container_group.custom_selector()
            self.main_container_group.custom_draw()
            self.pop_up.draw()
            # Update the display
            pygame.display.flip()

        if self.verify_input_values():
            self.save()
        else:
            pass


if __name__ == '__main__':
    Settings(pygame.display.set_mode(ConfigFile().get_screen_size())).run()
