import pygame


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


class Input:

    def __init__(self, screen, size: tuple, pos: tuple, color):
        self.screen = screen
        self.data = ""
        self.is_writing = False
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.color = color

    def write(self, letter):
        self.data += letter

    def update_data(self, data):
        data = self.data

    def display_data(self):
        self.screen.blit(self.data, (self.rect.x + 5, self.rect.y + 5))

    def draw_input(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
