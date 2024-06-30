import pygame
import math
from config import ConfigFile


def show_info(content, pos, side='topleft'):
    font = pygame.font.SysFont('Liberation Mono', 20)
    text_surface = font.render(str(content), True, (255, 255, 255))
    rect = text_surface.get_rect()
    setattr(rect, side, pos)
    pygame.display.get_surface().blit(text_surface, rect)


class Shapes:

    def __init__(self, screen, group, size: tuple, pos: tuple, color, shape, data, radius, title, title_size, side):
        self.screen = screen
        self.shape = shape
        self.color = color
        self.group = group
        self.group.append(self)
        self.size = size
        self.side = side
        self.pos = pos
        self.rect = pygame.Rect(self.pos, self.size)
        self.data = data
        self.title = title
        self.title_size = title_size
        self.init_title()
        self.all_shapes = {
            "rect": lambda: pygame.draw.rect(self.screen, self.color, self.rect),
            "circle": lambda: pygame.draw.circle(self.screen, self.color, (self.rect.x, self.rect.y), radius),
            "line": lambda: pygame.draw.line(self.screen, self.color, self.rect,
                                             (self.rect.x + size[0], self.rect.y + self.size[1])),
            "rounded rect": lambda: self.draw_rounded_rectangle(self.screen, self.color, self.rect, radius),
            "none": lambda: self.draw_nothing()
        }

        setattr(self.rect, self.side, self.pos)

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

    def init_title(self):
        if self.title is not None:
            self.title = Text(self.screen, self.group, self.title, self.title_size, (self.rect.centerx, self.rect.centery - self.size[1] / 2 - 20), (200, 200, 200), "center")


    def draw(self, pos=None, size=None):
        if pos is not None:
            self.update_pos(pos)
        if size is not None:
            self.update_size(size)

        self.all_shapes.get(self.shape)()
        if self.data is not None:
            self.data.update_pos(self.rect.center)
            self.data.draw()
        if self.title is not None:
            self.title.update_pos((self.rect.centerx, self.rect.centery - self.size[1] / 2 - 20))
            self.title.draw()

    def update_pos(self, pos):
        self.pos = pos
        setattr(self.rect, self.side, self.pos)

    def update_size(self, size):
        self.rect.size = size
        setattr(self.rect, self.side, self.pos)


class Text:
    font_name = "COMIC SANS MS"

    def __init__(self, screen, group, text, size, pos, color=(255, 255, 255), side='center'):
        self.screen = screen
        group.append(self)
        self.color = color
        self.text_str = text
        self.size = size
        self.font = pygame.font.SysFont(self.font_name, self.size)
        self.pos = pos
        self.side = side

        self.text = self.font.render(str(self.text_str), True, self.color)
        self.width, self.heigth = self.text.get_size()
        self.rect = self.text.get_rect()
        self.update_pos(pos)


    def update_text(self, text_str):
        self.text_str = text_str
        self.text = self.font.render(str(self.text_str), True, self.color)
        self.rect = self.text.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update_pos(self, pos):
        setattr(self.rect, self.side, pos)

    def draw(self):
        self.width, self.heigth = self.text.get_size()
        self.screen.blit(self.text, self.rect)


class Images:

    def __init__(self, group, screen, size, pos, image):
        self.screen = screen
        group.append(self)
        self.rect = pygame.Rect(pos, size)
        self.image = image
        self.image = pygame.transform.scale(self.image, size)
        self.width, self.heigth = self.rect.size

    def draw(self):
        self.width, self.heigth = self.image.get_size()
        self.screen.blit(self.image, ((self.rect.x - self.width / 2, self.rect.y - self.heigth / 2), self.rect.size))


