from random import random

J1_GAGNE = 1
J2_GAGNE = -1



class Match:

    def __init__(self,type_match):
        self.type_match=type_match
        self.types={
            "NIVEAU":self.niveau,
            "ELO":self.elo,
            "INTRINSEQUE":self.intrinseque
            }
    
    def niveau(self, j1, j2):
        """
        Simule un match en tirant un vainqueur selon la probabilité calculée par Elo
        (basée ici sur le niveau intrasec des joueurs) et met à jour les Elo.
        """
        diff = j1.niveau_E - j2.niveau_E
        expected_score = 1 / (1 + 10 ** (-diff / 400))   # proba que j1 gagne
        u = random()

        if expected_score > u:
            # Victoire j1
            j1.elo += j1.K * (1 - expected_score)
            j2.elo -= j2.K * (1 - expected_score)
            return J1_GAGNE
        else:
            # Victoire j2
            j1.elo -= j1.K * expected_score
            j2.elo += j2.K * expected_score
            return J2_GAGNE

    def elo(self, j1, j2):
        """
        Simule un match en tirant un vainqueur selon la probabilité calculée par Elo
        et met à jour les Elo des deux joueurs.
        """
        diff = j1.elo - j2.elo
        expected_score = 1 / (1 + 10 ** (-diff / 400))   # proba que j1 gagne
        u = random()

        if expected_score > u:
            # Victoire j1
            j1.elo += j1.K * (1 - expected_score)
            j2.elo -= j2.K * (1 - expected_score)
            return J1_GAGNE
        else:
            # Victoire j2
            j1.elo -= j1.K * expected_score
            j2.elo += j2.K * expected_score
            return J2_GAGNE
        
    def intrinseque(self, j1, j2):
        return J2_GAGNE if j2.niveau>j1.niveau else J1_GAGNE

    def resultat(self, j1, j2):
        """Execute the selected match type and return its result."""
        return self.types[self.type_match](j1, j2)

            