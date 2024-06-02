import pygame
pygame.init()

screen = pygame.display.set_mode((1200, 800))

running = True

while running:

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            running = False