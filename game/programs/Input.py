import pygame

class Input:

    def __init__(self, screen, size, pos, color):
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
