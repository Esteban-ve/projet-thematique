# on teste la robustesse des systèmes de classement
# pour mesurer statistiquement les écarts entre deux classements, on utilise la distance tau de Kendall.
# en gros, c'est le nombre de permutations permettant de passer d'un classement à l'autre, normalisé entre [-1,1]
# on y ajoutera MAE et Spearman

# On teste différentes configurations définies par : 
#       -un système de classement (tournoi à points, à élimination directe...)
#       -un type d'appariement (suisse, round robin, aléatoire)
#       -un nombre de joueurs
#       -une condition initiale le cas échéant

# Pour chaque métrique, on fait plein d'itérations pour différentes variances de niveau des joueurs (variable V)
# Cela nous donne des séries statistiques analysables. Pour chaque configuration, on pourra en déduire la robustesse, la sensibilité CI et la sensibilité
# au hasard.



from joueur import Joueur
import numpy as np
from random import shuffle
from scipy.stats import spearmanr, kendalltau
import matplotlib.pyplot as plt

### fonctions utiles ###

def MAE(a, b):
    assert len(a)==len(b)
    S=0
    for idx,elt in enumerate(a):
        i=0
        while b[i]!=elt:
            i+=1
        S+=abs(idx-i)
    return S/len(a)

### simulations de configurations ###
# chacune de ces fonctions renvoie un classement des joueurs
def tournoi_aleatoire(joueurs):
    try:
        shuffle(joueurs)
    except TypeError:
        print(joueurs)
        raise TypeError("shuffle!!")
    return joueurs

def tournoi_points_round_robin_tiebreaker_is_match(joueurs):
    joueurs2=joueurs.copy()
    points={j:0 for j in joueurs}
    while len(joueurs)>1:
        joueur=joueurs.pop()
        for j in joueurs:
            if joueur.niveau > j.niveau:
                points[joueur]+=1
            else:
                points[j]+=1
    classement = []
    classement.append(joueurs2[0])
    for j in joueurs2[1:]:
        i=0
        while i<len(classement) and points[j]>points[classement[i]]:
            i+=1
        if i<len(classement) and points[j]==points[classement[i]]:
            # tiebreaker : match
            if j.niveau > classement[i].niveau:
                classement.insert(i+1, j)
            else:
                classement.insert(i, j)
        else:
            classement.insert(i, j)
    return classement

n_joueurs = 20
n_tournois_simules = 500
ecart_entre_joueurs = 1

valeurs_V = np.linspace(0, 3, 50)

# métriques relevées à chaque tournoi, reset pour chaque nouvelle valeur de V
historique_MAE = []
historique_Kendall = []
historique_Spearman = []

# valeurs statistiques relevées pour chaque valeur de V, calculées avec les séries de n_tournois_simules tournois
moyenne_MAE = []
std_MAE = []
moyenne_Kendall = []
std_Kendall = []
moyenne_Spearman = []
std_Spearman = []


classement_tournoi = []
for V in valeurs_V:
    joueurs = {Joueur(str(i), i*ecart_entre_joueurs, V):i for i in range(n_joueurs)}  # chaque joueur représenté identifié par un nombre : utile pour utiliser
                                                                                      # les methodes spearmanr et kendalltau
    classement_reference = list(range(n_joueurs))   # joueurs classés du pire au meilleur
    historique_MAE = []
    historique_Kendall = [] 
    historique_Spearman = []
    for idx_tournoi in range(n_tournois_simules):
        classement_tournoi = tournoi_points_round_robin_tiebreaker_is_match(list(joueurs.keys()))
        classement_tournoi_num = [joueurs[joueur] for joueur in classement_tournoi]
        # calcul des metriques
        historique_Kendall.append(kendalltau(classement_reference, classement_tournoi_num))
        historique_Spearman.append(spearmanr(classement_reference, classement_tournoi_num))
        historique_MAE.append(MAE(classement_reference, classement_tournoi_num))
    moyenne_MAE.append(np.mean(historique_MAE))
    std_MAE.append(np.std(historique_MAE))
    moyenne_Kendall.append(np.mean(historique_Kendall))
    std_Kendall.append(np.std(historique_Kendall))
    moyenne_Spearman.append(np.mean(historique_Spearman))
    std_Spearman.append(np.std(historique_Spearman))


plt.title("moyenne MAE")
plt.plot(valeurs_V, moyenne_MAE)
plt.show()
plt.title("std MAE")
plt.plot(valeurs_V, std_MAE)
plt.show()
plt.title("moyenne Kendall")
plt.plot(valeurs_V, moyenne_Kendall)
plt.show()
plt.title("std Kendall")
plt.plot(valeurs_V, std_Kendall)
plt.show()
plt.title("moyenne Spearman")
plt.plot(valeurs_V, moyenne_Spearman)
plt.show()
plt.title("std Spearman")
plt.plot(valeurs_V, std_Spearman)
plt.show()