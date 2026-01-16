# match.py
import random

class Match:
    @staticmethod
    def simuler(j1, j2):
        """
        Simule un match entre j1 et j2 basé sur leur NIVEAU réel.
        Retourne le vainqueur (objet Joueur).
        Utilise une courbe logistique (style Elo) pour la probabilité de victoire.
        """
        # Différence de niveau réel
        diff = j2.niveau - j1.niveau
        
        # Probabilité que J1 gagne : 1 / (1 + 10^(diff/400))
        proba_j1 = 1 / (1 + 10 ** (diff / 400))
        
        # Tirage aléatoire
        if random.random() < proba_j1:
            return j1
        else:
            return j2

    @staticmethod
    def update_elo(gagnant, perdant, k=32):
        """
        Met à jour l'Elo des deux joueurs après un match.
        Ici, le calcul se base sur l'Elo (perception) et non le niveau.
        """
        diff = perdant.elo - gagnant.elo
        attendu_gagnant = 1 / (1 + 10 ** (diff / 400))
        
        # Mise à jour
        gain = k * (1 - attendu_gagnant)
        gagnant.elo += gain
        perdant.elo -= gain