class Input(Shapes):

    def __init__(self, screen, group, size: tuple, pos: tuple, bg_color, shape: str, data: str, radius=5, title=None, title_size=None, side="center"):
        self.data_size = math.ceil(size[1] * 1.333 - 10)
        self.data_text = data
        self.data = Text(screen, group, self.data_text, self.data_size, (0, 0), (0, 0, 0))

        super().__init__(screen, group, size, pos, bg_color, shape, self.data, radius, title, title_size, side)
        self.is_writing = False

    def write(self, key_pressed):
        if key_pressed == pygame.K_BACKSPACE:
            # we replace the variable with the same variable but without the last letter
            self.data_text = self.data_text[0:-1]

        elif self.data.text.get_size()[0] + 20 < self.size[0] and key_pressed < 110000:
            self.data_text += chr(key_pressed)

        self.data.update_text(self.data_text)

    def empty(self):
        self.data.update_text("")

    def check_clicked(self, event):
        if self.rect.collidepoint(event.pos):
            self.is_writing = True
        else:
            self.is_writing = False

    def check_key(self, event):
        if self.is_writing:
            self.write(event.key)

    def get_data(self, data):
        data = self.data.text_str



class Button(Shapes):

    def __init__(self, screen, group, size: tuple, pos: tuple, color, shape: str, effect: list, data=None, radius=5, title=None, title_size=None, side="center"):
        super().__init__(screen, group, size, pos, color, shape, data, radius, title, title_size, side)
        self.all_effects = effect

    def click(self):
        for effect in self.all_effects:
            effect()

    def check_clicked(self, event):
        if self.rect.collidepoint(event.pos):
            self.click()


class Selector(Shapes):

    def __init__(self, screen, group, pos, color, list_to_display: list, shape: str, radius=5, data=None, title=None, title_size=None, side="center"):
        self.list_to_display = list_to_display
        self.number = 0
        size = self.define_size()
        self.arrows_size = (25, 25)
        super().__init__(screen, group, size, pos, color, shape, data, radius, title, title_size, side)
        self.left_arrow = Button(self.screen, group, self.arrows_size,
                                 (0, 0), color, "rect", [lambda: self.add_number(-1)], side="center")
        self.right_arrow = Button(self.screen, group, self.arrows_size,
                                  (0, 0), color, "rect", [lambda: self.add_number(1)], side="center")

    def define_size(self):
        all_data_size = []

        for data in self.list_to_display:
            all_data_size.append((data.width, data.heigth))

        return all_data_size[self.number]

    def draw_all(self):
        self.draw(size=self.define_size())        # its size depends on the displayed word's size
        self.screen.blit(self.list_to_display[self.number].text, self.rect)
        self.right_arrow.draw((self.rect.x + self.rect.width + self.arrows_size[0], self.rect.centery))
        self.left_arrow.draw((self.rect.x - self.arrows_size[0], self.rect.centery))

    def add_number(self, amount):
        self.number += amount
        if self.number >= len(self.list_to_display):
            self.number = 0
        elif self.number <= -1:
            self.number = len(self.list_to_display) - 1

    def get_displayed_value(self, data):
        data = self.list_to_display[self.number]

    def check_arrows_clicked(self, event):
        self.left_arrow.check_clicked(event)
        self.right_arrow.check_clicked(event)


class Cursor(Shapes):

    def __init__(self, screen, group, size, pos, color, data: int, scale, title=None, title_size=None, side="center"):
        super().__init__(screen, group, size, pos, (0, 255, 0), "rect", None, 5, title, title_size, side)
        self.bar = Shapes(screen, group, (data, size[1]), (self.rect.x, self.rect.y), color, "rect", None, 5, None, None, "topleft")
        self.pointer = Shapes(screen, group, (20, 20), (self.rect.x + data, self.rect.centery), color, "circle", None, size[0] / 10, None, None, "topleft")
        self.scale = scale
        self.nb = data * self.scale
        self.is_clicked = False

    def draw_all(self):
        self.draw()
        self.bar.draw((self.rect.x, self.rect.y))
        self.pointer.draw()

    def check_clicked(self, event):
        if self.rect.collidepoint(event.pos):
            if self.pointer.rect.x < self.size[0] + self.rect.x:
                self.is_clicked = True
            else:
                self.is_clicked = False

            self.click(event)

    def click(self, event):
        x, y = event.pos
        if self.is_clicked:
            self.pointer.rect.x = x
            self.nb = (x - self.rect.x) * self.scale
            self.bar.update_size(((x - self.rect.x), self.rect.height))
