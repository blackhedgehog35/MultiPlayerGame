import pygame
from game import player
pygame.init()

screen = pygame.display.set_mode((1200, 800))
screen.fill('white')

player = player.Player(screen, "ae4c5b")

running = True

while running:

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            running = False