"""on cherche à savoir à quelle vitesse des joueurs partant tous du même elo mais
ayant des niveaux différents sont triés par le score elo.
Pour ça, on fait des round robins avec un pool de joueurs à répétition puis
on observe l'évolution de l'elo des joueurs et le taux de changement du score elo.
Ce dernier est mesuré en norme2 et en norme infinie, avec des résultats par ailleurs similaires.
Il faudrait ajouter les métriques spearman/mae/topk.
Ultérieurement on voudrait aussi observer la vitesse de convergence de l'elo d'un nouveau
joueur arrivant dans un ensemble de joueurs déjà 'stabilisés'.

Jsp à quel point c'est hors-sujet mais le prof en avait parlé je crois alors voilà..."""
#TODO ajouter les métriques spearman/mae/topk
#TODO nouveau joueur dans pool de joueurs déjà stabilisés

#imports
from joueur import Joueur
import matplotlib.pyplot as plt

# constantes
VICTOIRE = 1
DEFAITE = 0
NUL = 0.5  # inutile pour l'instant mais bon on sait jamais

# init
nb_tournois = 20
nb_joueurs = 50
variance = 2
offset = 40
ecart = 0.5
K = 20
participants  = [Joueur(str(i), offset+i*ecart, variance, K) for i in range(nb_joueurs)]
resultats_participants = {participant:0 for participant in participants}  # reset à chaque tournoi, +1 pour victoire, +0 pour défaite
ES_participants = {participant:0 for participant in participants}       # reset à chaque tournoi,à chaque rencontre on ajoute l'expected score
historique_elo_participants = {participant:[participant.elo] for participant in participants}
taux_changement_elo = {participant:[] for participant in participants}
historique_norme_inf = []
historique_norme_2 = []

# loop
for idx_tournois in range(nb_tournois):
    #round robin
    resultats_participants = {participant:0 for participant in participants}
    ES_participants = {participant:0 for participant in participants}
    for idx_j1 in range(len(participants)):
        for idx_j2 in range(idx_j1+1, len(participants)):
            j1 = participants[idx_j1]
            j2 = participants[idx_j2]
            difference_elo = j2.elo - j1.elo
            expected_score = 1 / (1 + 10 ** (difference_elo / 400))
            ES_participants[j1]+=expected_score
            ES_participants[j2]+=(1-expected_score)
            if j1.niveau < j2.niveau: # défaite j1
               # j1.elo = j1.elo + j1.K * (DEFAITE - expected_score)
               # j2.elo = j2.elo + j2.K * (VICTOIRE - (1-expected_score))
               resultats_participants[j2]+=1
            else:  # victoire j1
                # j1.elo = j1.elo + j1.K * (VICTOIRE - expected_score)
                # j2.elo = j2.elo + j2.K * (DEFAITE - (1-expected_score))
                resultats_participants[j1]+=1

    # calcul des elo après tournoi
    for participant in participants:
        participant.elo = participant.elo + participant.K * (resultats_participants[participant] - ES_participants[participant])

    # calcul du taux de changement des elo et update des historiques
    for participant in participants:
        taux_changement_elo[participant] = participant.elo - historique_elo_participants[participant][-1]
        historique_elo_participants[participant].append(participant.elo)
    
    # norme inf
    historique_norme_inf.append(max([taux_changement_elo[participant] for participant in participants]))

    # norme_2
    historique_norme_2.append(pow(sum([taux_changement_elo[participant]**2 for participant in participants]),1/2))


#plot
for participant in participants:
    plt.plot(historique_elo_participants[participant])
plt.show()

plt.plot(historique_norme_inf)
plt.show()

plt.plot(historique_norme_2)
plt.show()