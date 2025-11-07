class Joueur():
    def __init__(self, nom, niveau):
        self.nom = nom
        self._niveau = niveau
        self.elo = niveau  # pour l'instant l'elo reflete parfaitement le niveau intrinsèque
