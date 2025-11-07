# Classe tournoi qui gère le déroulement d'un tournoi(système suisse pour l'instant)
from random import random

J1_GAGNE = 1
J2_GAGNE = -1
VICTOIRE = 1
DEFAITE = -1
MATCH_NUL = 0

class Tournoi():
    def __init__(self, participants: list, match):
        self.participants = participants# liste des joueurs participants
        self.historique_rencontres = {}
        self.n_rondes = 6 # défini en dur temporairement
        self.resultats = {} # dictionnaire associant à chaque joueur son score actuel
        self.init_result() 
        self.init_historique_rencontres()

    def init_historique_rencontres(self):
        for participant in self.participants:
            self.historique_rencontres[participant] = []

    def init_results(self):
        for participant in self.participants:
            self.resultats[participant.nom] = 0

    
    def resultat_match(self, j1, j2, update_elo=False):
        #Calculer la probabilité de victoire de j1 avec la formule Elo 
        #TODO le système de gestion de l'historique des rencontres sera généré dans la partie apparaiement
        assert j1 not in self.historique_rencontres[j2]
        self.historique_rencontres[j1].append(j2)
        self.historique_rencontres[j2].append(j1)
        diff = j2.elo - j1.elo
        expected_score = 1/(1 + 10**(-diff/400))
        if expected_score > random():      # match nul non pris en compte pour le calcul de l'ELO car le calcul de la probabilité de match nul en fonction de l'ELO des joueurs est impossible
            if update_elo:
                j1.update_elo(j2.elo, VICTOIRE)
                j2.update_elo(j1.elo, DEFAITE)
            return J1_GAGNE
        else:
            if update_elo:
                j1.update_elo(j2.elo, DEFAITE)
                j2.update_elo(j1.elo, VICTOIRE)
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
                apparaiement.append((participants_classé[i],participants_classé[i+n_participants/2]))
        else:
            #TODO à écrir
            pass

        return apparaiement
