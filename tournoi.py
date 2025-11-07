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
        self.init_result() 

    def init_results(self):
        for participant in self.participants:
            self.resultats[participant.nom] = 0
                
    
    def resultat_match(self, j1, j2):
        #Calculer la probabilité de victoire de j1 avec la formule Elo 
        diff = j2.elo - j1.elo
        expected_score = 1/(1 + 10**(-diff/400))
        if expected_score > random():
            # mise à jour des cotes Elo des joueurs
            j1.elo += j1.K * (1 - expected_score)
            j2.elo -= j2.K * expected_score
            return J1_GAGNE
        else:
            # mise à jour des cotes Elo des joueurs
            j2.elo += j2.K * (1 - expected_score)
            j1.elo -= j1.K * expected_score
            return J2_GAGNE

    ## EN réalité certains matchs peuvent se terminer par une égalité, on en tiendra compte plus tard
    def match_avec_egalite(self,j1,j2): 
        # match qui peut se terminer par une égalité
        diff=j2.elo - j1.elo
        p=1/(1 + 10**(-diff/400))
        proba_de_victoire=random()
        if abs (p - proba_de_victoire )< 0.1:
            return MATCH_NUL
        elif p > proba_de_victoire:
            return J1_GAGNE
        else:
            return J2_GAGNE

    ## Fonction pour créer les appariements de la ronde
    def créer_apparaiement_ronde(self):
        n_participants = len(self.participants)
        participants_classé = sorted(self.participants, 
                                     key=lambda j: (self.résultats[j.nom], j.elo), 
                                     reverse=True) # on obtiennt directement un classement dans l'ordre décroissant des résultats puis de l'élo initial des joueurs
        apparaiement = []
        #TODO on ne peut pas valider l'apparaiement sans avoir vérifier qu'il ne respectait pas toutes les contraintes (ex: joueurs déja rencontrés, exempt, etc)
        if n_participants %2 == 0:
            for i in range (n_participants/2):
                apparaiement.append((participants_classé[i],participants_classé[i+n/2]))
        else:
            #TODO à écrir
            pass

        return apparaiement
    




