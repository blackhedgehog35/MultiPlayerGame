import pygame
from game import player
pygame.init()

screen = pygame.display.set_mode((1200, 800))


player = player.Player(screen, "ffffff")

running = True

while running:
    screen.fill("black")

    player.input()
    player.draw()

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            running = False
