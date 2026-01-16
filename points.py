import numpy as np

class AttributionPoints:

    @staticmethod
    def lineaire(classement):
        points = {}
        max_rang = max(classement.keys())  # nombre de rangs
        for rang, joueurs in classement.items():
            for j in joueurs:
                points[j] = max_rang - rang + 1  # meilleur rang reçoit le plus
        return points

    @staticmethod
    def exponentielle(classement):
        points = {}
        max_rang = max(classement.keys())
        for rang, joueurs in classement.items():
            for j in joueurs:
                points[j] = np.exp(max_rang - rang + 1)
        return points

    @staticmethod
    def logarithmique(classement):
        points = {}
        max_rang = max(classement.keys())
        for rang, joueurs in classement.items():
            for j in joueurs:
                points[j] = np.log(max_rang - rang + 2)  # +2 pour éviter log(0) si 1er rang
        return points
