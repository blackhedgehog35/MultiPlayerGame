import pygame


class Player(pygame.sprite.Sprite):
    margin_feet = 10
    #  This is the margin to obtain the player's position, because in a 2d game viewed from height, the positions are
    #  defined in relation to the foot and not in the middle of the rectangle.
    speed = 100

    def __init__(self, key, start_pos):
        self.KEY = key
        super().__init__()

        self.screen = pygame.display.get_surface()
        self.color = f"#{self.KEY}"

        self.pos = pygame.math.Vector2()
        self.pos.x, self.pos.y = start_pos
        self.direction = pygame.Vector2()

        self.rect = pygame.Rect(0, 0, 30, 30)
        self.rect.midbottom = (self.pos.x, self.pos.y + self.margin_feet)

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

        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()
        print(f'\r{self.direction}', end="              ")

    def update(self, dt):
        next_rect_x = self.rect.centerx + self.direction.x * self.speed * dt
        next_rect_y = self.rect.centery + self.direction.y * self.speed * dt

        if 0 <= next_rect_x <= self.screen.get_width():
            self.rect.x += self.direction.x * self.speed * dt
        if 0 <= next_rect_y <= self.screen.get_height():
            self.rect.y += self.direction.y * self.speed * dt

    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

    def set_attribute(self, current_position):
        self.pos.x, self.pos.y = current_position
