# joueur.py
import numpy as np

class Joueur:
    def __init__(self, nom, niveau_E, niveau_V, K=40, elo=800):
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
        self.K = K                 # facteur K pour les mises à jour Elo

    @property
    def niveau(self):
        return np.random.normal(self.niveau_E, self.niveau_V)

def joueurs_belloy():
    """Renvoie la liste des joueurs du Grand Prix de la Somme (Belloy)."""
    return [
        Joueur("BONNAY Yanis", 1310),
        Joueur("CAERELS Arsene", 950),
        Joueur("CAERELS Basile", 880),
        Joueur("CAILLY Leo", 1480),
        Joueur("CARDON Julia", 1080),
        Joueur("COURTOIS Regis", 1772),
        Joueur("DEVAL Clement", 1486),
        Joueur("DUMEIGE Lucas", 999),
        Joueur("DUMEIGE Mathieu", 1199),
        Joueur("GAMBIER Thibaut", 1350),
        Joueur("GAUMET Philippe", 1624),
        Joueur("GUINET Auguste", 999),
        Joueur("KOTWICA Arthur", 799),
        Joueur("LANDAZURI Fernando", 1567),
        Joueur("LEBLANC Francois", 1594),
        Joueur("MABILLE Philippe", 1300),
        Joueur("MARINI Jeremy", 1423),
        Joueur("MARINI Manuel", 1820),
        Joueur("MARINI Timothee", 1533),
        Joueur("TERNISIEN Jean-Michel", 1464),
        Joueur("VAST Maxence", 1489),
    ]
