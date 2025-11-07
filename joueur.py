class Joueur():
    def __init__(self, nom, niveau, K=32):
        self.nom = nom
        self._niveau = niveau
        self.elo = niveau  # pour l'instant l'elo reflete parfaitement le niveau intrinsèque
        self.K = K  # facteur de correction de l'elo
