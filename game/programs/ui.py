import pygame
from config import ConfigFile


def show_info(content, pos, side='topleft'):
    font = pygame.font.SysFont('Liberation Mono', 20)
    text_surface = font.render(str(content), True, (255, 255, 255))
    rect = text_surface.get_rect()
    setattr(rect, side, pos)
    pygame.display.get_surface().blit(text_surface, rect)


class Shapes:

    def __init__(self, screen, size: tuple, pos: tuple, color, shape, data, radius):
        self.screen = screen
        self.shape = shape
        self.color = color
        self.size = size
        self.data = data
        self.rect = pygame.Rect(pos, self.size)
        self.all_shapes = {
            "rect": lambda: pygame.draw.rect(self.screen, self.color, self.rect),
            "circle": lambda: pygame.draw.circle(self.screen, self.color, (self.rect.x, self.rect.y), radius),
            "line": lambda: pygame.draw.line(self.screen, self.color, self.rect,
                                             (self.rect.x + size[0], self.rect.y + self.size[1])),
            "rounded rect": lambda: self.draw_rounded_rectangle(self.screen, self.color, self.rect, radius),
            "none": lambda: self.draw_nothing()
        }

    def draw_rounded_rectangle(self, screen, color, rect, radius):
        x, y, width, height = rect

        pygame.draw.rect(screen, color, (x + radius, y, width - 2 * radius, height))
        pygame.draw.rect(screen, color, (x, y + radius, width, height - 2 * radius))

        pygame.draw.circle(screen, color, (x + radius, y + radius,), radius)
        pygame.draw.circle(screen, color, (x + width - radius, y + radius,), radius)
        pygame.draw.circle(screen, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(screen, color, (x + width - radius, y + height - radius,), radius)

    def draw_nothing(self):
        pass

    def draw(self, pos=None, size=None):
        if not pos:
            pos = (self.rect.x, self.rect.y)
        if not size:
            size = self.rect.size
        self.update_pos(pos)
        self.update_size(size)
        self.all_shapes.get(self.shape)()
        if self.data is not None:
            print(self.data)
            self.data.draw()

    def update_pos(self, pos):
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def update_size(self, size):
        self.rect.size = size


class Text:
    font_name = "COMIC SANS MS"

    def __init__(self, screen, text, size, pos, color=(255, 255, 255), side='center'):
        self.screen = screen
        self.color = color
        self.text_str = text
        self.size = size
        self.font = pygame.font.SysFont(self.font_name, self.size)
        self.pos = pos
        self.side = side

        self.text = self.font.render(str(self.text_str), True, self.color)
        self.width, self.heigth = self.text.get_size()
        self.rect = self.text.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update_text(self, text_str):
        self.text_str = text_str
        self.text = self.font.render(str(self.text_str), True, self.color)
        self.rect = self.text.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update_pos(self, pos):
        setattr(self.rect, self.side, pos)

    def draw(self):
        self.screen.blit(self.text, self.rect)


class Images:

    def __init__(self, screen, size, pos, image):
        self.screen = screen
        self.rect = pygame.Rect(pos, size)
        self.image = image

    def draw(self):
        self.screen.blit(self.image, self.rect)


class Input(Shapes):

    def __init__(self, screen, size: tuple, pos: tuple, color, shape: str, data_size, data=None, radius=5):
        super().__init__(screen, size, pos, color, shape, data, radius)
        self.data = ""
        self.is_writing = False
        self.data_size = data_size
        self.data_text = Text(self.screen, self.data, self.data_size, (self.rect.x + 5, self.rect.y + 5), (0, 0, 0))

    def write(self, key_pressed):
        if key_pressed == pygame.K_BACKSPACE:
            self.data = self.data[0:-1]

        elif self.data_text.text.get_size()[0] + 20 < self.size[0]:
            self.data += chr(key_pressed)
        self.data_text.update_text(self.data)

    def empty(self):
        self.data = ""
        self.data_text.update_text(self.data)

    def update_data(self, data):
        data = self.data

    def display_data(self):
        self.screen.blit(self.data_text.text, (self.rect.x + 5, self.rect.y + 5))


class Button(Shapes):

    def __init__(self, screen, size: tuple, pos: tuple, color, shape: str, effect: list, data=None, radius=5):
        super().__init__(screen, size, pos, color, shape, data, radius)
        self.all_effects = effect

    def click(self):
        for effect in self.all_effects:
            effect()

    def check_clicked(self, event):
        if self.rect.collidepoint(event.pos):
            self.click()


class Selector(Shapes):

    def __init__(self, screen, pos, color, list_to_display: list, shape:str, radius=5, data=None):
        self.list_to_display = list_to_display
        self.number = 0
        size = self.define_size()
        super().__init__(screen, size, pos, color, shape, data, radius)
        self.left_arrow = Button(self.screen, (self.size[0] / 2, self.size[1] / 2),
                                 (self.rect.x - 50, self.rect.centery), (0, 0, 0)
                                 , "circle", [lambda: self.add_number(-1)])
        self.right_arrow = Button(self.screen, (self.size[0] / 2, self.size[1] / 2),
                                  (self.rect.x + self.rect.width + 50, self.rect.centery), (0, 0, 0)
                                  , "circle", [lambda: self.add_number(1)])

    def define_size(self):
        all_data_size = []

        for data in self.list_to_display:
            all_data_size.append((data.width, data.heigth))

        return all_data_size[self.number]

    def draw_all(self):
        self.screen.blit(self.list_to_display[self.number].text, self.rect)
        self.right_arrow.draw((self.rect.x + self.rect.width + 50, self.rect.centery))
        self.left_arrow.draw((self.rect.x - 50, self.rect.centery))
        self.draw(size=self.define_size())

    def add_number(self, amount):
        self.number += amount
        if self.number >= len(self.list_to_display):
            self.number = 0
        elif self.number <= -1:
            self.number = len(self.list_to_display) - 1
