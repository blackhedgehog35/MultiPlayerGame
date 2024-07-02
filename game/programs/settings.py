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
                    #  break because in theory, there is just one component that is activate
                    break
        return list_component


class Text(pygame.sprite.Sprite):
    config_file = config.ConfigFile()

    def __init__(self, text, size, color, pos, side='topleft', bold=False):
        super().__init__()
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

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Input(pygame.sprite.Sprite):
    config_file = config.ConfigFile()
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


"""
Pour le OneKeyInput, ce que je veux :
Si aucune valeur au tout début, j'aimerai qu'il y ai marqué "Press a key" par défault, et lorsqu'on survole (à la façon 
du input) ce soit sélectionner et genre là si on appuie sur une touche alors ça écrive cette touche et c'est plus sélectionné
À partir de là, quand on survole ça met le petit truc de couleur comme d'hab mais quand pn clique, ça repasse en mode "Press a key".
Quand on sort du rectangle, si on clique pas ça reste encore en "Press a key" mais dès qu'on clique en dehors du rectangle,
ça remet la valeur d'avant. Je sais pas si c'est très clair...
"""


class OneKeyInput(pygame.sprite.Sprite):
    config_file = config.ConfigFile()
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


class Settings:
    config_file = config.ConfigFile()
    FPS = config_file.getint('SCREEN--SETTINGS', 'FPS')
    screen_size = config_file.get_screen_size()
    #  Container : Top, left, right
    margin = {'container': {"top": 55, "bottom": screen_size[1] - 100, "left": 240, "right": 240},
              "between": {"title": 70, "variable": 40}}
    char = {}
    special_char = []

    def __init__(self, screen: pygame.surface.Surface):
        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.screen = screen
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

        pos = list(self.main_container_group.inputs())[0].pos
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
        #  Je vais vérifier un peu à la main si chaque valeur des inputs est respecter, donc pour ça je vais faire plein
        #  de if else et dès qu'une valeur n'est pas correct, alors result = False. Si en fin de boucle result est encore=True
        #  alors c'est que tout les vérifications sont passé.
        result = True
        for input_component in self.main_container_group.inputs():
            section, option = input_component.id.split("|")
            if option == "fps":
                try:
                    if not 20 <= int(input_component.text.str) <= 144:
                        result = False
                # Si il y a une exception ValueError, c'est à cause du int() et alors ça veut dire que le champ
                # comporte du texte
                except ValueError:
                    result = False
            elif option == "address":
                #  Pour l'adresse, on vérifie juste si ça ne commence ou ne termine pas par un point
                #  On regarde également si les valeurs des adresses ip sont bien entre 0 et 255 compris.
                #  On vérifie bien sur que c'est des int et pas des str
                value_split = input_component.text.str.split(".")
                if input_component.text.str[0] == "." or input_component.text.str[-1] == ".":
                    result = False
                #  Une adresse ip est composé de 4 numéros de 0 à 255 séparé par un point donc le plus court c'est
                #  0.0.0.0 et le plus long c'est 255.255.255.255
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
                # Si il y a une exception ValueError, c'est à cause du int() et alors ça veut dire que le champ
                # comporte du texte
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
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
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
            # Update the display
            pygame.display.flip()

        if self.verify_input_values():
            self.save()
        else:
            print("Values Not Correct")


if __name__ == '__main__':
    Settings(pygame.display.set_mode(config.ConfigFile().get_screen_size())).run()
