import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self, screen, key):

        super().__init__()

        self.screen = screen
        self.color = f"#{key}"
        self.rect = pygame.rect.Rect
        self.rect.x = 0
        self.rect.y = 0
        self.draw()

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            self.rect.x = -1
        elif keys[pygame.K_d]:
            self.rect.x = 1
        else:
            self.rect.x = 0

        if keys[pygame.K_z]:
            self.rect.y = -1
        elif keys[pygame.K_s]:
            self.rect.y = 1
        else:
            self.rect.y = 0

        pass

    def move(self):
        pass

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.rect.x, self.rect.y), width=50)
