from random import random

J1_GAGNE = 1
J2_GAGNE = -1
MATCH_NUL = 0

class Tournoi():
    def __init__(self, participants: list, match):
        self.participants = participants
        self.historique_rencontres = {}
        self.n_rondes = 6 # défini en dure temporairement
        self.resultats = {}
        self.init_result()

    def init_results(self):
        for participant in self.participants:
            self.resultats[participant.nom] = 0
                
    
    def resultat_match(self, j1, j2):
        #TODO le système de gestion de l'historique des rencontres sera généré dans la partie apparaiement
        assert j1 not in self.historique_rencontres[j2]
        try:
            self.historique_rencontres[j1].append(j2)
        except KeyError:
             self.historique_rencontres[j1] = []
             self.historique_rencontres[j1].append(j2)
        try:
            self.historique_rencontres[j2].append(j1)
        except KeyError:
             self.historique_rencontres[j2] = []
             self.historique_rencontres[j2].append(j1)
        diff = j2.elo - j1.elo
        expected_score = 1/(1 + 10**(-diff/400))
        if expected_score > random():
            return J1_GAGNE
        else:
            return J2_GAGNE

    def match_avec_egalite(self,j1,j2):
        diff=j2.elo - j1.elo
        p=1/(1 + 10**(-diff/400))
        proba_de_victoire=random()
        if abs (p - proba_de_victoire )< 0.1:
            return self._MATCH_NUL
        elif p > proba_de_victoire:
            j1.elo += j1.K * (1 - p)
            j2.elo -= j2.K * p
            return J1_GAGNE
        else:
            j2.elo += j2.K * (1- p)
            j1.elo -= j1.K * p
            return J2_GAGNE


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
    




