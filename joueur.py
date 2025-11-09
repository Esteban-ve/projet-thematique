class Joueur():
    def __init__(self, nom, niveau, K=40):# au échecs, le K est souvent fixé à 40 pour les débutants, il passe à 20 pour les joueurs intermédiaires et à 10 pour les joueurs qui sont déja passé au dessus de 2400 élo
        self.nom = nom
        self._niveau = niveau
        self.elo = niveau  # pour l'instant l'elo reflete parfaitement le niveau intrinsèque
        self.K = K  # facteur de correction de l'elo
