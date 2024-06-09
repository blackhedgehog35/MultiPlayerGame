import pygame
import math


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

    def __init__(self, screen, size: tuple, pos: tuple, color, data_size):
        self.screen = screen
        self.data = ""
        self.size = size
        self.is_writing = False
        self.rect = pygame.Rect(pos[0], pos[1], self.size[0], self.size[1])
        self.color = color
        self.data_size = data_size
        self.data_text = Text(self.data, self.data_size, (self.rect.x + 5, self.rect.y + 5), (0, 0, 0))

    def write(self, letter):
        print(math.ceil(self.size[0] / self.data_size))
        if len(self.data) < math.ceil(self.size[0] / self.data_size):
            self.data += letter
            self.data_text.update_text(self.data)

    def update_data(self, data):
        data = self.data

    def display_data(self):
        self.data_text.draw(self.screen)

    def draw_input(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
