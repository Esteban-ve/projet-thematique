# on teste la robustesse des systèmes de classement
# pour mesurer statistiquement les écarts entre deux classements, on utilise la distance tau de Kendall.
# en gros, c'est le nombre de permutations permettant de passer d'un classement à l'autre, normalisé entre [-1,1]
# on y ajoutera MAE et Spearman

# On teste différentes configurations définies par : 
#       -un système de classement (tournoi à points, à élimination directe...)
#       -un type d'appariement (suisse, round robin, aléatoire)
#       -un nombre de joueurs
#       -une condition initiale le cas échéant

# Pour chaque métrique, on fait plein d'itérations pour différents V avec V la variance du niveau des joueurs et e l'écart entre chaque joueur
# Cela nous donne des séries statistiques analysables. Pour chaque configuration, on pourra en déduire la robustesse, la sensibilité CI et la sensibilité
# au hasard.



from joueur import Joueur
import numpy as np

n_joueurs = 20
n_tournois_simules = 500
ecart_entre_joueurs = 1

valeurs_V = np.linspace(0, 3, 50)

for V in valeurs_V:
    joueurs = [Joueur(str(i), i*ecart_entre_joueurs, V) for i in range(n_joueurs)]