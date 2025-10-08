import pygame as py
import sys
import socket
import pickle

#connexion au serveur du joueur 1
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("remplace l'ip par celle de ton ami")) #adresse IP du joueur 1

py.init()
root = py.display.set_mode((1000,600))
py.display.set_caption("PONG")
fond = (0,0,0)
joueurs = (255,255,255)
bouton = (255,0,0)

clock = py.time.Clock()
text = py.font.Font(None,40)

paddle_y = 250
game_start = True

while True:
    for event in py.event.get():
        if event.type == py.QUIT:
            py.quit()
            sys.exit()

    keys = py.key.get_pressed()
    #contrôles joueur 2 (P/M)
    if keys[py.K_p] and paddle_y - 5 >= 0:
        paddle_y -=5
    if keys[py.K_m] and paddle_y + 105 <= 600:
        paddle_y +=5

    #envoie position au serveur
    client.send(pickle.dumps(paddle_y))

    #reçoit état du jeu
    game_state = pickle.loads(client.recv(1024))

    #affichage
    root.fill(fond)
    py.draw.rect(root,joueurs,(40,game_state["joueur1_y"],10,100))
    py.draw.rect(root,joueurs,(950,game_state["joueur2_y"],10,100))
    py.draw.circle(root,joueurs,(int(game_state["balle_x"]),int(game_state["balle_y"])),10)

    #score
    if game_state["points_joueur1"]>=10:
        text_gagnant = "LE JOUEUR 1 A GAGNE!"
    elif game_state["points_joueur2"]>=10:
        text_gagnant = "LE JOUEUR 2 A GAGNE!"
    else:
        text_gagnant = f"JOUEUR 1: {game_state['points_joueur1']} JOUEUR 2: {game_state['points_joueur2']}"

    root.blit(text.render(text_gagnant,True,joueurs),(300,10))
    py.display.flip()

    clock.tick(60)
