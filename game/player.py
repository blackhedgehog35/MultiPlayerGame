import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self, screen, key, position):

        super().__init__()

        self.screen = screen
        self.color = f"#{key}"
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.x = 0
        self.rect.y = 0
        self.direction = pygame.Vector2()
        self.speed = 1

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_q]:
            self.direction.x += -1
        elif keys[pygame.K_d]:
            self.direction.x += 1

        else:
            self.direction.x = 0

        if keys[pygame.K_z]:
            self.direction.y += -1
        elif keys[pygame.K_s]:
            self.direction.y += 1

        else:
            self.direction.y = 0


    def update(self, dt):

        self.rect.x += self.direction.x * self.speed * dt
        self.rect.y += self.direction.y * self.speed * dt

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
