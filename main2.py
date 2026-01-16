from tournoi import Tournoi
from joueur import Joueur
from match import Match
from math import ceil
import numpy as np

n_joueurs = 32
participants = [Joueur(str(i), 4000*i) for i in range(n_joueurs)]
m = Match("NIVEAU")
t = Tournoi(participants,m)
classement = t.elimination_directe(False)
for i in range(ceil(np.log2(n_joueurs))+1, 0, -1):
    for j,rang in classement.items():
        if rang==i:
            print(j.nom,end=" ")
    print("\n", end="")