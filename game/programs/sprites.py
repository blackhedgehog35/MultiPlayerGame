import pygame
from config import ConfigFile


class CustomSpriteGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.screen = pygame.display.get_surface()

        #  camera offset
        self.offset = pygame.math.Vector2()
        self.half_w = self.screen.get_width() // 2
        self.half_h = self.screen.get_height() // 2
        config_file = ConfigFile()
        x = config_file.getint('CAMERA', 'margin-x')
        y = config_file.getint('CAMERA', 'margin-y')
        self.camera_borders = {'left': x, 'right': x, 'top': y, 'bottom': y}
        w = self.screen.get_width() - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.screen.get_height() - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(x, y, w, h)

    def find(self, key):
        for sprite in self.sprites():
            try:
                if sprite.KEY == key:
                    return sprite
            finally:
                pass

    def center_target_camera(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h

    def box_target_camera(self, target):
        if target.rect.left < self.camera_rect.left:
            self.camera_rect.left = target.rect.left
        elif target.rect.right > self.camera_rect.right:
            self.camera_rect.right = target.rect.right

        if target.rect.top < self.camera_rect.top:
            self.camera_rect.top = target.rect.top
        elif target.rect.bottom > self.camera_rect.bottom:
            self.camera_rect.bottom = target.rect.bottom

        self.offset.x = self.camera_rect.left - self.camera_borders['left']
        self.offset.y = self.camera_rect.top - self.camera_borders['top']

    def custom_draw(self, player):
        self.box_target_camera(player)
        for sprite in sorted(self.sprites(), key=lambda sprite_targeted: sprite_targeted.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            sprite.draw(offset_pos)


class Sprite(pygame.sprite.Sprite):
    config_file = ConfigFile()
    #  This is the margin to obtain the player's position, because in a 2d game viewed from height, the positions are
    #  defined in relation to the foot and not in the middle of the rectangle.
    speed = 250
    w = 30
    h = 30
    #  This is the depht of the hitbox
    depht = 5
    hitbox_w = w - 5

    def __init__(self, key, start_pos, group):
        self.KEY = key
        super().__init__(group)

        self.screen = pygame.display.get_surface()
        self.color = f"#{self.KEY}"

        self.pos = pygame.math.Vector2()
        self.pos.x, self.pos.y = start_pos
        self.direction = pygame.Vector2()

        self.rect = pygame.Rect(0, 0, self.w, self.h)
        self.rect.midbottom = (self.pos.x, self.pos.y)

        self.hitbox = pygame.Rect(0, 0, self.hitbox_w, self.depht)
        x, y = self.rect.centerx, self.rect.bottom + self.hitbox.height / 3
        self.hitbox.midbottom = (x, y)

    def input(self):
        keys = pygame.key.get_pressed()

        if keys[self.config_file.key.left] and keys[self.config_file.key.right]:
            self.direction.x = 0
        elif keys[self.config_file.key.left]:
            self.direction.x = -1
        elif keys[self.config_file.key.right]:
            self.direction.x = 1

        else:
            self.direction.x = 0

        if keys[self.config_file.key.top] and keys[self.config_file.key.bottom]:
            self.direction.y = 0
        elif keys[self.config_file.key.top]:
            self.direction.y = -1
        elif keys[self.config_file.key.bottom]:
            self.direction.y = 1

        else:
            self.direction.y = 0

        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

    def update(self, dt):
        #  next_rect_x = self.pos.x + self.direction.x * self.speed * dt
        #  next_rect_y = self.pos.y + self.direction.y * self.speed * dt

        self.pos.x += self.direction.x * self.speed * dt
        self.pos.y += self.direction.y * self.speed * dt

        #  if 0 <= next_rect_x <= self.screen.get_width():
        self.rect.x = self.pos.x
        #  if 0 <= next_rect_y <= self.screen.get_height():
        self.rect.y = self.pos.y

        x, y = self.rect.centerx, self.rect.bottom + self.hitbox.height / 3
        self.hitbox.midbottom = (x, y)

    def draw(self, pos=None):
        if pos:
            x, y = pos
            pygame.draw.rect(self.screen, self.color, (x, y, self.rect.w, self.rect.h))
            hitbox_x, hitbox_y = x + (self.w-self.hitbox_w)/2, y + self.rect.h - 2 * self.hitbox.h / 3
            pygame.draw.rect(self.screen, 'white', (hitbox_x, hitbox_y, self.hitbox.w, self.hitbox.h))
        else:
            pygame.draw.rect(self.screen, self.color, self.rect)
            pygame.draw.rect(self.screen, 'white', self.hitbox)

    def set_attribute(self, current_position):
        self.pos.x, self.pos.y = current_position
