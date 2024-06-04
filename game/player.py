import pygame

class Player(pygame.sprite.Sprite):

    def __init__(self, screen, key):

        super().__init__()

        self.screen = screen
        self.color = f"#{key}"
        self.rect = pygame.Rect(60, 60, 10, 10)
        self.rect.x = 0
        self.rect.y = 0

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            self.rect.x += -1
        elif keys[pygame.K_d]:
            self.rect.x += 1

        if keys[pygame.K_z]:
            self.rect.y += -1
        elif keys[pygame.K_s]:
            self.rect.y += 1

    def move(self):
        pass

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
