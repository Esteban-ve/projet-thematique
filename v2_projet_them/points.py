import numpy as np

class AttributionPoints:
    
    @staticmethod
    def lineaire(classement, max_points=None):
        """
        Répartition Linéaire : Points = Rang
        Le 1er reçoit 1 point, le 2ème reçoit 2 points, etc.
        (Système de pénalité : le plus petit score gagne)
        """
        points_attribues = {}
        for i, joueur in enumerate(classement):
            # i commence à 0, donc rang = i + 1
            pts = i + 1
            points_attribues[joueur] = pts
            
        return points_attribues

    @staticmethod
    def exponentielle(classement, max_points=None):
        """
        Répartition Exponentielle : Points = exp(Rang)
        Les points explosent avec le rang (pénalise très fort les derniers).
        """
        points_attribues = {}
        for i, joueur in enumerate(classement):
            rang = i + 1
            pts = np.exp(rang)
            points_attribues[joueur] = pts
            
        return points_attribues

    @staticmethod
    def logarithmique(classement, max_points=None):
        """
        Répartition Logarithmique : Points = log(Rang)
        Le 1er reçoit log(1) = 0 point.
        La différence de points est forte au début puis diminue.
        """
        points_attribues = {}
        for i, joueur in enumerate(classement):
            rang = i + 1
            pts = np.log(rang)
            points_attribues[joueur] = pts
            
        return points_attribues