from tournoi import Tournoi
from joueur import Joueur
from match import Match
from math import ceil
import numpy as np
import attribution as att

n_joueurs = 32
participants = [Joueur(str(i), 100*i) for i in range(n_joueurs)]
m = Match("NIVEAU")
t = Tournoi(participants,m)
"""
classement = t.elimination_directe(False)
for i in range(ceil(np.log2(n_joueurs))+1, 0, -1):
    for j,rang in classement.items():
        if rang==i:
            print(j.nom,end=" ")
    print("\n", end="")
"""

n_tournois = 5
n_iter = 100
points = {j:0 for j in participants}
classement_moyen = {j:0 for j in participants}    # moyenne du rang sur chaque saison
classements_par_joueur = {j:[] for j in participants}    # les classements obtenus apres chaque iteration
for _ in range(n_iter):
    # saison
    for _ in range(n_tournois):
        t = Tournoi(participants,m)
        classement = t.elimination_directe(False)
        points_temp = att.attribution_linéaire(classement)
        for j in participants:
            points[j]+=points_temp[j]
    classement_final = sorted(points.items(), key=lambda item: item[1])       # classement à la fin de la saison
    classement_final={classement_final[i][0]:i for i in range(len(classement_final))}
    for j in participants:
        classements_par_joueur[j].append(classement_final[j])

# par joueur : on compile les rangs obtenus à chaque itération
# on calcule moyenne et écart type
# les joueurs sont déja triés par niveau
# on a plus qu'à tracer les rangs moyens+barres d'erreur en fct du niveau réel


