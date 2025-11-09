# Classe tournoi qui gère le déroulement d'un tournoi(système suisse pour l'instant)
from random import random

J1_GAGNE = 1
J2_GAGNE = -1
MATCH_NUL = 0

class Tournoi():
    def __init__(self, participants: list, match):
        self.participants = participants# liste des joueurs participants
        self.historique_rencontres = {}
        self.n_rondes = 6 # défini en dure temporairement
        self.resultats = {} # dictionnaire associant à chaque joueur son score actuel
        self.init_results() 
        self.init_historique_rencontres()
        self.match = match  # fonction de simulation de match entre deux joueurs

    def init_historique_rencontres(self):
        for participant in self.participants:
            self.historique_rencontres[participant] = []

    def init_results(self):
        for participant in self.participants:
            self.resultats[participant.nom] = 0                
    
    def resultat_match(self, j1, j2):
        #Calculer la probabilité de victoire de j1 avec la formule Elo 
        diff = j1.elo - j2.elo
        expected_score = 1/(1 + 10**(-diff/400))
        if expected_score > random():
            # mise à jour des cotes Elo des joueurs
            j1.elo += j1.K * (1 - expected_score)
            j2.elo -= j2.K * (1 - expected_score)
            return J1_GAGNE
        else:
            # mise à jour des cotes Elo des joueurs
            j1.elo -= j1.K * expected_score         
            j2.elo += j2.K * expected_score         
            return J2_GAGNE

    ## EN réalité certains matchs peuvent se terminer par une égalité, on en tiendra compte plus tard
    def match_avec_egalite(self,j1,j2): 
        # match qui peut se terminer par une égalité
        diff=j1.elo - j2.elo 
        p=1/(1 + 10**(-diff/400))
        proba_de_victoire=random()
        if abs (p - proba_de_victoire )< 0.01:
            return MATCH_NUL
        elif p > proba_de_victoire:
            return J1_GAGNE
        else:
            return J2_GAGNE

    ## Fonction pour créer les appariements de la ronde
    def créer_apparaiement_ronde(self):
        n_participants = len(self.participants)
        participants_classés = sorted(self.participants, 
                                     key=lambda j: (self.resultats[j.nom], j.elo), 
                                     reverse=True) # on obtiennt directement un classement dans l'ordre décroissant des résultats puis de l'élo initial des joueurs
        appariements = []
        deja_paires = set()
        i = 0
        while i < n_participants:
            j1 = participants_classés[i]

            # Si déjà apparié via un swap précédent, on saute
            if j1 in deja_paires:
                i += 1
                continue

            # Récupère les joueurs encore disponibles après i
            candidats_restants = [
                j for j in participants_classés[i + 1:]
                if j not in deja_paires
            ]

            # Cas où il ne reste personne -> exempt 
            if not candidats_restants:
                # On note un exempt avec None
                appariements.append((j1, None))
                deja_paires.add(j1)
                break

            # On essaie de trouver le meilleur candidat qui n'a pas encore été rencontré
            adversaire = None
            for candidat in candidats_restants:
                if candidat not in self.historique_rencontres[j1]:
                    adversaire = candidat
                    break

            # Si tout le monde a déjà été joué, on prend le premier dispo (autorise re-match)
            if adversaire is None:
                adversaire = candidats_restants[0]

            appariements.append((j1, adversaire))
            deja_paires.add(j1)
            deja_paires.add(adversaire)

            i += 1

        # Mise à jour de l'historique des rencontres
        for j1, j2 in appariements:
            if j2 is not None:
                self.historique_rencontres[j1].append(j2)
                self.historique_rencontres[j2].append(j1)

        return appariements
    
    def jouer_ronde(self, n_ronde, avec_nulles: bool = True):


        appariements = self.créer_apparaiement_ronde()

        for j1, j2 in appariements:
            if j2 is None:
                self.resultats[j1.nom] += 1 # par défaut dans les vrais écheecs on a plus 1 si on est exempt on peut faire varier cette donnée, (au passage je ne sais pas comment est modifié le élo dans ce cas)
                continue

            # Choix de la logique de match
            if avec_nulles:
                resultat = self.match_avec_egalite(j1, j2)
            else:
                resultat = self.resultat_match(j1, j2)

            if resultat == J1_GAGNE:
                self.resultats[j1.nom] += 1
            elif resultat == J2_GAGNE:
                self.resultats[j2.nom] += 1
            elif resultat == MATCH_NUL:
                self.resultats[j1.nom] += 0.5
                self.resultats[j2.nom] += 0.5

