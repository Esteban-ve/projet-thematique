# joueur.py
import numpy as np

class Joueur:
    def __init__(self, nom, niveau_E=0, niveau_V=0, K=40, elo=1500):
        """
        Représente un joueur avec :
        - nom          : str
        - niveau       : "force réelle" (ici on la fait coïncider avec l'Elo initial)
        - K            : facteur K du système Elo
        """
        self.nom = nom
        self.niveau_E = niveau_E    # espérance et variance du niveau intrinsèque (gaussienne)
        self.niveau_V = niveau_V
        self.elo = elo          # Elo courant (évolue pendant le tournoi)
       # Elo courant (évolue pendant le tournoi)
        self.K = K                 # facteur K pour les mises à jour Elo

    @property
    def niveau(self):
        return np.random.normal(self.niveau_E, self.niveau_V)

