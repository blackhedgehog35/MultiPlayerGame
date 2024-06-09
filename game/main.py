import pygame.display
from programs.client import ClientNetwork
from programs.game import Game


if __name__ == '__main__':
    Game(pygame.display.set_mode((1100, 800)), ClientNetwork('86.253.205.36', 56349)).run()
