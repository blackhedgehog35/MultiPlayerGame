import os.path
import pygame.image


def load_animation(*path):
    return pygame.image.load(os.path.join("..", "assets", *path))
