import pygame as py
import sys
import time
import socket
import threading
import pickle

# === PARTIE RÉSEAU ===
game_state = {
    "balle_x": 500,
    "balle_y": 300,
    "velocity_balle_x": 6,
    "velocity_balle_y": 6,
    "joueur1_y": 250,
    "joueur2_y": 250,
    "points_joueur1": 0,
    "points_joueur2": 0
}

clients = []

#gerer la raquette du joueur 2
def handle_client(conn, player):
    global game_state
    while True:
        try:
            paddle_y = pickle.loads(conn.recv(1024))
            if player == 2:
                game_state["joueur2_y"] = paddle_y
        except:
            clients.remove(conn)
            conn.close()
            break

#mettre à jour la balle et envoyer l'état à tous les clients
def update_game():
    global game_state
    while True:
        game_state["balle_x"] += game_state["velocity_balle_x"]
        game_state["balle_y"] += game_state["velocity_balle_y"]

        #empêche la balle de sortir verticalement
        if game_state["balle_y"] <= 0 or game_state["balle_y"] >= 600:
            game_state["velocity_balle_y"] *= -1

        #collision avec joueur 1
        if game_state["balle_x"] <= 50 and game_state["joueur1_y"] <= game_state["balle_y"] <= game_state["joueur1_y"] + 100:
            hit_pos = (game_state["balle_y"] - game_state["joueur1_y"]) / 100
            game_state["velocity_balle_x"] = abs(game_state["velocity_balle_x"])
            game_state["velocity_balle_y"] = (hit_pos - 0.5) * 12

        #collision avec joueur 2
        if game_state["balle_x"] >= 950 and game_state["joueur2_y"] <= game_state["balle_y"] <= game_state["joueur2_y"] + 100:
            hit_pos = (game_state["balle_y"] - game_state["joueur2_y"]) / 100
            game_state["velocity_balle_x"] = -abs(game_state["velocity_balle_x"])
            game_state["velocity_balle_y"] = (hit_pos - 0.5) * 12

        #attribution des points
        if game_state["balle_x"] <= 0:
            game_state["points_joueur2"] += 1
            game_state["balle_x"], game_state["balle_y"] = 500, 300
        elif game_state["balle_x"] >= 1000:
            game_state["points_joueur1"] += 1
            game_state["balle_x"], game_state["balle_y"] = 500, 300

        #envoi aux clients
        for client in clients:
            try:
                client.send(pickle.dumps(game_state))
            except:
                clients.remove(client)

        time.sleep(1/60)

#configuration du serveur
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("0.0.0.0", 5555))
server.listen(1)
print("Serveur en attente pour Joueur 2...")
threading.Thread(target=update_game, daemon=True).start()

#accepter le joueur 2
def accept_client():
    conn, addr = server.accept()
    clients.append(conn)
    threading.Thread(target=handle_client, args=(conn, 2), daemon=True).start()
    print("Joueur 2 connecté !")

threading.Thread(target=accept_client, daemon=True).start()

# === PARTIE PYGAME ===
py.init() #lance pygame

root = py.display.set_mode((1000, 600))
py.display.set_caption("PONG")
fond = (0, 0, 0) #couleur du fond (noir), RGB
joueurs = (255, 255, 255) #couleur des joueurs (blanc), RGB
bouton = (255, 0, 0) #couleur des boutons(rouge), RGB

#positions initiales du joueur 1 (côté gauche)
joueur1_y = 250
paddle_y = joueur1_y

clock = py.time.Clock() #vérifie si la balle sort de l'écran
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
                game_state["points_joueur1"], game_state["points_joueur2"] = 0,0
                game_state["balle_x"], game_state["balle_y"] = 500, 300
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
        while show_timer and timer > 0:
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
        if game_state["points_joueur1"] >= 10:
            text_gagnant = "LE JOUEUR 1 A GAGNE!"
        elif game_state["points_joueur2"] >= 10:
            text_gagnant = "LE JOUEUR 2 A GAGNE!"
        else:
            text_gagnant = f"JOUEUR 1: {game_state['points_joueur1']} JOUEUR 2: {game_state['points_joueur2']}"

        #detecte si des touches sont pressées
        keys = py.key.get_pressed()
        
        #controles joueur 1
        if keys[py.K_z] and paddle_y - 5 >= 0:
            paddle_y -= 5
        if keys[py.K_s] and paddle_y + 105 <= 600:
            paddle_y += 5

        #mise à jour de la position de joueur1
        game_state["joueur1_y"] = paddle_y

        #affiche les joueurs
        py.draw.rect(root, joueurs, (40, game_state["joueur1_y"], 10, 100))
        py.draw.rect(root, joueurs, (950, game_state["joueur2_y"], 10, 100))
         
        #affiche la balle
        py.draw.circle(root, joueurs, (int(game_state["balle_x"]), int(game_state["balle_y"])), 10)
        
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