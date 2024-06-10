import pygame


class Shapes:

    def __init__(self, screen, size: tuple, pos: tuple, color, shape, image):
        self.screen = screen
        self.shape = shape
        self.color = color
        self.size = size
        self.image = image
        self.rect = pygame.Rect(pos, self.size)
        self.all_shapes = {
            "rect": pygame.draw.rect,
            "cercle": pygame.draw.circle,
            "line": pygame.draw.line,
            "rounded rect": self.draw_rounded_rectangle
        }

    def draw_rounded_rectangle(self, screen, color, rect):
        radius = 25
        x, y, width, height = rect

        pygame.draw.rect(screen, color, (x + radius, y, width - 2 * radius, height))
        pygame.draw.rect(screen, color, (x, y + radius, width, height - 2 * radius))

        pygame.draw.circle(screen, color, (x + radius, y + radius, ), radius)
        pygame.draw.circle(screen, color, (x + width - radius, y + radius,), radius)
        pygame.draw.circle(screen, color, (x + radius, y + height - radius), radius)
        pygame.draw.circle(screen, color, (x + width - radius, y + height - radius,), radius)

    def draw(self):
        self.all_shapes.get(self.shape)(self.screen, self.color, self.rect)
        if self.image is not None:
            self.image.draw()


class Text:
    font_name = "COMIC SANS MS"

    def __init__(self, text, size, pos, color=(255, 255, 255), side='center'):
        self.color = color
        self.text_str = text
        self.size = size
        self.font = pygame.font.SysFont(self.font_name, self.size)
        self.pos = pos
        self.side = side

        self.text = self.font.render(str(self.text_str), True, self.color)
        self.rect = self.text.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update_text(self, text_str):
        self.text_str = text_str
        self.text = self.font.render(str(self.text_str), True, self.color)
        self.rect = self.text.get_rect()
        setattr(self.rect, self.side, self.pos)

    def update_pos(self, pos):
        setattr(self.rect, self.side, pos)

    def draw(self, screen: pygame.surface.Surface):
        screen.blit(self.text, self.rect)


class Images:

    def __init__(self, screen, size, pos, image):
        self.screen = screen
        self.rect = pygame.Rect(pos, size)
        self.image = image

    def draw(self):
        self.screen.blit(self.image, self.rect)


class Input(Shapes):

    def __init__(self, screen, size: tuple, pos: tuple, color, shape: str, data_size, image=None):
        super().__init__(screen, size, pos, color, shape, image)
        self.data = ""
        self.is_writing = False
        self.data_size = data_size
        self.data_text = Text(self.data, self.data_size, (self.rect.x + 5, self.rect.y + 5), (0, 0, 0))

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

    def __init__(self, screen, size: tuple, pos: tuple, color, shape: str, effect: list, image=None):
        super().__init__(screen, size, pos, color, shape, image)
        self.all_effects = effect

    def click(self):
        for effect in self.all_effects:
            effect()

    def check_clicked(self, event):
        if self.rect.collidepoint(event.pos):
            self.click()
