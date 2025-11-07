VICTOIRE = 1
DEFAITE = -1
MATCH_NUL = 0

class Joueur():
    def __init__(self, nom, niveau, K=32):
        self.nom = nom
        self._niveau = niveau
        self.elo = niveau  # pour l'instant l'elo reflete parfaitement le niveau intrinsèque
        self.K = K  # facteur de correction de l'elo

    def update_elo(self, elo_adversaire, resultat_match):
        expected_score = 1/(1 + 10**(-(elo_adversaire - self.elo)/400))
        if resultat_match == VICTOIRE:
            self.elo = self.elo + self.K * (1 - expected_score)
        elif resultat_match == DEFAITE:
            self.elo = self.elo + self.K * (0 - expected_score)
        elif resultat_match == MATCH_NUL:
            self.elo = self.elo + self.K * (0.5 - expected_score)
