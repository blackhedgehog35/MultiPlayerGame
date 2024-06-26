import pygame.sprite

from ui import *

"""
Si t'y arrive, c'est parfait ! Je te met tout les trucs que j'ai remarqué mais bien évidemeent tu le fais quand tu veux et pas forcément dans l'ordre:
menu : 
- Présentation :
	- sorte de ligne à gauche à enlever car une seul page
	- Titre de section en grand au centre, en gras
	- disposition horizontal pour le nom de la variable et son input
	- Faire un truc un minimum centrer, avec system de container au centre pour mettre le nom des variables le + à gauche, et les inputs le plus à droite
	
	- Changer le design pour avoir un truc moins brute mais ça pourra être fait plus tard
	- Ne pas centrer le texte dans les inputs, choisir de les mettres à gauche ou à droite suivant ce que c'est
- UX :
	- Il faut faire en sorte qu'on ne puisse plus scroller quand c'est bon
	- Mettre une scroll bar quand tout ne tiendra plus sur une seul page. Sinon ne pas l'afficher.
	- Mettre une sorte de bar qui clignote dans les inputs pour faire comprendre qu'on peut saisir OU mettre le input en subriance comme les composants web
	- Interdire les charactères spéciaux
	- Enlever le exit button et mettre à la place un bouton échap qui fait que quand on veut sortir, on appuie sur Échap.
	
- Fonctionnement :
	- Connecter ça au config.ini
	- Problème pour mettre les points dans le input address
	- Mettre une clock pour limiter les FPS
"""


class Settings:

    pygame.init()
    bg_color = "black"
    space = 150

    def __init__(self, screen, mainwindow):
        self.screen = screen
        self.sprites = []
        self.around_text = Shapes(self.screen, [], (200, 60), (0, 20), (50, 50, 50), "rect", None, 5, None, None, "topleft")
        self.settings_text = Text(self.screen, [], "Settings", 30, (75, 25), (255, 255, 255), "topleft")
        self.exit_button = Button(self.screen, [], (40, 50), (30, 50), (255, 255, 255), "rounded rect", [self.stop_settings, mainwindow.run])

        self.line = Shapes(self.screen, [], (3, self.screen.get_height()), (210, 0), (50, 50, 50), "rect", None, 5, None, None, "topleft")

        self.code_text = Text(self.screen, self.sprites, "CODE:", 25, (750, self.space * 1), (200, 200, 200))
        self.pseudo_input = Input(self.screen, self.sprites, (150, 25), (750, self.space * 2), (200, 200, 200), "rect", "pseudo", 10, "PSEUDO", 20)
        self.port_input = Input(self.screen, self.sprites, (150, 25), (750, self.space * 3), (200, 200, 200), "rect", "", title="PORT", title_size=20)
        self.adress_input = Input(self.screen, self.sprites, (150, 25), (750, self.space * 4), (200, 200, 200), "rect", "", title="ADRESS IP", title_size=20)
        self.keyboard_selector = Selector(self.screen, self.sprites, (750, self.space * 5), (200, 200, 200),
                                          [Text(self.screen, self.sprites, "QWERTY", 18, (0, 0), (0, 0, 0)), Text(self.screen, self.sprites, "AZERTY", 18, (0, 0), (0, 0, 0))], "rect", title="KEYBOARD", title_size=20)
        self.key_selector = Selector(self.screen, self.sprites, (750, self.space * 6), (200, 200, 200),
                                     [Text(self.screen, self.sprites, "Z, Q, S ,W", 18, (0, 0), (0, 0, 0)), Text(self.screen, self.sprites, "K_up, K_right, K_left ,K_down", 18, (0, 0), (0, 0, 0))],
                                     "rect", title="KEYS", title_size=20)
        self.luminosity_cursor = Cursor(self.screen, self.sprites, (150, 10), (750, self.space * 7), (200, 200, 200), 40, 1/10, "LUMINOSITY", title_size=20)
        self.music_cursor = Cursor(self.screen, self.sprites, (150, 10), (750, self.space * 8), (200, 200, 200), 20, 1/10, "MUSIC", 20)


    def draw_bg(self):
        self.screen.fill(self.bg_color)

    def stop_settings(self):
        self.running = False

    def run(self):
        self.running = True

        while self.running:

            self.draw_bg()

            self.around_text.draw()
            self.settings_text.draw()
            self.exit_button.draw()

            self.line.draw()

            self.code_text.draw()
            self.pseudo_input.draw()
            self.adress_input.draw()
            self.port_input.draw()

            self.luminosity_cursor.draw_all()
            self.music_cursor.draw_all()


            self.keyboard_selector.draw_all()
            self.key_selector.draw_all()


            pygame.display.flip()


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_settings()
                    pygame.quit()

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    self.adress_input.check_clicked(event)
                    self.port_input.check_clicked(event)
                    self.pseudo_input.check_clicked(event)

                    self.exit_button.check_clicked(event)

                    self.keyboard_selector.check_arrows_clicked(event)
                    self.key_selector.check_arrows_clicked(event)

                    self.luminosity_cursor.check_clicked(event)
                    self.music_cursor.check_clicked(event)

                elif event.type == pygame.KEYDOWN:
                    self.pseudo_input.check_key(event)
                    self.adress_input.check_key(event)
                    self.port_input.check_key(event)

                elif event.type == pygame.MOUSEWHEEL:
                    if event.y > 0:

                        self.key_selector.rect.y += 5
                        for sprite in self.sprites:
                            sprite.rect.y += 5
                    else:
                        for sprite in self.sprites:
                            sprite.rect.y -= 5

                    print(self.key_selector.rect)
