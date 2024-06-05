import pygame


class Player(pygame.sprite.Sprite):

    def __init__(self, screen, key, position):

        super().__init__()

        self.screen = screen
        self.color = f"#{key}"
        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.centerx = position[0]
        self.rect.centery = position[1]
        self.direction = pygame.Vector2()
        self.speed = 100

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_q] and keys[pygame.K_d]:
            self.direction.x = 0
        elif keys[pygame.K_q]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1

        else:
            self.direction.x = 0

        if keys[pygame.K_z] and keys[pygame.K_s]:
            self.direction.y = 0
        if keys[pygame.K_z]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1

        else:
            self.direction.y = 0

    def update(self, dt):

        next_rect_x = self.rect.x + self.direction.x * self.speed * dt
        next_rect_y = self.rect.y + self.direction.y * self.speed * dt

        if next_rect_x >= 0 and next_rect_x <= self.screen.get_width():
            self.rect.x += self.direction.x * self.speed * dt
        if next_rect_y >= 0 and next_rect_y <= self.screen.get_height():
            self.rect.y += self.direction.y * self.speed * dt

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

    def set_attribute(self, attribute, value):
        attribute = value
