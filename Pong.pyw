import pygame as py
import sys
import time
py.init() #lance pygame

root = py.display.set_mode((1000, 600))
py.display.set_caption("PONG")
fond = (0, 0, 0) #couleur du fond (noir), RGB
joueurs = (255, 255, 255) #couleur des joueurs (blanc), RGB
bouton = (255, 0, 0) #couleur des boutons(rouge), RGB

#positions initialles des joueurs
joueur1_y = joueur2_y = 250

#position initialle de la balle
balle_x, balle_y = 500, 300
depl_balle = True

#vitesse des joueurs et de la balle
velocity = 5
velocity_balle_x = velocity_balle_y = 6

clock = py.time.Clock() #vérifie si la balle sort de l'écran

#points des joueurs
points_joueur1, points_joueur2 = 0, 0

#definition de la taille et de la police d'écriture du texte
text = py.font.Font(None, 40)

#definit les positions des boutons quitter et lancer
bouton_lancer = py.Rect(400, 300, 180, 50)
bouton_quitter = py.Rect(420, 450, 150, 40)
bouton_menu = py.Rect(450, 550, 150, 40)
timer_pos = py.Rect(450, 250, 100, 50)

#variable pour lancer le jeu
game_start = False
show_timer = True
timer = 3
last_time = py.time.get_ticks()

#pour la frame des regles
text_rules = "joueur 1=Z,S / joueur 2=P,M"
text_frame = py.Rect(300, 400, 560, 50)
text_title = py.Rect(450, 100, 200, 100)

#tout ce qui est dans la fenetre
while True:
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            sys.exit()
        elif event.type == py.MOUSEBUTTONDOWN:
            if bouton_lancer.collidepoint(event.pos):
                game_start = True
                last_time = py.time.get_ticks()
            if bouton_menu.collidepoint(event.pos):
                game_start = False
                points_joueur1, points_joueur2 = 0, 0 #réinitialise les scores
                balle_x, balle_y = 500, 300
                depl_balle = True
            if bouton_quitter.collidepoint(event.pos):
                py.quit()
                sys.exit()
    
    root.fill(fond) #affiche le fond en noir
    
    #menu du jeu
    if not game_start:

        timer = 3 #reinitialisation du timer

        #affichage du titre du jeu
        py.draw.rect(root, fond, text_title)
        title_text = text.render("PONG", True, bouton)
        root.blit(title_text, (text_title.x + 5, text_title.y + 50))
        
        #bouton start
        py.draw.rect(root, joueurs, bouton_lancer)
        start_text = text.render("START", True, bouton)
        root.blit(start_text, (bouton_lancer.x + 50, bouton_lancer.y + 10))
        
        #affichage des regles
        py.draw.rect(root, fond, text_frame)
        text_rendu = text.render(text_rules, True, bouton)
        root.blit(text_rendu, (text_frame.x + 20, text_frame.y + 10))
        
        #bouton quitter
        py.draw.rect(root, joueurs, bouton_quitter)
        quit_text = text.render("QUITTER", True, bouton)
        root.blit(quit_text, (bouton_quitter.x + 5, bouton_quitter.y + 5))
    
    #le jeu
    elif game_start:

        #timer avant le debut de la partie
        while timer > 0:
            current_time = py.time.get_ticks()
            if current_time - last_time >= 1000: #1s ecoulee
                timer -= 1
                last_time = current_time
            
            #affichage du timer
            py.draw.rect(root, fond, timer_pos)
            timer_text = text.render(f"{timer}", True, bouton)
            root.blit(timer_text, (timer_pos.x + 30, timer_pos.y + 10))
            py.display.flip()
        
        show_timer = False #fin du timer

        #dit qui a gagné
        if points_joueur1 >= 10:
            text_gagnant = "LE JOUEUR 1 A GAGNE!"
            depl_balle = False
        elif points_joueur2 >= 10:
            text_gagnant = "LE JOUEUR 2 A GAGNE!"
            depl_balle = False
        else:
            text_gagnant = f"JOUEUR 1: {points_joueur1} JOUEUR 2: {points_joueur2}"
        
        #detecte si des touches sont pressées
        keys = py.key.get_pressed()
        
        #controles joueur 1
        if keys[py.K_z] and joueur1_y - velocity >= 0: #touche A pour monter
            joueur1_y -= velocity
        if keys[py.K_s] and joueur1_y + velocity + 100 <= 600: #touche S pour descendre
            joueur1_y += velocity
        
        #controles joueur 2
        if keys[py.K_p] and joueur2_y - velocity >= 0: #fleche HAUT pour monter
            joueur2_y -= velocity
        if keys[py.K_m] and joueur2_y + velocity + 100 <= 600: #fleche BAS pour descendre
            joueur2_y += velocity
        
        #déplacements de la balle
        if depl_balle:
            balle_x += velocity_balle_x
            balle_y += velocity_balle_y
        
        #empeche la balle de sortir de la fenetre
        if balle_y <= 10 or balle_y >= 590:
            velocity_balle_y *= -1
        if balle_x <= 0: #donne un point au joueur 2
            balle_x, balle_y = 500, 300
            points_joueur2 += 1
        elif balle_x >= 1000: #donne un point au joueur 1
            balle_x, balle_y = 500, 300
            points_joueur1 += 1
        
        #colision avec le joueur 1
        if balle_x <= 50 and joueur1_y <= balle_y <= joueur1_y + 100:
            hit_pos = (balle_y - joueur1_y) / 100
            velocity_balle_x = abs(velocity_balle_x)
            velocity_balle_y = (hit_pos - 0.5) * 12 #l'angle selon là où ça touche

        #collision avec le joueur 2
        if balle_x >= 950 and joueur2_y <= balle_y <= joueur2_y + 100:
            hit_pos = (balle_y - joueur2_y) / 100
            velocity_balle_x = -abs(velocity_balle_x)
            velocity_balle_y = (hit_pos - 0.5) * 12 #l'angle selon là où ça touche
        
        #affiche les joueurs
        py.draw.rect(root, joueurs, (40, joueur1_y, 10, 100))
        py.draw.rect(root, joueurs, (950, joueur2_y, 10, 100))
         
        #affiche la balle
        py.draw.circle(root, joueurs, (balle_x, balle_y), 10)
        
        #affiche le score
        score_text = text.render(text_gagnant, True, joueurs)
        root.blit(score_text, (300, 10))
        
        #affiche le bouton menu
        py.draw.rect(root, fond, bouton_menu)
        menu_text = text.render("MENU", True, bouton)
        root.blit(menu_text, (bouton_menu.x + 5, bouton_menu.y + 5))
        
    py.display.flip()
    #vitesse d'actualisation
    clock.tick(60)